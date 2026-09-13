# 🧚‍♀️ Magic Winx: Computer Vision

An interactive real-time computer vision application built in Python that analyzes facial features (eye color, hair color, and skin tone), matches them against Winx character color profiles, and applies video transformation effects and AR fairy wings using touchless hand tracking and offline voice recognition.



## Key Features

* **Offline Voice Activation**: Hands-free trigger powered by the Vosk speech recognition engine listening for magic keywords ("Magic", "Winx", "Vision")
* **Facial & Feature Color Analysis**: Uses MediaPipe Face Mesh to extract eye, skin, and hair regions, running HSV-space calculations and temporal smoothing buffers for color detection
* **Touchless Gesture Navigation**: Tracks index finger position with MediaPipe Hands to interact with UI buttons and render particle-trail effects
* **Pose-Aware AR Wings Filter**: Leverages MediaPipe Pose to anchor dynamic fairy wings to shoulder landmarks and Selfie Segmentation to layer the user's body correctly over the AR elements
* **Dynamic Video Transformation**: Blends webcam feeds with custom background transformation videos, custom font overlays, and multi-channel audio effects using OpenCV and Pygame
* **Performance Caching**: Employs RAM caching for UI overlays and downscaled segmentation passes to maintain a high framerate




## Tech Stack

| Category | Technologies |
| :--- | :--- |
| **Language** | Python 3.9+ |
| **Computer Vision & AR** | OpenCV, MediaPipe (Face Mesh, Hands, Pose, Selfie Segmentation) |
| **Speech & Audio** | Vosk (Offline Speech-to-Text), PyAudio, Pygame (Mixer) |
| **Graphics & Processing** | Pillow (PIL), NumPy, Colorsys |





## Getting Started

#### Prerequisites
- Python 3.10 or 3.11
- Webcam and microphone
- System audio dependencies

## Installation
Clone the repository:
``` bash
git clone https://github.com/rosetoy66/Magic-Winx-COMPUTER-VISION.git
```

Install required Python dependencies (MediaPipe version 0.10.14 is required):
```bash
pip install opencv-python mediapipe==0.10.14 pygame numpy vosk pyaudio pillow
```

## Run the application
```bash
python main.py
```





## Control and Interaction

| **Control Input** | **Action** |
| :--- | :--- |
| **Voice Command** | Speak words like "Magic", "Winx", or "Vision" into the microphone |
| **Index Finger Hover** | Touchless interaction with UI buttons and particle generation |
| `T` **Key** | Manually trigger voice activation override |
| `Q` **Key** | Exit the application |



















