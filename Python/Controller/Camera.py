from flask import Blueprint, Response
from multiprocessing import Queue as PQueue
import queue
import json
import time

bp = Blueprint("Camera", __name__)

face_queue = PQueue(maxsize=1)
face_data = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

camera_command_queue = queue.Queue(maxsize=1)

def sse_generator():
    while True:
        try:
            face_data = face_queue.get(block=False)
            payload = json.dumps({
                "face_data": face_data
            })
            yield f"data: {payload}\n\n"
        except queue.Empty:
            pass
        time.sleep(0.03)

@bp.route("/open")
def new():  
    camera_command_queue.put("open")
    print("Log: Camera will be created.")
    return {
        "code": 200,
        "msg": "Camera will be created."
    }, 200

@bp.route("/close")
def close():
    camera_command_queue.put("close")
    print("Log: Camera has been closed.")
    return {"code": 200, "msg": "Camera has been closed."}, 200


@bp.route("/query")
def query():
    return Response(
        sse_generator(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )