import cv2
from face_detector import process_frame
from winx_percentages_calculator import calculate_winx_match

def main():
    cap = cv2.VideoCapture(0)
    
    # Box Menu Principale
    btn_avvia = (50, 50, 250, 150)
    btn_esci = (390, 50, 590, 150)
    
    # Box Schermata Calcolo (pulsante più piccolo, in alto a destra)
    btn_chiudi_piccolo = (500, 20, 620, 80)
    
    state = "MENU"

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        
        # Elaboro sempre il frame, a prescindere dallo stato, per avere il cursore
        finger_pos, colors = process_frame(frame)
        
        if state == "MENU":
            # --- Rendering Menu ---
            cv2.rectangle(frame, (btn_avvia[0], btn_avvia[1]), (btn_avvia[2], btn_avvia[3]), (0, 200, 0), -1)
            cv2.putText(frame, "AVVIA", (90, 110), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2)
            
            cv2.rectangle(frame, (btn_esci[0], btn_esci[1]), (btn_esci[2], btn_esci[3]), (0, 0, 200), -1)
            cv2.putText(frame, "ESCI", (440, 110), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2)
            
            # --- Logica Cursore Menu ---
            if finger_pos:
                fx, fy = finger_pos
                cv2.circle(frame, (fx, fy), 15, (0, 255, 255), -1)
                cv2.circle(frame, (fx, fy), 15, (255, 255, 255), 2)
                
                # Hitbox Menu
                if btn_avvia[0] < fx < btn_avvia[2] and btn_avvia[1] < fy < btn_avvia[3]:
                    print("Pulsante AVVIA premuto!")
                    if colors:
                        calculate_winx_match(colors['eyes'], colors['hair'], colors['skin'])
                        state = "CALCOLO" 
                        
                elif btn_esci[0] < fx < btn_esci[2] and btn_esci[1] < fy < btn_esci[3]:
                    print("Uscita in corso...")
                    break
                    
        elif state == "CALCOLO":
            # --- Rendering Schermata Risultati ---
            cv2.putText(frame, "Dati estratti!", (200, 240), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 255, 255), 3)
            cv2.putText(frame, "Guarda il terminale", (200, 290), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)
            
            # Disegno il bottone "CHIUDI" piccolo in alto a destra
            cv2.rectangle(frame, (btn_chiudi_piccolo[0], btn_chiudi_piccolo[1]), 
                                (btn_chiudi_piccolo[2], btn_chiudi_piccolo[3]), (0, 0, 150), -1)
            cv2.putText(frame, "ESCI", (525, 60), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)

            # --- Logica Cursore Calcolo ---
            if finger_pos:
                fx, fy = finger_pos
                cv2.circle(frame, (fx, fy), 15, (0, 255, 255), -1)
                cv2.circle(frame, (fx, fy), 15, (255, 255, 255), 2)
                
                # Hitbox Chiudi Piccolo
                if btn_chiudi_piccolo[0] < fx < btn_chiudi_piccolo[2] and btn_chiudi_piccolo[1] < fy < btn_chiudi_piccolo[3]:
                    print("Uscita in corso...")
                    break

        cv2.imshow("Magic Winx - Mirror UI", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()