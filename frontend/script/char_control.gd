extends Node3D

const LISTEN_PORT: int = 8002
var udp: PacketPeerUDP

@onready var timer = $Timer

@export var chars: Array = []
@export var char_index = 0
@onready var face
@onready var bone


func _ready():
	var the_scene = chars[char_index]
	var char_instance = load(the_scene).instantiate() as Node3D
	add_child(char_instance)
	face = char_instance.get_node("GeneralSkeleton/Face")
	bone = char_instance.get_node("GeneralSkeleton")
	

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

var tick_time = 0
var move_time = 0
var is_jump = true
var is_front = true

func _physics_process(_delta):
	while udp.get_available_packet_count() > 0:
		var raw_bytes = udp.get_packet()
		var text = raw_bytes.get_string_from_utf8()
		var data = JSON.parse_string(text)
		if data == null:
			print("Can not get json", text)
			continue
		
		var face_data = data["face_data"]
		face.set_blend_shape_value(15, 1-make_normal(face_data[0], 0.18, 0.22))
		face.set_blend_shape_value(14, 1-make_normal(face_data[1], 0.18, 0.22))
		face.set_blend_shape_value(39, 1-make_normal(face_data[2], 1.0, 1.28))
		
		var head_bone_index = bone.find_bone("Neck")
		var v = bone.get_bone_pose_position(head_bone_index)
		var dv = Vector3(deg_to_rad(face_data[3] + 140), deg_to_rad(face_data[4] - 7), deg_to_rad(face_data[5] - 2.4))
		var rpy = v - dv

		var target_basis = Basis.from_euler(rpy, EulerOrder.EULER_ORDER_YXZ)
		var target_transform = bone.get_bone_pose(head_bone_index)
		target_transform.basis = target_basis

		bone.set_bone_pose(head_bone_index, target_transform)

		if tick_time > 128:
			is_jump = true
		else:
			is_jump = false
		if is_jump:
			if is_front:
				move_time += 1
				if move_time == 4:
					is_front = not is_front
			else:
				move_time -= 1
				if move_time == 0:
					is_front = not is_front
					move_time = 0
					tick_time = 0
					is_jump = false
			var cat_ear_l = bone.get_bone_pose(bone.find_bone("J_Opt_L_CatEar2_01"))
			#var cat_ear_r = bone.get_bone_pose(bone.find_bone("J_Opt_R_CatEar2_01"))
			var tpy = Vector3(deg_to_rad(0.0), deg_to_rad(0.0), deg_to_rad(4*move_time))
			cat_ear_l.basis = Basis.from_euler(tpy, EulerOrder.EULER_ORDER_XYZ)
			bone.set_bone_pose(bone.find_bone("J_Opt_L_CatEar2_01"), cat_ear_l)
		tick_time += 1
		


	

func _exit_tree():
	udp.close()
