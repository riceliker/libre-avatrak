extends Control

@onready var http = $http
@export var open_button: Button
@export var close_button: Button
var camera_status = false

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	http.request_completed.connect(_on_request_completed)
	open_button.pressed.connect(_on_camera_open)
	close_button.pressed.connect(_on_camera_close)

func _on_camera_open():
	http.request("http://127.0.0.1:8001/camera/open")

func _on_camera_close():
	http.request("http://127.0.0.1:8001/camera/close")

func _on_request_completed(_result, _response_code, _headers, _body):
	pass

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass
