import cv2
import numpy as np
from PIL import Image, ImageFont, ImageDraw
import config as config
import mediapipe as mp
import math
import random

# inizializza il segmentatore di MediaPipe
mp_selfie_segmentation = mp.solutions.selfie_segmentation
segmenter = mp_selfie_segmentation.SelfieSegmentation(model_selection=0)

# inizializza il Pose Detector per trovare le spalle
mp_pose = mp.solutions.pose
pose_detector = mp_pose.Pose(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Pre-caricamento immagini cursore e scintille
cursor_img = cv2.imread(config.CURSOR_PATH, cv2.IMREAD_UNCHANGED)
sparkle_img = cv2.imread(config.SPARKLE_PATH, cv2.IMREAD_UNCHANGED)

if cursor_img is not None:
    cursor_img = cv2.resize(cursor_img, config.CURSOR_SIZE)
if sparkle_img is not None:
    sparkle_img = cv2.resize(sparkle_img, config.SPARKLE_SIZE)

# genera le scintille per l'intro una sola volta
intro_sparkles = [
    {"x": random.randint(0, 640), "y": random.randint(0, 480), 
     "speed": random.uniform(1.0, 2.5), "offset": random.uniform(0, 2 * math.pi)} 
    for _ in range(20)
]

def draw_centered_text(draw, text, font, btn_coords, text_color, shadow_color):
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

def overlay_transparent(bg_img, overlay_img, x, y, alpha_mod=1.0):
    if overlay_img is None: return bg_img
    h, w, _ = overlay_img.shape
    x = int(x - w / 2)
    y = int(y - h / 2)
    if x >= bg_img.shape[1] or y >= bg_img.shape[0] or x + w <= 0 or y + h <= 0:
        return bg_img
    x1, x2 = max(x, 0), min(x + w, bg_img.shape[1])
    y1, y2 = max(y, 0), min(y + h, bg_img.shape[0])
    ox1, ox2 = max(0, -x), min(w, bg_img.shape[1] - x)
    oy1, oy2 = max(0, -y), min(h, bg_img.shape[0] - y)
    
    alpha = (overlay_img[oy1:oy2, ox1:ox2, 3:] / 255.0) * alpha_mod
    overlay_rgb = overlay_img[oy1:oy2, ox1:ox2, :3]
    
    bg_img[y1:y2, x1:x2] = (alpha * overlay_rgb + (1.0 - alpha) * bg_img[y1:y2, x1:x2]).astype(np.uint8)
    return bg_img

def draw_intro_screen(frame, state_time, fade_progress):
    if frame is None: return None
    h, w = frame.shape[:2]
    
    overlay = frame.copy()
    lilac_color = (255, 180, 220)  # Lilla BGR
    cv2.rectangle(overlay, (0, 0), (w, h), lilac_color, -1)
    
    for s in intro_sparkles:
        px = s["x"] + math.sin(state_time * s["speed"] + s["offset"]) * 30
        py = s["y"] - (state_time * 40 * s["speed"]) % h 
        if py < 0: py += h 
        
        if sparkle_img is not None:
            overlay = overlay_transparent(overlay, sparkle_img, int(px), int(py))
        else:
            cv2.circle(overlay, (int(px), int(py)), 3, (255, 255, 255), -1)

    pil_im = Image.fromarray(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_im)
    try:
        font = ImageFont.truetype(config.FONT_PATH, 40)
    except IOError:
        font = ImageFont.load_default()

    if state_time < 5.0:
        text = "Hai mai sognato\ndi essere una fata?"
    else:
        text = "Pronuncia le parole\n'Magic Winx Computer Vision!'\ne trasformati!"

    bbox = draw.multiline_textbbox((0, 0), text, font=font, align="center")
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (w - text_w) // 2
    text_y = (h - text_h) // 2

    draw.multiline_text((text_x + 3, text_y + 3), text, font=font, fill=(100, 0, 100), align="center")
    draw.multiline_text((text_x, text_y), text, font=font, fill=(255, 255, 255), align="center")

    overlay_bgr = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)

    if fade_progress > 0:
        alpha = max(0.0, 1.0 - fade_progress)
        return cv2.addWeighted(overlay_bgr, alpha, frame, 1.0 - alpha, 0)
    
    return overlay_bgr

def draw_menu_screen(frame):
    if frame is None: return None
    cv2.rectangle(frame, (config.BTN_AVVIA[0], config.BTN_AVVIA[1]), (config.BTN_AVVIA[2], config.BTN_AVVIA[3]), config.BG_AVVIA_BGR, -1)
    cv2.rectangle(frame, (config.BTN_AVVIA[0], config.BTN_AVVIA[1]), (config.BTN_AVVIA[2], config.BTN_AVVIA[3]), config.BORDER_PINK_BGR, 4)
    cv2.rectangle(frame, (config.BTN_ESCI[0], config.BTN_ESCI[1]), (config.BTN_ESCI[2], config.BTN_ESCI[3]), config.BG_ESCI_BGR, -1)
    cv2.rectangle(frame, (config.BTN_ESCI[0], config.BTN_ESCI[1]), (config.BTN_ESCI[2], config.BTN_ESCI[3]), config.BORDER_PINK_BGR, 4)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_im = Image.fromarray(frame_rgb)
    draw = ImageDraw.Draw(pil_im)
    try:
        font = ImageFont.truetype(config.FONT_PATH, 40) 
    except IOError:
        font = ImageFont.load_default() 
    draw_centered_text(draw, "Avvia", font, config.BTN_AVVIA, config.TEXT_PINK_RGB, config.SHADOW_RGB)
    draw_centered_text(draw, "Esci", font, config.BTN_ESCI, config.TEXT_PINK_RGB, config.SHADOW_RGB)
    return cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)

def draw_result_screen(frame, final_winx, final_perc):
    if frame is None:
        return None

    frame_h, frame_w = frame.shape[:2]

    # converte il frame in formato PIL (RGB)
    pil_im = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_im)
    
    try:
        font_title = ImageFont.truetype(config.FONT_PATH, 50)
        font_sub = ImageFont.truetype(config.FONT_PATH, 25)
    except IOError:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # recupera il colore BGR e converte in RGB per PIL
    bgr_color = config.WINX_COLORS_BGR.get(final_winx, (0, 255, 255))
    rgb_color = (bgr_color[2], bgr_color[1], bgr_color[0])

    # Testo "Sei..."
    title_text = f"Sei {final_winx}!"
    bbox_title = draw.textbbox((0, 0), title_text, font=font_title)
    title_w = bbox_title[2] - bbox_title[0]
    title_x = (frame_w - title_w) // 2
    title_y = 200

    draw.text((title_x + 2, title_y + 2), title_text, font=font_title, fill=(50, 0, 50)) # ombra
    draw.text((title_x, title_y), title_text, font=font_title, fill=rgb_color) # testo winx

    # testo "affinita'..."
    perc_text = f"Affinita': {final_perc:.1f}%"
    bbox_perc = draw.textbbox((0, 0), perc_text, font=font_sub)
    perc_w = bbox_perc[2] - bbox_perc[0]
    perc_x = (frame_w - perc_w) // 2
    perc_y = 265

    draw.text((perc_x + 2, perc_y + 2), perc_text, font=font_sub, fill=(0, 0, 0)) # ombra
    draw.text((perc_x, perc_y), perc_text, font=font_sub, fill=(255, 255, 255)) # testo Bianco

    # riconverte il frame in OpenCV (BGR)
    frame = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)
    
    return frame

def draw_stats_button(frame):
    if frame is None:
        return None

    x1, y1, x2, y2 = config.BTN_STATISTICHE

    pil_im = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_im)

    try:
        font_btn = ImageFont.truetype(config.FONT_PATH, 30)
    except IOError:
        font_btn = ImageFont.load_default()

    shadow_offset = 3
    corner_radius = 30

    # ombra nera dello sfondo e del bordo del pulsante
    draw.rounded_rectangle(
        [x1 + shadow_offset, y1 + shadow_offset, x2 + shadow_offset, y2 + shadow_offset],
        radius=corner_radius,
        fill=config.BTN_STATS_SHADOW_RGB,
        outline=config.BTN_STATS_SHADOW_RGB,
        width=3
    )

    # bottone statistiche
    draw.rounded_rectangle(
        [x1, y1, x2, y2],
        radius=corner_radius,
        fill=config.BTN_STATS_BG_RGB,
        outline=config.BTN_STATS_PINK_RGB,
        width=3
    )

    text = "Statistiche"
    bbox = draw.textbbox((0, 0), text, font=font_btn)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    text_x = x1 + ((x2 - x1) - text_w) // 2
    text_y = y1 + ((y2 - y1) - text_h) // 2 - bbox[1]

    # ombra nera del testo
    draw.text((text_x + 2, text_y + 2), text, font=font_btn, fill=config.BTN_STATS_SHADOW_RGB)
    draw.text((text_x, text_y), text, font=font_btn, fill=config.BTN_STATS_PINK_RGB)

    return cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)

def draw_avanti_button(frame):
    if frame is None:
        return None

    x1, y1, x2, y2 = config.BTN_AVANTI

    pil_im = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_im)

    try:
        font_btn = ImageFont.truetype(config.FONT_PATH, 30)
    except IOError:
        font_btn = ImageFont.load_default()

    shadow_offset = 3
    corner_radius = 30

    # ombra nera dello sfondo e del bordo del pulsante
    draw.rounded_rectangle(
        [x1 + shadow_offset, y1 + shadow_offset, x2 + shadow_offset, y2 + shadow_offset],
        radius=corner_radius,
        fill=config.BTN_STATS_SHADOW_RGB,
        outline=config.BTN_STATS_SHADOW_RGB,
        width=3
    )

    # bottone statistiche
    draw.rounded_rectangle(
        [x1, y1, x2, y2],
        radius=corner_radius,
        fill=config.BTN_STATS_BG_RGB,
        outline=config.BTN_STATS_PINK_RGB,
        width=3
    )

    text = "Avanti"
    bbox = draw.textbbox((0, 0), text, font=font_btn)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    text_x = x1 + ((x2 - x1) - text_w) // 2
    text_y = y1 + ((y2 - y1) - text_h) // 2 - bbox[1]

    # ombra nera del testo
    draw.text((text_x + 2, text_y + 2), text, font=font_btn, fill=config.BTN_STATS_SHADOW_RGB)
    draw.text((text_x, text_y), text, font=font_btn, fill=config.BTN_STATS_PINK_RGB)

    return cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)

def draw_menu_button(frame):
    if frame is None:
        return None

    x1, y1, x2, y2 = config.BTN_MENU

    pil_im = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_im)

    try:
        font_btn = ImageFont.truetype(config.FONT_PATH, 30)
    except IOError:
        font_btn = ImageFont.load_default()

    shadow_offset = 3
    corner_radius = 30
    # ombra nera dello sfondo e del bordo
    draw.rounded_rectangle(
        [x1 + shadow_offset, y1 + shadow_offset, x2 + shadow_offset, y2 + shadow_offset],
        radius=corner_radius,
        fill=config.BTN_STATS_SHADOW_RGB,
        outline=config.BTN_STATS_SHADOW_RGB,
        width=3
    )

    # sfondo e bordo
    draw.rounded_rectangle(
        [x1, y1, x2, y2],
        radius=corner_radius,
        fill=config.BTN_STATS_BG_RGB,
        outline=config.BTN_STATS_PINK_RGB,
        width=3
    )

    # testo
    text = "Menu'"
    bbox = draw.textbbox((0, 0), text, font=font_btn)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    text_x = x1 + ((x2 - x1) - text_w) // 2
    text_y = y1 + ((y2 - y1) - text_h) // 2 - bbox[1]

    # ombra del testo e testo principale
    draw.text((text_x + 2, text_y + 2), text, font=font_btn, fill=config.BTN_STATS_SHADOW_RGB)
    draw.text((text_x, text_y), text, font=font_btn, fill=config.BTN_STATS_PINK_RGB)

    return cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)




def draw_particles(frame, particles):
    if frame is None: return None
    for p in particles:
        px, py, life = p
        if sparkle_img is not None:
            frame = overlay_transparent(frame, sparkle_img, px, py, alpha_mod=life)
        else:
            cv2.circle(frame, (int(px), int(py)), int(5 * life), (255, 200, 255), -1)
    return frame

def draw_cursor(frame, x, y):
    if frame is None: return None
    if cursor_img is not None:
        frame = overlay_transparent(frame, cursor_img, x, y)
    else:
        cv2.circle(frame, (x, y), 15, (0, 255, 255), -1)
        cv2.circle(frame, (x, y), 15, (255, 255, 255), 2)
    return frame

def apply_transformation_effect(frame, bg_frame, fade_progress=1.0):
    if frame is None: return None
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = segmenter.process(frame_rgb)
    mask = results.segmentation_mask
    condition = np.stack((mask,) * 3, axis=-1) > 0.5
    
    pink_overlay = np.full(frame.shape, config.TINT_COLOR_BGR, dtype=np.uint8)
    tinted_user = cv2.addWeighted(frame, 0.6, pink_overlay, 0.4, 0)
    
    if bg_frame is None:
        bg_frame = np.zeros(frame.shape, dtype=np.uint8)
    else:
        bg_frame = cv2.resize(bg_frame, (frame.shape[1], frame.shape[0]))
        
    fully_transformed = np.where(condition, tinted_user, bg_frame)
    
    if fade_progress < 1.0:
        output_image = cv2.addWeighted(frame, 1.0 - fade_progress, fully_transformed, fade_progress, 0)
        return output_image
        
    return fully_transformed

IMAGE_CACHE = {}

def draw_winx_images(frame, winx_name):
    if frame is None: return None
    
    if winx_name not in IMAGE_CACHE:
        img_path = config.WINX_IMAGES.get(winx_name)
        if not img_path: return frame
        img_winx = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        if img_winx is None: return frame
        h, w = img_winx.shape[:2]
        new_w = 200
        new_h = int((new_w / w) * h)
        img_winx = cv2.resize(img_winx, (new_w, new_h))
        if img_winx.shape[2] == 4:
            alpha_img = img_winx[:, :, 3] / 255.0
            alpha_frame = 1.0 - alpha_img
            bgr_img = img_winx[:, :, :3]
            IMAGE_CACHE[winx_name] = (bgr_img, alpha_img, alpha_frame, new_w, new_h, True)
        else:
            IMAGE_CACHE[winx_name] = (img_winx, None, None, new_w, new_h, False)
    bgr_img, alpha_img, alpha_frame, new_w, new_h, is_transparent = IMAGE_CACHE[winx_name]
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
    if frame is None: return None
    overlay = frame.copy()
    cv2.rectangle(overlay, (20, 50), (620, 390), (0, 0, 0), -1)
    frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
    cv2.putText(frame, "CLASSIFICA AFFINITA'", (120, 90), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2)
    y_offset = 115
    for winx_name, perc, details in all_results:
        color = config.WINX_COLORS_BGR.get(winx_name, (255, 100, 255))
        cv2.putText(frame, f"{winx_name} {perc:.1f}%", (30, y_offset + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        bar_width = int((perc / 100.0) * 300)
        cv2.rectangle(frame, (210, y_offset), (210 + bar_width, y_offset + 20), color, -1)
        cv2.rectangle(frame, (210, y_offset), (510, y_offset + 20), (255, 255, 255), 2)
        details_text = f"Occhi: {details['eyes']:.0f}% | Capelli: {details['hair']:.0f}% | Pelle: {details['skin']:.0f}%"
        cv2.putText(frame, details_text, (210, y_offset + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 255, 200), 1)
        y_offset += 45

    frame = draw_avanti_button(frame)

    return frame

WINGS_CACHE = {}

def apply_wings_effect(frame, winx_name):
    if frame is None: return None
    
    if winx_name not in WINGS_CACHE:
        wings_path = config.WINX_WINGS_PATHS.get(winx_name, config.WINGS_PATH)
        img = cv2.imread(wings_path, cv2.IMREAD_UNCHANGED)
        WINGS_CACHE[winx_name] = img

    wings_img = WINGS_CACHE[winx_name]
    if wings_img is None: 
        return frame

    h, w, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # 1. Trova le spalle per posizionare le ali
    pose_results = pose_detector.process(frame_rgb)
    frame_with_wings = frame.copy()
    
    if pose_results.pose_landmarks:
        landmarks = pose_results.pose_landmarks.landmark
        l_sh = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        r_sh = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        center_x = int((l_sh.x + r_sh.x) * w / 2)
        center_y = int((l_sh.y + r_sh.y) * h / 2)
        shoulder_width = abs(l_sh.x - r_sh.x) * w
        
        wings_w = int(max(shoulder_width * 2.5, 100))
        wings_h = int(wings_w * (wings_img.shape[0] / wings_img.shape[1]))
        resized_wings = cv2.resize(wings_img, (wings_w, wings_h))
        neck_offset = int(wings_h * 0.18)
        frame_with_wings = overlay_transparent(frame_with_wings, resized_wings, center_x, center_y - neck_offset)
        
    # 2. Segmentazione su frame scalato (dimezza i tempi di calcolo)
    small_frame = cv2.resize(frame_rgb, (w // 2, h // 2))
    seg_results = segmenter.process(small_frame)
    mask = cv2.resize(seg_results.segmentation_mask, (w, h))
    condition = np.stack((mask,) * 3, axis=-1) > 0.5
    
    final_frame = np.where(condition, frame, frame_with_wings)
    
    return draw_menu_button(final_frame)