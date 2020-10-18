import io
import time
import datetime as dt
from threading import Event, Thread
from pathlib import Path
import uvicorn

from src import cameraFunctions

from fastapi import FastAPI, Response, WebSocket, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.testclient import TestClient
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.websockets import WebSocket, WebSocketDisconnect

import RPi.GPIO as GPIO


app = FastAPI()


app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/static/")

servoPIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)
pwm = GPIO.PWM(servoPIN, 50)


def calcAngle(data):
    x = int(data)
    print(x)
    return (x - 1) * (20 - 1) / (20 - 1) + 1


def SetAngle(angle):
    print(angle)
    duty = angle / 18 + 2
    print(duty)
    GPIO.output(servoPIN, True)
    pwm.start(duty) 
    pwm.ChangeDutyCycle(duty) 
    time.sleep(1)
    pwm.stop()
    #GPIO.cleanup()

##### Main interface class
class Interface:
    def __init__(self, camera):
        self.camera = camera
        

    # CAMERA FUNCTIONS
    def gen_camera(self):
        """Generate the video"""
        while True:
            frame = self.camera.image_encode()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame.tobytes() + b"\r\n"
            )

    # ROUTES
    def start(self):
        @app.get("/", response_class=HTMLResponse)
        def index(request: Request):
            return templates.TemplateResponse(
                "videoControl.html",
                {"request": request}
            )

       
        @app.get("/video_viewer")
        def video_viewer():
            return StreamingResponse(
                self.gen_camera(),
                media_type="multipart/x-mixed-replace; boundary=frame",
            )

        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await manager.connect(websocket)

            try:
                while True:
                    data = await websocket.receive_text()
                    SetAngle(calcAngle(data))

            except WebSocketDisconnect:
                manager.disconnect(websocket)


# WEBSOCKET MANAGER - Accept new connection and disconnect
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)


manager = ConnectionManager()

# Start server
if __name__ == "__main__":
    Camera = cameraFunctions.camera()
    Camera.daemon = True
    Camera.start()
    Interface(Camera).start()
    uvicorn.run("__main__:app", host="0.0.0.0", port=8000, log_level="info")
