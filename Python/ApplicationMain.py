# Library
import queue

from flask import Flask
from threading import Thread
from multiprocessing import Process, Value
from multiprocessing import Queue as PQueue

from Controller.Camera import camera_command_queue, face_queue
from OpenCV.Camera import run_camera

# Application
app = Flask(__name__)

@app.after_request
def add_security_headers(resp):
    resp.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    resp.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    return resp

# Config
from Config import get_port

from Controller.Camera import bp as camera_bp
app.register_blueprint(camera_bp, url_prefix="/camera")

from Controller.Scene import bp as scene_bp
app.register_blueprint(scene_bp, url_prefix="/scene")

from Controller.Console import bp as console_bp
app.register_blueprint(console_bp, url_prefix="/")

# OpenCV

# Service

# DataBase

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
    app.run(host="127.0.0.1", port=get_port(), debug=False, use_reloader=False)
    