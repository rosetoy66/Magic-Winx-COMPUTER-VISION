import cv2
from face_detector import process_frame
from winx_percentages_calculator import calculate_winx_match
import time # <-- Aggiungi questo import in alto

def main():
    cap = cv2.VideoCapture(0)
    
    # Box Menu Principale
    btn_avvia = (50, 50, 250, 150)
    btn_esci = (390, 400, 590, 500)
    
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
            cv2.rectangle(frame, (btn_avvia[0], btn_avvia[1]), (btn_avvia[2], btn_avvia[3]), (0, 200, 0), -1)
            cv2.putText(frame, "AVVIA", (90, 110), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2)
            
            cv2.rectangle(frame, (btn_esci[0], btn_esci[1]), (btn_esci[2], btn_esci[3]), (0, 0, 200), -1)
            cv2.putText(frame, "ESCI", (440, 460), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2)
            
            if finger_pos:
                fx, fy = finger_pos
                cv2.circle(frame, (fx, fy), 15, (0, 255, 255), -1)
                cv2.circle(frame, (fx, fy), 15, (255, 255, 255), 2)
                
                if btn_avvia[0] < fx < btn_avvia[2] and btn_avvia[1] < fy < btn_avvia[3]:
                    if colors:
                        final_winx, final_perc = calculate_winx_match(colors['eyes'], colors['hair'], colors['skin'])
                        state = "CALCOLO"
                        time.sleep(0.5) # <-- Cooldown: evita click multipli accidentali
                        
                elif btn_esci[0] < fx < btn_esci[2] and btn_esci[1] < fy < btn_esci[3]:
                    print("Uscita in corso...")
                    break
                    
        elif state == "CALCOLO":
            cv2.putText(frame, f"Sei {final_winx}!", (150, 240), cv2.FONT_HERSHEY_DUPLEX, 1.8, (0, 255, 255), 3)
            cv2.putText(frame, f"Affinita': {final_perc:.1f}%", (180, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
            
            cv2.rectangle(frame, (btn_chiudi_piccolo[0], btn_chiudi_piccolo[1]), 
                                (btn_chiudi_piccolo[2], btn_chiudi_piccolo[3]), (0, 0, 150), -1)
            cv2.putText(frame, "INDIETRO", (510, 55), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

            if finger_pos:
                fx, fy = finger_pos
                cv2.circle(frame, (fx, fy), 15, (0, 255, 255), -1)
                cv2.circle(frame, (fx, fy), 15, (255, 255, 255), 2)
                
                if btn_chiudi_piccolo[0] < fx < btn_chiudi_piccolo[2] and btn_chiudi_piccolo[1] < fy < btn_chiudi_piccolo[3]:
                    print("Torno al menu...")
                    state = "MENU"
                    time.sleep(0.5) # <-- Cooldown vitale per non cliccare subito ESCI dal menu

        cv2.imshow("Benvenuta, fata!", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()