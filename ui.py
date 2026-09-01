import cv2
import numpy as np
from PIL import Image, ImageFont, ImageDraw
import config

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