import cv2
import numpy as np
import mediapipe as mp
from color_analyzer import get_dominant_color

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

BUFFER_SIZE = 15
color_buffers = {
    "eyes": [],
    "skin": [],
    "hair": []
}

def get_stable_color(feature_name, raw_color):
    # calcola la media degli ultimi colori letti per stabilizzare il risultato usando una lista
    if raw_color == (0, 0, 0):
        return raw_color
    
    color_buffers[feature_name].append(raw_color) # aggiunge il nuovo colore alla lista
    
    # se len > 15, cancella il primo
    if len(color_buffers[feature_name]) > BUFFER_SIZE:
        color_buffers[feature_name].pop(0)
    
    # calcola la media
    avg_r = int(np.mean([c[0] for c in color_buffers[feature_name]]))
    avg_g = int(np.mean([c[1] for c in color_buffers[feature_name]]))
    avg_b = int(np.mean([c[2] for c in color_buffers[feature_name]]))
    
    return (avg_r, avg_g, avg_b)

def process_frame(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # mano
    hand_results = hands.process(rgb_frame)
    finger_pos = None
    if hand_results.multi_hand_landmarks:
        h, w, _ = frame.shape
        hx = int(hand_results.multi_hand_landmarks[0].landmark[8].x * w)
        hy = int(hand_results.multi_hand_landmarks[0].landmark[8].y * h)
        finger_pos = (hx, hy)
    
    # volto
    face_results = face_mesh.process(rgb_frame)
    colors = None
    
    if face_results.multi_face_landmarks:
        landmarks = face_results.multi_face_landmarks[0].landmark
        h, w, _ = frame.shape
        
        def get_pt(idx):
            return (int(landmarks[idx].x * w), int(landmarks[idx].y * h))

        # occhi
        eye_pts = np.array([get_pt(33), get_pt(160), get_pt(158), get_pt(133), get_pt(153), get_pt(144)], np.int32)
        eye_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillConvexPoly(eye_mask, eye_pts, 255)
        eye_color = get_dominant_color(frame, mask=eye_mask)

        # guancia per la pelle
        cx, cy = get_pt(50)
        skin_y1, skin_y2 = max(0, cy-15), min(h, cy+15)
        skin_x1, skin_x2 = max(0, cx-15), min(w, cx+15)
        skin_crop = frame[skin_y1:skin_y2, skin_x1:skin_x2]
        skin_color = get_dominant_color(skin_crop) if skin_crop.size > 0 else (0,0,0)

        # capelli
        fx, fy = get_pt(10)
        hair_y1, hair_y2 = max(0, fy - 75), max(0, fy - 45) # rettangolo sopra la fronte per i capelli
        hair_x1, hair_x2 = max(0, fx - 20), min(w, fx + 20)
        hair_crop = frame[hair_y1:hair_y2, hair_x1:hair_x2]
        hair_color = get_dominant_color(hair_crop) if hair_crop.size > 0 else (0,0,0)

        cv2.polylines(frame, [eye_pts], isClosed=True, color=(0, 255, 0), thickness=1) # verde: occhio
        cv2.rectangle(frame, (skin_x1, skin_y1), (skin_x2, skin_y2), (0, 0, 255), 1)   # rosso: pelle
        cv2.rectangle(frame, (hair_x1, hair_y1), (hair_x2, hair_y2), (255, 0, 0), 1)   # blu: capelli

        colors = {
            "eyes": get_stable_color("eyes", eye_color),
            "hair": get_stable_color("hair", hair_color),
            "skin": get_stable_color("skin", skin_color)
        }
        
    return finger_pos, colors