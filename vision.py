import cv2
import numpy as np
import mediapipe as mp
import time

# Official MediaPipe 1.0+ Tasks Vision API
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# 1. Angle Calculation Math
def calculate_angle(a, b, c):
    """Calculates dynamic 2D interior angle formed by 3 joint landmarks (a-b-c)"""
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360.0 - angle
    return angle

# 2. Configure Pose Landmarker for Live Webcam Video Stream
MODEL_PATH = "pose_landmarker.task"

base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_poses=1,
    min_pose_detection_confidence=0.7,
    min_pose_presence_confidence=0.7,
    min_tracking_confidence=0.7
)

# Standard Pose Connection Lines
POSE_CONNECTIONS = [
    (11, 12), (11, 13), (13, 15), (12, 14), (14, 16), # Arms
    (11, 23), (12, 24), (23, 24),                      # Torso
    (23, 25), (24, 26), (25, 27), (26, 28)            # Legs
]

# 3. Open Webcam Feed
cap = cv2.VideoCapture(0)

with vision.PoseLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # Convert frame format for MediaPipe 1.0 Image Object
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Pass timestamp in milliseconds
        frame_timestamp_ms = int(time.time() * 1000)
        pose_landmarker_result = landmarker.detect_for_video(mp_image, frame_timestamp_ms)

        # Draw Landmarks and Calculate Joint Angles
        if pose_landmarker_result.pose_landmarks:
            for landmarks in pose_landmarker_result.pose_landmarks:
                # Extract Left Arm Coordinates (Index 11: Shoulder, 13: Elbow, 15: Wrist)
                shoulder = [landmarks[11].x * w, landmarks[11].y * h]
                elbow = [landmarks[13].x * w, landmarks[13].y * h]
                wrist = [landmarks[15].x * w, landmarks[15].y * h]

                # Compute Angle
                angle = calculate_angle(shoulder, elbow, wrist)

                # Draw Joint Connections
                for start_idx, end_idx in POSE_CONNECTIONS:
                    pt1 = (int(landmarks[start_idx].x * w), int(landmarks[start_idx].y * h))
                    pt2 = (int(landmarks[end_idx].x * w), int(landmarks[end_idx].y * h))
                    cv2.line(frame, pt1, pt2, (245, 117, 66), 2)

                # Draw Landmark Nodes
                for lm in landmarks:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

                # Display Dynamic Angle Text near the Elbow
                cv2.putText(frame, f"Elbow Angle: {int(angle)} deg", (int(elbow[0]) + 10, int(elbow[1])),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2, cv2.LINE_AA)

        # HUD Top Banner Overlay
        cv2.rectangle(frame, (0, 0), (w, 50), (30, 30, 30), -1)
        cv2.putText(frame, "MODULE 1: AI POSE TRACKING & ANGLE CALCULATION", (15, 33),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow('AI Rehab System - Core Vision Engine (Om Prasad)', frame)

        # Press 'q' to exit
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()