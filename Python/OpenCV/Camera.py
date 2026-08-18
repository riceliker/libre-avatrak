import cv2
import numpy as np
import mediapipe as mp
from multiprocessing import Queue
import time
import socket
import json

class FPSCounter:
    def __init__(self, smooth=10):
        self.smooth = smooth
        self.times = []
        self.last_time = time.perf_counter()

    def tick(self):
        now = time.perf_counter()
        dt = now - self.last_time
        self.last_time = now

        self.times.append(dt)
        if len(self.times) > self.smooth:
            self.times.pop(0)
        avg_dt = sum(self.times) / len(self.times)
        return 1.0 / avg_dt if avg_dt > 0 else 0

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

fps_counter = FPSCounter(smooth=15)

# face index
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
LEFT_EYE  = [33, 160, 158, 133, 153, 144]
MOUTH     = [61, 146, 91, 181, 84, 17]
PnP_IDS   = [4, 33, 263, 61, 291]

# 3D face template
obj_pts = np.array([
    [0.0, 0.0, 0.0],
    [-225, 425, 275],
    [225, 425, 275],
    [-150, -150, 225],
    [150, -150, 225]
], dtype=np.float32)

def ear(pts):
    p0,p1,p2,p3,p4,p5 = pts
    A = np.linalg.norm(p1-p5)
    B = np.linalg.norm(p2-p4)
    C = np.linalg.norm(p0-p3)
    return (A+B)/(2.0*C) if C>1e-4 else 0.0

def mar(pts):
    p0,p1,p2,p3,p4,p5 = pts
    A = np.linalg.norm(p1-p4)
    B = np.linalg.norm(p2-p5)
    C = np.linalg.norm(p0-p3)
    return (A+B)/(2.0*C) if C>1e-4 else 0.0

def rvec_to_euler(rvec):
    R,_ = cv2.Rodrigues(rvec)
    sy = np.sqrt(R[0,0]**2 + R[1,0]**2)
    singular = sy < 1e-6
    if not singular:
        pitch = np.arctan2(R[2,1], R[2,2])
        yaw   = np.arctan2(-R[2,0], sy)
        roll  = np.arctan2(R[1,0], R[0,0])
    else:
        pitch = np.arctan2(-R[1,2], R[1,1])
        yaw = 0
        roll = np.arctan2(R[1,0], R[0,0])
    return np.rad2deg([pitch, yaw, roll])


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def run_camera(face_queue: Queue):
    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path="./face_landmarker.task"),
        running_mode=VisionRunningMode.VIDEO,
        num_faces=1,
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False
    )
    landmarker = FaceLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(0)
    timestamp_ms = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        h, w = frame.shape[:2]
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)

        detection_result = landmarker.detect_for_video(mp_image, timestamp_ms)
        timestamp_ms += 33

        if detection_result.face_landmarks:
            face_lm = detection_result.face_landmarks[0]
            pts_list = []
            for lm in face_lm:
                px = lm.x * w
                py = lm.y * h
                pts_list.append([px, py])
            all_points = np.array(pts_list, dtype=np.float32)

            # EAR
            ear_l = ear(all_points[LEFT_EYE])
            ear_r = ear(all_points[RIGHT_EYE])
        
            eye_l = round(float(ear_l), 3)
            eye_r = round(float(ear_r), 3)

            # MAR
            mar_val = mar(all_points[MOUTH])
            mouse = round(float(mar_val), 3)

            # solvePnP
            img_pts = all_points[PnP_IDS]
            cam_matrix = np.array([
                [w, 0, w/2],
                [0, w, h/2],
                [0, 0, 1]
            ], dtype=np.float32)
            _, rvec, _ = cv2.solvePnP(
                obj_pts, img_pts, cam_matrix, 
                np.zeros((4,1)),flags=cv2.SOLVEPNP_SQPNP
            )
            pitch, yaw, roll = rvec_to_euler(rvec)
            pitch = round(float(pitch), 1)
            yaw = round(float(yaw), 1)
            roll = round(float(roll), 1)
            fps = fps_counter.tick()

            # draw info text
            texts = [
                f"Eye: L{eye_l} R:{eye_r} Mouse:{mouse}",
                f"Pitch:{pitch} Yaw:{yaw} Roll:{roll}",
                f"FPS: {fps:.1f}"
            ]
            for idx,txt in enumerate(texts):
                cv2.putText(
                    frame, txt, (10, 30 + idx*30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0,255,0), 2
                )

            # draw points
            for (x,y) in all_points:
                cv2.circle(frame, (int(x), int(y)), 1, (0,255,0), -1)

            # send data
            try:
                face_queue.put((eye_l, eye_r, mouse, pitch, yaw, roll), block=False)
            except:
                pass
            payload = json.dumps({"face_data": (eye_l, eye_r, mouse, pitch, yaw, roll)})
            sock.sendto(payload.encode("utf-8"), ("127.0.0.1", 8002))

        cv2.imshow("LibreAvatrak", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    landmarker.close()