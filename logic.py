import os
import sys
import time
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

MODEL_PATH = "pose_landmarker.task"
if not os.path.exists(MODEL_PATH):
    print(f"\n[ERROR] '{MODEL_PATH}' not found in folder!")
    print("Download it using this command:")
    print('curl.exe -L -o pose_landmarker.task "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task"\n')
    sys.exit(1)

def calculate_angle(a, b, c):
    """Calculates 2D interior angle formed by 3 joint landmarks (a-b-c)"""
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360.0 - angle
    return angle

# Configure MediaPipe Tasks
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_poses=1,
    min_pose_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Upper Body Skeleton Connections
POSE_CONNECTIONS = [
    (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),
    (11, 23), (12, 24), (23, 24)
]

# State Machine Variables
counter = 0
stage = "READY"
target_reps = 10
frame_timestamp_ms = 0

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("[ERROR] Cannot access webcam.")
    sys.exit(1)

print("\n--- Biomechanical State Machine Engine Running (Shashwat) ---")
print("Press 'q' or 'ESC' to exit.\n")

with vision.PoseLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Increment timestamp safely
        frame_timestamp_ms += 33
        pose_result = landmarker.detect_for_video(mp_image, frame_timestamp_ms)

        if pose_result.pose_landmarks:
            for landmarks in pose_result.pose_landmarks:
                # Left Arm: Shoulder (11), Elbow (13), Wrist (15)
                shoulder = [landmarks[11].x * w, landmarks[11].y * h]
                elbow = [landmarks[13].x * w, landmarks[13].y * h]
                wrist = [landmarks[15].x * w, landmarks[15].y * h]

                angle = calculate_angle(shoulder, elbow, wrist)

                # --- FINITE STATE MACHINE LOGIC ---
                if angle > 150:
                    stage = "DOWN"
                
                if angle < 45 and stage == "DOWN":
                    stage = "UP"
                    counter += 1
                    print(f"[REHAB TELEMETRY] Repetition {counter}/{target_reps} Registered!")

                # Draw Upper Body Skeleton Lines
                for p1, p2 in POSE_CONNECTIONS:
                    pt1 = (int(landmarks[p1].x * w), int(landmarks[p1].y * h))
                    pt2 = (int(landmarks[p2].x * w), int(landmarks[p2].y * h))
                    cv2.line(frame, pt1, pt2, (245, 117, 66), 2)

                # Draw Key Landmarks
                for idx in [11, 12, 13, 14, 15, 16]:
                    cv2.circle(frame, (int(landmarks[idx].x * w), int(landmarks[idx].y * h)), 5, (0, 255, 0), -1)

                # Live Angle Text next to Elbow
                cv2.putText(frame, f"{int(angle)} deg", (int(elbow[0]) + 10, int(elbow[1])),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        # --- REHABILITATION HUD ---
        cv2.rectangle(frame, (0, 0), (w, 45), (30, 30, 30), -1)
        cv2.putText(frame, "MODULE 1: REHAB EXERCISE STATE MACHINE & COMPLIANCE", (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.rectangle(frame, (15, h - 105), (280, h - 15), (20, 20, 20), -1)
        cv2.rectangle(frame, (15, h - 105), (280, h - 15), (0, 255, 0), 2)
        cv2.putText(frame, f"STAGE: {stage}", (30, h - 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)
        cv2.putText(frame, f"REPS: {counter} / {target_reps}", (30, h - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

        cv2.imshow('AI Rehab System - State Machine Demo (Shashwat)', frame)

        key = cv2.waitKey(5) & 0xFF
        if key == ord('q') or key == ord('Q') or key == 27:
            break

cap.release()
cv2.destroyAllWindows()