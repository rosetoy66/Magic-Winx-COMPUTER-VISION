import cv2
import time
import config
import ui
from face_detector import process_frame
from winx_percentages_calculator import calculate_winx_match

def is_inside_button(pos, btn_coords):
    # controlla se il dito è dentro le coordinate del bottone
    x, y = pos
    bx1, by1, bx2, by2 = btn_coords
    return bx1 < x < bx2 and by1 < y < by2

def main():
    cap = cv2.VideoCapture(0)
    bg_cap = cv2.VideoCapture(config.BG_VIDEO_PATH)
    
    # STATI POSSIBILI: "MENU", "TRASFORMAZIONE", "CALCOLO"
    state = "MENU"
    final_winx = ""
    final_perc = 0.0
    particles = [] 
    
    # Variabile per tracciare il tempo di inizio dell'animazione
    transformation_start_time = 0 

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        finger_pos, colors = process_frame(frame)

        # --- GESTIONE GRAFICA DEGLI STATI ---
        if state == "MENU":
            frame = ui.draw_menu_screen(frame)
            
        elif state == "TRASFORMAZIONE":
            ret_bg, bg_frame = bg_cap.read()
            if not ret_bg:
                bg_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret_bg, bg_frame = bg_cap.read()
            if not ret_bg: bg_frame = None

            frame = ui.apply_transformation_effect(frame, bg_frame)
            if time.time() - transformation_start_time >= 5.0:
                state = "CALCOLO"
                
        elif state == "CALCOLO":
            frame = ui.draw_result_screen(frame, final_winx, final_perc)
            frame = ui.draw_winx_images(frame, final_winx)
            # Aggiungiamo qui un bottone AVANTI
            cv2.rectangle(frame, (config.BTN_AVANTI[0], config.BTN_AVANTI[1]), (config.BTN_AVANTI[2], config.BTN_AVANTI[3]), (0, 150, 255), -1)
            cv2.putText(frame, "AVANTI", (config.BTN_AVANTI[0] + 25, config.BTN_AVANTI[1] + 40), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)
            
        elif state == "CLASSIFICA":
            # Passiamo l'array con tutti i risultati per fare il grafico a barre
            frame = ui.draw_ranking_screen(frame, all_results)
            
        elif state == "FILTRO_ALI":
            frame = ui.apply_wings_effect(frame)

        # GESTIONE DEL DITO E DELLE COLLISIONI
        if finger_pos:
            fx, fy = finger_pos
            particles.append([fx, fy, 1.0])
            frame = ui.draw_particles(frame, particles)
            frame = ui.draw_cursor(frame, fx, fy)
            
            if state == "MENU":
                if is_inside_button(finger_pos, config.BTN_AVVIA):
                    if colors:
                        # Assicurati di salvare anche all_results!
                        final_winx, final_perc, all_results = calculate_winx_match(colors['eyes'], colors['hair'], colors['skin'])
                        state = "TRASFORMAZIONE"
                        transformation_start_time = time.time() 
                        particles.clear() 
                        time.sleep(0.5) 
                        
                elif is_inside_button(finger_pos, config.BTN_ESCI):
                    break
                    
            elif state == "CALCOLO":
                if is_inside_button(finger_pos, config.BTN_AVANTI):
                    state = "CLASSIFICA"
                    particles.clear()
                    time.sleep(0.5)
                    
            elif state == "CLASSIFICA":
                if is_inside_button(finger_pos, config.BTN_PROSEGUI):
                    state = "FILTRO_ALI"
                    particles.clear()
                    time.sleep(0.5)
                    
            elif state == "FILTRO_ALI":
                if is_inside_button(finger_pos, config.BTN_MENU):
                    state = "MENU"
                    particles.clear()
                    time.sleep(0.5)

        # Decadimento vita delle particelle (scintille)
        for p in particles:
            p[2] -= config.PARTICLE_DECAY_RATE
        particles = [p for p in particles if p[2] > 0]

        cv2.imshow("Magic Winx: COMPUTER VISION!!", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    bg_cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()