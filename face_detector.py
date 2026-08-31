import cv2
import mediapipe as mp
import numpy as np

class FaceLandmarksDetector:
    def __init__(self, max_num_faces=1, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=max_num_faces,
            refine_landmarks=True,  # Include i punti fini delle iridi
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

        # Indici dei landmark MediaPipe
        # Iridi (grazie a refine_landmarks=True)
        self.LEFT_IRIS = [474, 475, 476, 477]
        self.RIGHT_IRIS = [469, 470, 471, 472]
        
        # Guance / Pelle (zone stabili senza barba/trucco eccessivo)
        self.CHEEKS_SKIN = [117, 118, 101, 205, 346, 347, 330, 425]
        
        # Fronte / Attaccatura capelli (zona superiore)
        self.FOREHEAD_HAIR = [10, 109, 67, 103, 54, 21, 162, 127]

    def extract_regions(self, frame):
        h, w, _ = frame.shape
        # MediaPipe richiede immagini RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        if not results.multi_face_landmarks:
            return None

        landmarks = results.multi_face_landmarks[0].landmark

        def get_coords(indices):
            return np.array([(int(landmarks[idx].x * w), int(landmarks[idx].y * h)) for idx in indices])

        coords = {
            "left_iris": get_coords(self.LEFT_IRIS),
            "right_iris": get_coords(self.RIGHT_IRIS),
            "skin": get_coords(self.CHEEKS_SKIN),
            "hair_zone": get_coords(self.FOREHEAD_HAIR)
        }
        return coords