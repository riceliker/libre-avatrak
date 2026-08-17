extends Node

const LISTEN_PORT: int = 8002
var udp: PacketPeerUDP

func _ready():
	udp = PacketPeerUDP.new()
	var err = udp.bind(LISTEN_PORT, "127.0.0.1")
	if err != OK:
		print("UDP监听失败！端口占用？err = ", err)
		return
	print("UDP服务启动，监听端口：", LISTEN_PORT)

func _physics_process(_delta):
	# 循环读取所有收到的数据包
	while udp.get_available_packet_count() > 0:
		var raw_bytes = udp.get_packet()
		var text = raw_bytes.get_string_from_utf8()
		var data = JSON.parse_string(text)
		if data == null:
			print("JSON解析失败：", text)
			continue
		
		var face_data = data["face_data"]
		print("收到人脸：", face_data)

func _exit_tree():
	udp.close()
