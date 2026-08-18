extends Control

var is_hide = true
var camera_status = false

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	position.x = -512




# Called every frame. 'delta' is the elapsed time since the previous frame.
func _physics_process(_delta: float) -> void:
	var mouse_global: Vector2 = get_global_mouse_position()
	if mouse_global.x > 512:
		is_hide = true
	else:
		is_hide = false
		position.x = 0
	if is_hide and position.x > -512:
		position.x -= 8
