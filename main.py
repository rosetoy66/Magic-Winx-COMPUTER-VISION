import cv2
import time
import threading
import speech_recognition as sr
import config
import ui
from face_detector import process_frame
from winx_percentages_calculator import calculate_winx_match

# --- GESTIONE RICONOSCIMENTO VOCALE (NLP/ASR) in Background ---
magic_word_detected = False

def listen_for_magic_words():
    global magic_word_detected
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("[Microfono] Calibrazione rumore di fondo in corso...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("[Microfono] In ascolto. Pronuncia la frase magica!")
        
        while not magic_word_detected:
            try:
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=4)
                text = recognizer.recognize_google(audio, language="it-IT").lower()
                print(f"[Speech-to-Text] Riconosciuto: {text}")
                
                # Check flessibile delle keyword
                if ("magic" in text or "winx" in text) and "vision" in text:
                    print("*** PAROLA MAGICA RILEVATA! ***")
                    magic_word_detected = True
                    break
                    
            except sr.WaitTimeoutError:
                continue 
            except sr.UnknownValueError:
                pass 
            except sr.RequestError as e:
                print(f"[Errore SR] Rete assente o API irraggiungibile: {e}")
                pass

def is_inside_button(pos, btn_coords):
    x, y = pos
    bx1, by1, bx2, by2 = btn_coords
    return bx1 < x < bx2 and by1 < y < by2

def main():
    global magic_word_detected
    
    audio_thread = threading.Thread(target=listen_for_magic_words, daemon=True)
    audio_thread.start()
    
    cap = cv2.VideoCapture(0)
    bg_cap = cv2.VideoCapture(config.BG_VIDEO_PATH)
    
    # STATI AGGIORNATI: aggiunto "ANALISI"
    state = "INTRO"
    
    final_winx = ""
    final_perc = 0.0
    all_results = []
    particles = [] 
    
    # Timer
    intro_start_time = time.time()
    fade_start_time = None
    transformation_start_time = 0 
    analysis_start_time = 0 # Timer per la fase di analisi automatica

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        
        finger_pos = None
        colors = None
        # Avviamo il process_frame sempre tranne nell'intro
        if state != "INTRO":
            finger_pos, colors = process_frame(frame)

        # --- GESTIONE GRAFICA DEGLI STATI ---
        
        if state == "INTRO":
            current_time = time.time()
            elapsed_state_time = current_time - intro_start_time
            fade_progress = 0.0
            
            if magic_word_detected and fade_start_time is None:
                fade_start_time = current_time
                
            if fade_start_time is not None:
                fade_progress = (current_time - fade_start_time) / 1.0
                if fade_progress >= 1.0:
                    # Invece di andare al MENU, andiamo in ANALISI
                    state = "ANALISI" 
                    analysis_start_time = time.time()
                    particles.clear()
            
            frame = ui.draw_intro_screen(frame, elapsed_state_time, fade_progress)
            
        elif state == "ANALISI":
            # Scritta a schermo per far capire che sta analizzando in automatico
            cv2.putText(frame, "Scansione tratti somatici...", (30, 40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 200, 255), 2)
            
            # Aspettiamo 4 secondi in modo che l'utente possa vedere la maschera sul volto
            if time.time() - analysis_start_time > 4.0:
                if colors:
                    # Appena ha i colori, fa il calcolo in automatico e passa alla trasformazione
                    final_winx, final_perc, all_results = calculate_winx_match(colors['eyes'], colors['hair'], colors['skin'])
                    state = "TRASFORMAZIONE"
                    transformation_start_time = time.time()
                    particles.clear()
                else:
                    # Se non trova nessuno, lo segnala e aspetta
                    cv2.putText(frame, "Inquadra bene il volto!", (30, 80), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 255), 2)

        elif state == "TRASFORMAZIONE":
            ret_bg, bg_frame = bg_cap.read()
            if not ret_bg:
                bg_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret_bg, bg_frame = bg_cap.read()
            if not ret_bg: bg_frame = None

            # Calcola da quanto tempo è iniziata la trasformazione
            elapsed_transform = time.time() - transformation_start_time
            
            # Calcola l'opacità per il primo secondo (da 0.0 a 1.0)
            fade_progress = min(elapsed_transform / 1.0, 1.0)

            # Passa il valore del fade alla UI
            frame = ui.apply_transformation_effect(frame, bg_frame, fade_progress)
            
            # Dopo 5 secondi passa ai risultati
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


        # --- GESTIONE DEL DITO E DELLE COLLISIONI ---
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
                    # INIZIO FIX: Resettiamo tutto e torniamo alla schermata iniziale!
                    state = "INTRO"
                    
                    # Resettiamo i timer e la voce per il prossimo utente
                    intro_start_time = time.time()
                    fade_start_time = None
                    magic_word_detected = False
                    
                    # Puliamo i dati vecchi
                    final_winx = ""
                    colors = None
                    particles.clear()
                    
                    time.sleep(0.5)
                    
        for p in particles:
            p[2] -= config.PARTICLE_DECAY_RATE
        particles = [p for p in particles if p[2] > 0]

        cv2.imshow("Magic Winx: COMPUTER VISION!!", frame)
        
        # --- GESTIONE TASTIERA ---
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('t'):  # Premi 't' per triggerare manualmente l'inizio!
            magic_word_detected = True

    cap.release()
    bg_cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()