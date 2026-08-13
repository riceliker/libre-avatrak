from flask import Blueprint, send_from_directory
import os

bp = Blueprint("Console", __name__)

CONSOLE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../Web/dist")
)

@bp.route("/")
def Console():
    return send_from_directory(CONSOLE_DIR, "index.html")

@bp.route("/<path:filename>")
def godot_static(filename):
    return send_from_directory(CONSOLE_DIR, filename)