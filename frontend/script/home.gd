extends Control

@onready var http = $http

@export var sidebar_button: Button
@export var sidebar: Control
@onready var is_show: bool = false

@export var open_button: Button
@export var close_button: Button
var camera_status = false

func _ready() -> void:
	sidebar.visible = is_show
	http.request_completed.connect(_on_request_completed)
	open_button.pressed.connect(_on_camera_open)
	close_button.pressed.connect(_on_camera_close)
	sidebar_button.pressed.connect(_on_sidebar_show)

func _on_sidebar_show():
	is_show = not is_show
	sidebar.visible = is_show

func _on_camera_open():
	http.request("http://127.0.0.1:8001/camera/open")

func _on_camera_close():
	http.request("http://127.0.0.1:8001/camera/close")

func _on_request_completed(_result, _response_code, _headers, _body):
	pass
