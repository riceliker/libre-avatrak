# Library
import queue

from flask import Flask
from threading import Thread
from multiprocessing import Process
from multiprocessing import Queue as PQueue

from controller.camera import camera_command_queue, face_queue
from cv.camera import run_camera

# Application
app = Flask(__name__)

@app.after_request
def add_security_headers(resp):
    resp.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    resp.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    return resp


from controller.camera import bp as camera_bp
app.register_blueprint(camera_bp, url_prefix="/camera")


camera_process: Process | None = None

def run_event():
    while True:
        # Camera control
        try:
            camera_command = camera_command_queue.get(block=False)
            if camera_command == "open":
                camera_process = Process(target=run_camera, args=(face_queue,))
                camera_process.start()
            if camera_command == "close":
                camera_process.terminate()
                camera_process.join()
        except queue.Empty:
            pass

if __name__ == '__main__':
    event_process = Thread(target=run_event)
    event_process.start()
    app.run(host="127.0.0.1", port=8001, debug=False, use_reloader=False)
    