from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from threading import Event, Thread

import uvicorn
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, StreamingResponse


app = FastAPI()


index1 = open("index.html").read().format(first_header='goodbye')  

#index = "<html><head><title>Video Streaming - Raspberry</title></head><body><h1>VideoTy</h1></body></html>"
#app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")

class Interface:
    def __init__(self):
        self.frame = None
        self.event = Event()

    def start(self):
        @app.get("/", response_class=HTMLResponse)
        def index():
            
            html_content = index
            return HTMLResponse(content=html_content, status_code=200)
            
        @app.get("/items/")
        async def read_items():
            html_content = """
            <html>
                <head>
                    <title>Some HTML in here</title>
                </head>
                <body>
                    <h1>Look ma! HTML!</h1>
                </body>
            </html>
            """
            return HTMLResponse(content=index1, status_code=200)

        #self.thread.start()

if __name__ == "__main__":
    Interface().start()
    uvicorn.run("__main__:app", host="0.0.0.0", port=5000, log_level="info")
