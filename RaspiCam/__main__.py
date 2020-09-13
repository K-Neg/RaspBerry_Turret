import io
import time
from threading import Event, Thread

import picamera
import uvicorn
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, StreamingResponse

app = FastAPI()

class Interface:
    def __init__(self):
        self.frame = None
        self.event = Event()

    def get_frame(self):
        """Return the current frame."""
        # wait for a signal from the thread
        self.event.wait()
        self.event.clear()
        return self.frame

    def frames(self):
        with picamera.PiCamera() as camera:
            # let camera warm up
            time.sleep(2)

            stream = io.BytesIO()
            for _ in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # return current frame
                stream.seek(0)
                yield stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()

    def framemap(self):
        """FrameMap background thread."""
        frames = self.frames()
        for frame in frames:
            self.frame = frame
            self.event.set()  # send signal to client
            time.sleep(0.01)
        self.thread = None

    def gen_camera(self):
        """Generate the video"""
        while True:
            frame = self.get_frame()
            yield (b"--frame\r\n" b"Content-Type: image/PNG\r\n\r\n" + frame + b"\r\n")

    def start(self):
        @app.get("/", response_class=HTMLResponse)
        def index():
            """Route to the main page"""
            return """<html>
                        <head>
                            <title>Video Streaming - Raspberry</title>
                        </head>
                        <body>
                            <h1>Video Streaming - Raspberry</h1>
                            <img src="http://0.0.0.0:5151/video_viewer">
                        </body>
                    </html>"""

        @app.get("/video_viewer")
        def video_viewer():
            """Route to the video"""
            return StreamingResponse(self.gen_camera(), media_type="multipart/x-mixed-replace; boundary=frame")

        self.thread = Thread(target=self.framemap)
        self.thread.start()


if __name__ == "__main__":
    Interface().start()
    uvicorn.run("__main__:app", host="0.0.0.0", port=5151, log_level="info")
