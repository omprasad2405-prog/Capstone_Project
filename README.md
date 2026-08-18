**AI-Based Gamified Rehabilitation System**
A computer vision platform designed to monitor physical rehabilitation exercises, evaluate joint Range of Motion (RoM) in real time, and gamify recovery routines using standard webcam hardware.

**Overview**
Traditional physical rehabilitation often suffers from high costs, lack of continuous feedback, and low patient adherence. This system provides an accessible solution using lightweight AI pose tracking to extract 33 skeletal landmarks, calculate biomechanical joint angles dynamically, and validate exercise repetitions via a finite state machine.

**Key Features**
Real-Time Pose Estimation: Tracks full-body skeletal coordinates at 30+ FPS using MediaPipe Tasks Vision API.

Biomechanical Angle Extraction: Trigonometric vector computation to dynamically evaluate interior joint angles (e.g., elbow, shoulder, knee).

State Machine Validation: Enforces strict Range of Motion (RoM) thresholds to prevent incomplete reps and false counting.

On-Screen HUD: Visual feedback displaying real-time joint degree angles, current exercise stage, and completed repetition counts.

**Tech Stack**
Language: Python 3.10+

Computer Vision & ML: OpenCV, MediaPipe (Tasks Vision API)

Mathematical Computation: NumPy
