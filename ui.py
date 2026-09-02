import cv2
import numpy as np
from PIL import Image, ImageFont, ImageDraw
import config
import mediapipe as mp

# Inizializziamo il segmentatore di MediaPipe (modello 1 = ottimizzato per la velocità)
mp_selfie_segmentation = mp.solutions.selfie_segmentation
segmenter = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)

# Inizializziamo il Pose Detector per trovare le spalle
mp_pose = mp.solutions.pose
pose_detector = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Caricamento immagine ali
wings_img = cv2.imread(config.WINGS_PATH, cv2.IMREAD_UNCHANGED)

def draw_centered_text(draw, text, font, btn_coords, text_color, shadow_color):
    # funzione per centrare il testo dentro un bottone
    x1, y1, x2, y2 = btn_coords
    btn_w = x2 - x1
    btn_h = y2 - y1
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    text_x = x1 + (btn_w - text_w) // 2
    text_y = y1 + (btn_h - text_h) // 2 - bbox[1] 
    
    draw.text((text_x + 2, text_y + 2), text, font=font, fill=shadow_color)
    draw.text((text_x, text_y), text, font=font, fill=text_color)

def draw_menu_screen(frame):

    # disegna i rettangoli
    cv2.rectangle(frame, (config.BTN_AVVIA[0], config.BTN_AVVIA[1]), (config.BTN_AVVIA[2], config.BTN_AVVIA[3]), config.BG_AVVIA_BGR, -1)
    cv2.rectangle(frame, (config.BTN_AVVIA[0], config.BTN_AVVIA[1]), (config.BTN_AVVIA[2], config.BTN_AVVIA[3]), config.BORDER_PINK_BGR, 4)
    
    cv2.rectangle(frame, (config.BTN_ESCI[0], config.BTN_ESCI[1]), (config.BTN_ESCI[2], config.BTN_ESCI[3]), config.BG_ESCI_BGR, -1)
    cv2.rectangle(frame, (config.BTN_ESCI[0], config.BTN_ESCI[1]), (config.BTN_ESCI[2], config.BTN_ESCI[3]), config.BORDER_PINK_BGR, 4)
    
    # conversione per Pillow
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_im = Image.fromarray(frame_rgb)
    draw = ImageDraw.Draw(pil_im)
    
    try:
        font = ImageFont.truetype(config.FONT_PATH, 40) 
    except IOError:
        font = ImageFont.load_default() 

    # scritte centrate
    draw_centered_text(draw, "Avvia", font, config.BTN_AVVIA, config.TEXT_PINK_RGB, config.SHADOW_RGB)
    draw_centered_text(draw, "Esci", font, config.BTN_ESCI, config.TEXT_PINK_RGB, config.SHADOW_RGB)

    return cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)

def draw_result_screen(frame, final_winx, final_perc):
    """Disegna la schermata con il risultato del calcolo e il bottone indietro."""
    cv2.putText(frame, f"Sei {final_winx}!", (150, 240), cv2.FONT_HERSHEY_DUPLEX, 1.8, (0, 255, 255), 3)
    cv2.putText(frame, f"Affinita': {final_perc:.1f}%", (180, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    
    cv2.rectangle(frame, (config.BTN_CHIUDI[0], config.BTN_CHIUDI[1]), (config.BTN_CHIUDI[2], config.BTN_CHIUDI[3]), (0, 0, 150), -1)
    cv2.putText(frame, "INDIETRO", (510, 55), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
    return frame

# Pre-caricamento delle immagini per ottimizzare i frame
cursor_img = cv2.imread(config.CURSOR_PATH, cv2.IMREAD_UNCHANGED)
sparkle_img = cv2.imread(config.SPARKLE_PATH, cv2.IMREAD_UNCHANGED)

if cursor_img is not None:
    cursor_img = cv2.resize(cursor_img, config.CURSOR_SIZE)
if sparkle_img is not None:
    sparkle_img = cv2.resize(sparkle_img, config.SPARKLE_SIZE)

def overlay_transparent(bg_img, overlay_img, x, y, alpha_mod=1.0):
    """
    Sovrappone un'immagine PNG con trasparenza (BGRA) su uno sfondo (BGR).
    Gestisce i bordi dello schermo e l'opacità globale (alpha_mod per il fading).
    """
    if overlay_img is None: return bg_img
    
    # Centriamo l'immagine sulle coordinate
    h, w, _ = overlay_img.shape
    x = int(x - w / 2)
    y = int(y - h / 2)
    
    # Se l'immagine esce completamente dallo schermo, non fare nulla
    if x >= bg_img.shape[1] or y >= bg_img.shape[0] or x + w <= 0 or y + h <= 0:
        return bg_img
        
    # Calcolo dei limiti per il ritaglio (se parte dell'immagine esce dai bordi)
    x1, x2 = max(x, 0), min(x + w, bg_img.shape[1])
    y1, y2 = max(y, 0), min(y + h, bg_img.shape[0])
    
    ox1, ox2 = max(0, -x), min(w, bg_img.shape[1] - x)
    oy1, oy2 = max(0, -y), min(h, bg_img.shape[0] - y)
    
    # Estrazione del canale alpha (trasparenza) e applicazione del modificatore (fading)
    alpha_channel = (overlay_img[oy1:oy2, ox1:ox2, 3] / 255.0) * alpha_mod
    overlay_colors = overlay_img[oy1:oy2, ox1:ox2, :3]
    
    # Blending vettoriale con NumPy (molto più veloce dei loop for)
    for c in range(3):
        bg_img[y1:y2, x1:x2, c] = (alpha_channel * overlay_colors[:, :, c] + 
                                  (1 - alpha_channel) * bg_img[y1:y2, x1:x2, c])
    return bg_img

def draw_particles(frame, particles):
    """Disegna la scia di scintille in base alla loro vita residua."""
    for p in particles:
        px, py, life = p
        if sparkle_img is not None:
            frame = overlay_transparent(frame, sparkle_img, px, py, alpha_mod=life)
        else:
            # e non trova l'immagine PNG, disegna cerchietti  che rimpiccioliscono
            cv2.circle(frame, (int(px), int(py)), int(5 * life), (255, 200, 255), -1)
    return frame

def draw_cursor(frame, x, y):
    """Disegna il cursore immagine."""
    if cursor_img is not None:
        frame = overlay_transparent(frame, cursor_img, x, y)
    else:
        # Fallback originale se manca l'immagine
        cv2.circle(frame, (x, y), 15, (0, 255, 255), -1)
        cv2.circle(frame, (x, y), 15, (255, 255, 255), 2)
    return frame

def apply_transformation_effect(frame, bg_frame):
    """
    Applica l'effetto trasformazione: isola l'utente, lo tinge di rosa 
    e sostituisce lo sfondo (argomento del corso: maschere binarie e blending NumPy).
    """
    # maschera binaria del corpo
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = segmenter.process(frame_rgb)
    mask = results.segmentation_mask

    # condizione 3D (per i 3 canali BGR) dove la maschera è sicura (> 0.5)
    condition = np.stack((mask,) * 3, axis=-1) > 0.5

    # effetto "Tinta Rosa"
    pink_overlay = np.full(frame.shape, config.TINT_COLOR_BGR, dtype=np.uint8)
    tinted_user = cv2.addWeighted(frame, 0.6, pink_overlay, 0.4, 0)

    # gestione dello sfondo (se il video manca, usiamo uno sfondo nero)
    if bg_frame is None:
        bg_frame = np.zeros(frame.shape, dtype=np.uint8)
    else:
        # assicura che il video sia grande quanto la webcam
        bg_frame = cv2.resize(bg_frame, (frame.shape[1], frame.shape[0]))

    # se "condition" è vera, mette l'utente rosa, altrimenti mette lo sfondo
    output_image = np.where(condition, tinted_user, bg_frame)
    
    return output_image

IMAGE_CACHE = {}

def draw_winx_images (frame, winx_name):

    # controlla se l'immagine è stata caricata in cache
    if winx_name not in IMAGE_CACHE:
        img_path = config.WINX_IMAGES.get(winx_name)
        if not img_path:
            return frame
            
        img_winx = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        if img_winx is None:
            print("Errore immagine")
            return frame

        # ridimensionamento immagine
        h, w = img_winx.shape[:2]
        new_w = 200
        new_h = int((new_w / w) * h)
        img_winx = cv2.resize(img_winx, (new_w, new_h))

        # maschera alpha
        if img_winx.shape[2] == 4:
            alpha_img = img_winx[:, :, 3] / 255.0
            alpha_frame = 1.0 - alpha_img
            bgr_img = img_winx[:, :, :3]
            # salva l'immagine bgr, le maschere, le dimensioni e una flag per la trasparenza
            IMAGE_CACHE[winx_name] = (bgr_img, alpha_img, alpha_frame, new_w, new_h, True)
        else:
            IMAGE_CACHE[winx_name] = (img_winx, None, None, new_w, new_h, False)

    # recupero dati dalla cache
    bgr_img, alpha_img, alpha_frame, new_w, new_h, is_transparent = IMAGE_CACHE[winx_name]

    # stampa
    frame_h, frame_w = frame.shape[:2]
    x_offset = frame_w - new_w - 20
    y_offset = frame_h - new_h - 20
    
    if is_transparent:
        roi = frame[y_offset:y_offset+new_h, x_offset:x_offset+new_w]
        for c in range(0, 3):
            roi[:, :, c] = (alpha_img * bgr_img[:, :, c] + alpha_frame * roi[:, :, c])
        frame[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = roi
    else:
        frame[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = bgr_img

    return frame

def draw_ranking_screen(frame, all_results):
    """Disegna il grafico a barre con le percentuali di tutte le Winx e le sub-statistiche."""
    overlay = frame.copy()
    # Riquadro nero semi-trasparente per migliorare la leggibilità
    cv2.rectangle(overlay, (20, 50), (620, 390), (0, 0, 0), -1)
    frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)

    cv2.putText(frame, "CLASSIFICA AFFINITA'", (120, 90), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2)

    y_offset = 115
    # Estraiamo anche la variabile 'details' (il nostro dizionario)
    for winx_name, perc, details in all_results:
        color = config.WINX_COLORS_BGR.get(winx_name, (255, 100, 255))
        
        # Testo del nome e percentuale (ridotto un po' il font)
        cv2.putText(frame, f"{winx_name} {perc:.1f}%", (30, y_offset + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Barra orizzontale (altezza compattata a 20 pixel invece di 30)
        bar_width = int((perc / 100.0) * 300)
        cv2.rectangle(frame, (210, y_offset), (210 + bar_width, y_offset + 20), color, -1)
        cv2.rectangle(frame, (210, y_offset), (510, y_offset + 20), (255, 255, 255), 2) # Contorno
        
        # Testo percentuali singole sotto la barra
        details_text = f"Occhi: {details['eyes']:.0f}% | Capelli: {details['hair']:.0f}% | Pelle: {details['skin']:.0f}%"
        cv2.putText(frame, details_text, (210, y_offset + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 255, 200), 1)
        
        # Spazio per la prossima Winx (45 pixel)
        y_offset += 45

    # Disegna Bottone "PROSEGUI"
    cv2.rectangle(frame, (config.BTN_PROSEGUI[0], config.BTN_PROSEGUI[1]), (config.BTN_PROSEGUI[2], config.BTN_PROSEGUI[3]), (0, 200, 0), -1)
    cv2.putText(frame, "PROSEGUI", (config.BTN_PROSEGUI[0] + 15, config.BTN_PROSEGUI[1] + 40), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)
    
    return frame

def apply_wings_effect(frame):
    # mette le ali dietro la schiena usando Pose Landmark e Selfie Segmentation
    if wings_img is None: return frame
    
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # trova le spalle per posizionare le ali
    pose_results = pose_detector.process(frame_rgb)
    
    frame_with_wings = frame.copy()
    
    if pose_results.pose_landmarks:
        landmarks = pose_results.pose_landmarks.landmark
        h, w, _ = frame.shape
        
        # spalla sinistra e destra
        l_sh = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        r_sh = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        
        # calcola il centro del torace e la larghezza tra le spalle
        center_x = int((l_sh.x + r_sh.x) * w / 2)
        center_y = int((l_sh.y + r_sh.y) * h / 2)
        shoulder_width = abs(l_sh.x - r_sh.x) * w
        
        # ridimensiona le ali in base alla larghezza delle spalle
        wings_w = int(max(shoulder_width * 2.5, 100))
        wings_h = int(wings_w * (wings_img.shape[0] / wings_img.shape[1])) # Mantieni le proporzioni
        
        resized_wings = cv2.resize(wings_img, (wings_w, wings_h))
        
        # Disegniamo le ali sul frame "di sfondo" (leggermente spostate in basso rispetto alle spalle)
        # Spostamento verso l'alto (sottraendo offset da center_y) per allineare l'attaccatura al collo
        neck_offset = int(wings_h * 0.18)
        frame_with_wings = overlay_transparent(frame_with_wings, resized_wings, center_x, center_y - neck_offset)
        
    # 2. Isoliamo il corpo (Maschera Binaria)
    seg_results = segmenter.process(frame_rgb)
    mask = seg_results.segmentation_mask
    condition = np.stack((mask,) * 3, axis=-1) > 0.5
    
    # 3. MAGIA: Se il pixel appartiene al corpo, usiamo il frame ORIGINALE (senza ali).
    # Se appartiene allo sfondo, usiamo il frame CON LE ALI. 
    # Questo porta le ali "dietro" alla schiena!
    final_frame = np.where(condition, frame, frame_with_wings)
    
    # Bottone MENU
    cv2.rectangle(final_frame, (config.BTN_MENU[0], config.BTN_MENU[1]), (config.BTN_MENU[2], config.BTN_MENU[3]), (0, 0, 150), -1)
    cv2.putText(final_frame, "MENU", (config.BTN_MENU[0] + 15, config.BTN_MENU[1] + 40), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)
    
    return final_frame