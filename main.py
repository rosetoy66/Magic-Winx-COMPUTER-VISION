import cv2
from face_detector import process_frame
from winx_percentages_calculator import calculate_winx_match
import time
from PIL import Image, ImageFont, ImageDraw
import numpy as np

def draw_centered_text(draw, text, font, btn_coords, text_color, shadow_color):
    """Funzione helper per centrare il testo dentro un bottone con Pillow."""
    x1, y1, x2, y2 = btn_coords
    btn_w = x2 - x1
    btn_h = y2 - y1
    
    # Calcola le dimensioni esatte della parola con questo font
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    # Trova il centro matematico
    text_x = x1 + (btn_w - text_w) // 2
    text_y = y1 + (btn_h - text_h) // 2 - bbox[1] 
    
    # Disegna ombra e testo
    draw.text((text_x + 2, text_y + 2), text, font=font, fill=shadow_color)
    draw.text((text_x, text_y), text, font=font, fill=text_color)

def main():
    cap = cv2.VideoCapture(0)

    btn_avvia = (70, 360, 270, 440)
    btn_esci = (370, 360, 570, 440) 
    
    # Box Schermata Calcolo
    btn_chiudi_piccolo = (500, 20, 620, 80)
    
    state = "MENU"
    final_winx = ""
    final_perc = 0.0

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        finger_pos, colors = process_frame(frame)

        if state == "MENU":
            # BGR
            blue_bgr = (243, 179, 128)
            pink_bgr = (140, 0, 237)
            green_bgr = (67, 205, 194)

            # bottone AVVIA
            cv2.rectangle(frame, (btn_avvia[0], btn_avvia[1]), (btn_avvia[2], btn_avvia[3]), blue_bgr, -1)
            cv2.rectangle(frame, (btn_avvia[0], btn_avvia[1]), (btn_avvia[2], btn_avvia[3]), pink_bgr, 4)
            
            # bottone ESCI
            cv2.rectangle(frame, (btn_esci[0], btn_esci[1]), (btn_esci[2], btn_esci[3]), green_bgr, -1)
            cv2.rectangle(frame, (btn_esci[0], btn_esci[1]), (btn_esci[2], btn_esci[3]), pink_bgr, 4)
            
            # converte l'immagine da BGR a RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_im = Image.fromarray(frame_rgb)
            draw = ImageDraw.Draw(pil_im)
            
            # font
            try:
                font = ImageFont.truetype("./Utilz/winx_font.ttf", 40) 
            except IOError:
                font = ImageFont.load_default() 

            shadow_color_rgb = (70, 30, 70)
            white_rgb = (237, 0, 140)

            # centra il testo nei bottoni
            draw_centered_text(draw, "Avvia", font, btn_avvia, white_rgb, shadow_color_rgb)
            draw_centered_text(draw, "Esci", font, btn_esci, white_rgb, shadow_color_rgb)

            # riconverte l'immagine da Pillow a OpenCV (da RGB a BGR)
            frame = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)
            
            if finger_pos:
                fx, fy = finger_pos
                cv2.circle(frame, (fx, fy), 15, (0, 255, 255), -1)
                cv2.circle(frame, (fx, fy), 15, (255, 255, 255), 2)
                
                # Collisione Bottone Avvia
                if btn_avvia[0] < fx < btn_avvia[2] and btn_avvia[1] < fy < btn_avvia[3]:
                    if colors:
                        final_winx, final_perc = calculate_winx_match(colors['eyes'], colors['hair'], colors['skin'])
                        state = "CALCOLO"
                        time.sleep(0.5) # Cooldown
                        
                # Collisione Bottone Esci
                elif btn_esci[0] < fx < btn_esci[2] and btn_esci[1] < fy < btn_esci[3]:
                    print("Uscita in corso...")
                    break
                    
        elif state == "CALCOLO":
            # Testo del risultato
            cv2.putText(frame, f"Sei {final_winx}!", (150, 240), cv2.FONT_HERSHEY_DUPLEX, 1.8, (0, 255, 255), 3)
            cv2.putText(frame, f"Affinita': {final_perc:.1f}%", (180, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
            
            # Bottone Indietro
            cv2.rectangle(frame, (btn_chiudi_piccolo[0], btn_chiudi_piccolo[1]), 
                                (btn_chiudi_piccolo[2], btn_chiudi_piccolo[3]), (0, 0, 150), -1)
            cv2.putText(frame, "INDIETRO", (510, 55), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

            if finger_pos:
                fx, fy = finger_pos
                cv2.circle(frame, (fx, fy), 15, (0, 255, 255), -1)
                cv2.circle(frame, (fx, fy), 15, (255, 255, 255), 2)
                
                if btn_chiudi_piccolo[0] < fx < btn_chiudi_piccolo[2] and btn_chiudi_piccolo[1] < fy < btn_chiudi_piccolo[3]:
                    print("Torno al menù")
                    state = "MENU"
                    time.sleep(0.5) # Cooldown

        cv2.imshow("Magic Winx: COMPUTER VISION!!", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()