extends Node3D

var eye_param: float = 1
var mouse_param: float = 1

const LISTEN_PORT: int = 8002
var udp: PacketPeerUDP

var face



func _ready():
	face = $Char/GeneralSkeleton/Face
	
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
		print("收到人脸：", face_data)
		face.set_blend_shape_value(15, 1-make_normal(face_data[0], 0.16, 0.22))
		face.set_blend_shape_value(14, 1-make_normal(face_data[1], 0.16, 0.22))

func _exit_tree():
	udp.close()




func mood_control(mood: String) -> void:
	pass
