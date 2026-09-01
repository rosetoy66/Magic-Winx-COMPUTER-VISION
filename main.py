import cv2
import time
import config
import ui
from face_detector import process_frame
from winx_percentages_calculator import calculate_winx_match

    """Funzione helper per centrare il testo dentro un bottone con Pillow."""
def is_inside_button(pos, btn_coords):
    # controlla se il dito è dentro le coordinate del bottone
    x, y = pos
    bx1, by1, bx2, by2 = btn_coords
    return bx1 < x < bx2 and by1 < y < by2

def main():
    cap = cv2.VideoCapture(0)
    
    state = "MENU"
    final_winx = ""
    final_perc = 0.0

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        finger_pos, colors = process_frame(frame)

        # 1. DISEGNO DELL'INTERFACCIA
        if state == "MENU":
            frame = ui.draw_menu_screen(frame)
        elif state == "CALCOLO":
            frame = ui.draw_result_screen(frame, final_winx, final_perc)

        # 2. GESTIONE DEL DITO E DELLE COLLISIONI
        if finger_pos:
            fx, fy = finger_pos
            cv2.circle(frame, (fx, fy), 15, (0, 255, 255), -1)
            cv2.circle(frame, (fx, fy), 15, (255, 255, 255), 2)
            
            if state == "MENU":
                if is_inside_button(finger_pos, config.BTN_AVVIA):
                    if colors:
                        final_winx, final_perc = calculate_winx_match(colors['eyes'], colors['hair'], colors['skin'])
                        state = "CALCOLO"
                        time.sleep(0.5) 
                        
                elif is_inside_button(finger_pos, config.BTN_ESCI):
                    print("Uscita in corso...")
                    break
                    
            elif state == "CALCOLO":
                if is_inside_button(finger_pos, config.BTN_CHIUDI):
                    print("Torno al menù")
                    state = "MENU"
                    time.sleep(0.5)

        cv2.imshow("Magic Winx: COMPUTER VISION!!", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()