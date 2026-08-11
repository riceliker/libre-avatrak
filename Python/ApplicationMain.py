# Library
from flask import Flask
from multiprocessing import Process, Queue
import os

# Application
app = Flask(__name__)

@app.after_request
def add_security_headers(resp):
    resp.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    resp.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    return resp

# Config
from Config import get_port

# Controller
from Controller.CameraOperation import bp as camera_bp
app.register_blueprint(camera_bp, url_prefix="/camera")

from Controller.Scene import bp as scene_bp
app.register_blueprint(scene_bp, url_prefix="/scene")

# OpenCV

# Service

# DataBase

# MultiProcess

def add_process(func, arg_list):
    p = Process(target=func, args=arg_list)
    p.start()

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=get_port(), debug=False)
    
    