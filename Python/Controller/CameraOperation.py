"""
This file will open the camera from web http request.
It has two operation: create new camera or close camera.
Use https://127.0.0.1:5000/camera/new to create new camera.
Use https://127.0.0.1:5000/camera/close to close camera.
"""

# library
from multiprocessing import Process
from flask import Blueprint
import numpy
# module
from OpenCV.Camera import run_camera

bp = Blueprint("Camera", __name__)
camera_process: Process | None = None
def is_camera_process_running():
    global camera_process
    return camera_process is not None and camera_process.is_alive()

@bp.route("/new")
def new():
    global camera_process
    if is_camera_process_running():
        print("Warning: Camera has been running.")
        return {
            "code" : 429,
            "msg": "Camera has been running."
        }, 429
    
    camera_process = Process(target=run_camera)
    camera_process.start()
    print("Log: Camera will be created.")
    return {
        "code": 200,
        "msg": "Camera will be created."
    }, 200

@bp.route("/close")
def close():
    global camera_process
    if is_camera_process_running():
        camera_process.terminate()
        camera_process.join()
        print("Log: Camera has been closed.")
        return {"code": 200, "msg": "Camera has been closed."}, 200
    print("Warning: Camera not found.")
    return {"code": 400, "msg": "Camera not found."}, 400
    