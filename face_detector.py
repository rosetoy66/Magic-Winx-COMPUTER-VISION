import cv2
import mediapipe as mp

# Inizializzazione di MediaPipe Face Mesh (per estrarre i colori)
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

# Inizializzazione di MediaPipe Hands (per il cursore del menu)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

def process_frame(frame):
    # Convertiamo in RGB per MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # 1. --- RILEVAMENTO MANO (CURSORE) ---
    hand_results = hands.process(rgb_frame)
    finger_pos = None
    
    if hand_results.multi_hand_landmarks:
        # Prendiamo la prima mano rilevata
        hand_landmarks = hand_results.multi_hand_landmarks[0]
        h, w, _ = frame.shape
        
        # Landmark 8 = Punta del dito indice (INDEX_FINGER_TIP)
        finger_x = int(hand_landmarks.landmark[8].x * w)
        finger_y = int(hand_landmarks.landmark[8].y * h)
        finger_pos = (finger_x, finger_y)
    
    # 2. --- RILEVAMENTO VOLTO (COLORI) ---
    face_results = face_mesh.process(rgb_frame)
    colors = None
    
    if face_results.multi_face_landmarks:
        # MOCKUP: Simuliamo i colori estratti
        colors = {
            "eyes": (255, 0, 0),     # Blu
            "hair": (0, 0, 0),       # Nero
            "skin": (220, 180, 150)  # Rosa/Pelle
        }
        
    return finger_pos, colors