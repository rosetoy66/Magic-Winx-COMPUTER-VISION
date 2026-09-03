import cv2
import time
import config
import ui
from face_detector import process_frame
from winx_percentages_calculator import calculate_winx_match
from voice_recognizer import VoiceRecognizer

def is_inside_button(pos, btn_coords):
    x, y = pos
    bx1, by1, bx2, by2 = btn_coords
    return bx1 < x < bx2 and by1 < y < by2

def main():
    # inizializzazione ed avvio del modulo vocale
    voice_rec = VoiceRecognizer()
    voice_rec.start()
    
    cap = cv2.VideoCapture(0)
    bg_cap = cv2.VideoCapture(config.BG_VIDEO_PATH)
    
    state = "INTRO"
    
    final_winx = ""
    final_perc = 0.0
    all_results = []
    particles = [] 
    
    # timer
    intro_start_time = time.time()
    fade_start_time = None
    transformation_start_time = 0 
    analysis_start_time = 0 

    while True:
        ret, frame = cap.read()
        if not ret: 
            break
        
        frame = cv2.flip(frame, 1)
        
        finger_pos = None
        colors = None
        
        if state != "INTRO":
            finger_pos, colors = process_frame(frame)

        # GESTIONE GRAFICA DEGLI STATI
        if state == "INTRO":
            current_time = time.time()
            elapsed_state_time = current_time - intro_start_time
            fade_progress = 0.0
            
            if voice_rec.magic_word_detected and fade_start_time is None:
                fade_start_time = current_time
                
            if fade_start_time is not None:
                fade_progress = (current_time - fade_start_time) / 1.0
                if fade_progress >= 1.0:
                    state = "ANALISI" 
                    analysis_start_time = time.time()
                    particles.clear()
            
            frame = ui.draw_intro_screen(frame, elapsed_state_time, fade_progress)
            
        elif state == "ANALISI":
            cv2.putText(frame, "Scansione tratti somatici...", (30, 40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 200, 255), 2)
            
            if time.time() - analysis_start_time > 4.0:
                if colors:
                    final_winx, final_perc, all_results = calculate_winx_match(colors['eyes'], colors['hair'], colors['skin'])
                    state = "TRASFORMAZIONE"
                    transformation_start_time = time.time()
                    particles.clear()
                else:
                    cv2.putText(frame, "Inquadra bene il volto!", (30, 80), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 255), 2)

        elif state == "TRASFORMAZIONE":
            ret_bg, bg_frame = bg_cap.read()
            if not ret_bg:
                bg_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret_bg, bg_frame = bg_cap.read()
            if not ret_bg: 
                bg_frame = None

            elapsed_transform = time.time() - transformation_start_time
            fade_progress = min(elapsed_transform / 1.0, 1.0)
            frame = ui.apply_transformation_effect(frame, bg_frame, fade_progress)
            
            if elapsed_transform >= 5.0:
                state = "CALCOLO"
                
        elif state == "CALCOLO":
            frame = ui.draw_result_screen(frame, final_winx, final_perc)
            frame = ui.draw_winx_images(frame, final_winx)
            cv2.rectangle(frame, (config.BTN_AVANTI[0], config.BTN_AVANTI[1]), (config.BTN_AVANTI[2], config.BTN_AVANTI[3]), (0, 150, 255), -1)
            cv2.putText(frame, "AVANTI", (config.BTN_AVANTI[0] + 25, config.BTN_AVANTI[1] + 40), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)
            
        elif state == "CLASSIFICA":
            frame = ui.draw_ranking_screen(frame, all_results)
            
        elif state == "FILTRO_ALI":
            frame = ui.apply_wings_effect(frame, final_winx)

        # GESTIONE DEL DITO E DELLE COLLISIONI
        if state not in ["INTRO", "ANALISI"] and finger_pos:
            fx, fy = finger_pos
            particles.append([fx, fy, 1.0])
            frame = ui.draw_particles(frame, particles)
            frame = ui.draw_cursor(frame, fx, fy)
            
            if state == "MENU":
                if is_inside_button(finger_pos, config.BTN_AVVIA):
                    if colors:
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
                    state = "INTRO"
                    intro_start_time = time.time()
                    fade_start_time = None
                    
                    # Reset dello stato vocale dal modulo esterno
                    voice_rec.reset()
                    
                    final_winx = ""
                    colors = None
                    particles.clear()
                    time.sleep(0.5)
                    
        for p in particles:
            p[2] -= config.PARTICLE_DECAY_RATE
        particles = [p for p in particles if p[2] > 0]

        cv2.imshow("Magic Winx: COMPUTER VISION!!", frame)
        
        # GESTIONE TASTIERA
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            voice_rec.stop()
            break
        elif key == ord('t'):
            voice_rec.trigger_manual()

    cap.release()
    bg_cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()