extends Node3D

var eye_param: float = 1
var mouse_param: float = 1

const LISTEN_PORT: int = 8002
var udp: PacketPeerUDP

@onready var face = $Char/GeneralSkeleton/Face
@onready var head = $Char/GeneralSkeleton
@onready var head_bone_index = head.find_bone("Neck")


func _ready():
	print(head_bone_index)
	udp = PacketPeerUDP.new()
	var err = udp.bind(LISTEN_PORT, "127.0.0.1")
	if err != OK:
		print("UDP Listener Create Error. ", err)
		return

func make_normal(data: float, bottom: float, top: float) -> float:
	if data > top: 
		data = top
	if data < bottom:
		data = bottom
	var value = (data-bottom) / (top-bottom)
	return value


func _physics_process(_delta):
	while udp.get_available_packet_count() > 0:
		var raw_bytes = udp.get_packet()
		var text = raw_bytes.get_string_from_utf8()
		var data = JSON.parse_string(text)
		if data == null:
			print("Can not get json", text)
			continue
		
		var face_data = data["face_data"]
		face.set_blend_shape_value(15, 1-make_normal(face_data[0], 0.17, 0.21))
		face.set_blend_shape_value(14, 1-make_normal(face_data[1], 0.18, 0.22))
		face.set_blend_shape_value(39, 1-make_normal(face_data[2], 1.0, 1.28))
		
		var v = head.get_bone_pose_position(head_bone_index)
		var dv = Vector3(deg_to_rad(face_data[3] + 135), deg_to_rad(face_data[4] - 7), deg_to_rad(face_data[5] - 2.4))
		var rpy = v - dv
		
		var target_basis = Basis.from_euler(rpy, EulerOrder.EULER_ORDER_YXZ)
		var target_transform = head.get_bone_pose(head_bone_index)
		target_transform.basis = target_basis

		head.set_bone_pose(head_bone_index, target_transform)

		

func _exit_tree():
	udp.close()




func mood_control(mood: String) -> void:
	pass
