import cv2
from threading import Thread


class camera(Thread):
    def __init__(self):
        Thread.__init__(self, name="Camera")
        self.device_adress = 0
        self.running = True
        self.flag = None
        self.frame = None
        self.record = None
        try:
            self.cap = cv2.VideoCapture(self.device_adress)
        except Exception:
            print(Exception)

    def image_encode(self):
        self.cap_framejpeg = cv2.imencode(".JPEG", self.cap_frame)[1]
        return self.cap_framejpeg

    def change_resolution(self, width, height):
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def record_video(self, width, height, flag):
        self.flag = flag
        filename = "file.avi"
        self.record = cv2.VideoWriter(
            filename, cv2.VideoWriter_fourcc(*"XVID"), 25, (width, height)
        )

    def run(self):
        while self.cap.isOpened():
            _, self.cap_frame = self.cap.read()
            if not self.running:
                self.cap.release()
                break
