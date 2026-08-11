import cv2
import numpy as np
import mediapipe as mp

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

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

def run_camera():
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
            ear_avg = (ear_l + ear_r)/2
            eye_status = "close" if ear_avg < 0.24 else "open"

            # MAR
            mar_val = mar(all_points[MOUTH])
            mouth_status = "open" if mar_val > 1.33 else "closed"

            # solvePnP
            img_pts = all_points[PnP_IDS]
            cam_matrix = np.array([
                [w, 0, w/2],
                [0, w, h/2],
                [0, 0, 1]
            ], dtype=np.float32)
            dist_coeffs = np.zeros((4,1))
            _, rvec, tvec = cv2.solvePnP(
                obj_pts, img_pts, cam_matrix, dist_coeffs,
                flags=cv2.SOLVEPNP_SQPNP
            )
            pitch, yaw, roll = rvec_to_euler(rvec)

            # draw info text
            texts = [
                f"EAR:{ear_avg:.3f}",
                f"MAR:{mar_val:.3f}",
                f"Pitch:{pitch:.1f} Yaw:{yaw:.1f} Roll:{roll:.1f}"
            ]
            for idx,txt in enumerate(texts):
                cv2.putText(frame, txt, (10, 30 + idx*30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

            # draw points
            for (x,y) in all_points:
                cv2.circle(frame, (int(x), int(y)), 1, (0,255,0), -1)

        cv2.imshow("FaceLandmarker", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    landmarker.close()