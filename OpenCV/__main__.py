import io
import aiofiles
import time
from threading import Event, Thread

import cv2
import uvicorn
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse

app = FastAPI()

#get local IP
import os
stream = os.popen('hostname -I')
local_ip = stream.read().strip()
port="5151"
webpage_address = local_ip + ":" +port


class Interface:
    def __init__(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    def gen_camera(self):
        """Generate the video"""
        while True:
            _, self.cap_frame = self.cap.read()
            self.cap_framejpeg = cv2.imencode(".JPEG", self.cap_frame)[1]
            frame = self.cap_framejpeg
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame.tobytes() + b"\r\n")

    def start(self):
        @app.get("/", response_class=HTMLResponse)
        async def index():
            index = open("index.html").read().format(first_header=webpage_address+"/video_viewer")  
            return HTMLResponse(content=index, status_code=200)
            

        @app.get("/video_viewer")
        async def video_viewer():
            """Route to the video"""
            return StreamingResponse(self.gen_camera(), media_type="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    Interface().start()
    uvicorn.run("__main__:app", host="0.0.0.0", port=5151, log_level="info")
