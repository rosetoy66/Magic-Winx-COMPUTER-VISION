import cv2
import time
import pygame
import numpy as np
import config
import ui
from face_detector import process_frame
from winx_percentages_calculator import calculate_winx_match
from voice_recognizer import VoiceRecognizer

pygame.mixer.init()

try:
    snd1 = pygame.mixer.Sound(config.SOUND1_PATH)
    snd2 = pygame.mixer.Sound(config.SOUND2_PATH)
    pygame.mixer.music.load(config.BGM_PATH)
except Exception as e:
    print(f"[Audio] Qualche file audio manca, ma il programma continua! Errore: {e}")
    snd1, snd2 = None, None

def play_sfx(snd_obj):
    if snd_obj:
        snd_obj.play()

def is_inside_button(pos, btn_coords):
    x, y = pos
    bx1, by1, bx2, by2 = btn_coords
    return bx1 < x < bx2 and by1 < y < by2

def main():
    voice_rec = VoiceRecognizer()
    voice_rec.start()
    
    cap = cv2.VideoCapture(0)
    bg_cap = None
    
    state = "INTRO"
    
    final_winx = ""
    final_perc = 0.0
    all_results = []
    particles = [] 
    
    intro_start_time = time.time()
    fade_start_time = None
    transformation_start_time = 0 
    analysis_start_time = 0 
    flash_start_time = None

    while True:
        ret, frame = cap.read()
        if not ret or frame is None: break
        
        frame = cv2.flip(frame, 1)
        finger_pos = None
        colors = None
        
        if state != "INTRO":
            # disegna i landmark sulla copia, lasciando il nostro frame pulito
            frame, finger_pos, colors = process_frame(frame.copy())

        # gestione stati
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
            missing_face = False
            
            if time.time() - analysis_start_time > 1.5:
                if colors:
                    final_winx, final_perc, all_results = calculate_winx_match(colors['eyes'], colors['hair'], colors['skin'])
                    
                    video_path = getattr(config, 'WINX_VIDEOS_PATHS', {}).get(final_winx, getattr(config, 'BG_VIDEO_PATH', None))
                    if bg_cap is not None: bg_cap.release()
                    if video_path: bg_cap = cv2.VideoCapture(video_path)
                    
                    state = "TRASFORMAZIONE"
                    transformation_start_time = time.time()
                    particles.clear()
                    
                    try: pygame.mixer.music.play(-1)
                    except: pass
                else:
                    # se non trova il volto, da errore
                    missing_face = True
            
            # disegna le scritte tramite la nostra nuova funzione in ui.py!
            frame = ui.draw_analisi_screen(frame, missing_face)
            
            if time.time() - analysis_start_time > 4.0:
                if colors:
                    final_winx, final_perc, all_results = calculate_winx_match(colors['eyes'], colors['hair'], colors['skin'])
                    
                    video_path = getattr(config, 'WINX_VIDEOS_PATHS', {}).get(final_winx, getattr(config, 'BG_VIDEO_PATH', None))
                    if bg_cap is not None: bg_cap.release()
                    if video_path: bg_cap = cv2.VideoCapture(video_path)
                    
                    state = "TRASFORMAZIONE"
                    transformation_start_time = time.time()
                    particles.clear()
                    
                    try: pygame.mixer.music.play(-1)
                    except: pass
                else:
                    cv2.putText(frame, "Inquadra bene il volto!", (30, 80), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 255), 2)

        elif state == "TRASFORMAZIONE":
            bg_frame = None
            if bg_cap is not None:
                ret_bg, bg_frame = bg_cap.read()
                if not ret_bg:
                    bg_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret_bg, bg_frame = bg_cap.read()
                if not ret_bg: bg_frame = None

            elapsed_transform = time.time() - transformation_start_time
            fade_progress = min(elapsed_transform / 1.0, 1.0)
            frame = ui.apply_transformation_effect(frame, bg_frame, fade_progress)
            
            if elapsed_transform >= 5.0:
                state = "CALCOLO"
                # timer flash appena finisce la trasformazione
                flash_start_time = time.time() 
                
        elif state == "CALCOLO":
            frame = ui.draw_result_screen(frame, final_winx, final_perc)
            frame = ui.draw_winx_images(frame, final_winx)
            frame = ui.draw_stats_button(frame)
            
            # flash bianco
            if flash_start_time is not None:
                elapsed_flash = time.time() - flash_start_time
                flash_duration = 0.6 
                if elapsed_flash < flash_duration:
                    # Parte dall'85% di bianco e scende dolcemente a 0
                    flash_intensity = 0.85 * (1.0 - (elapsed_flash / flash_duration))
                    white_overlay = np.full(frame.shape, 255, dtype=np.uint8)
                    frame = cv2.addWeighted(white_overlay, flash_intensity, frame, 1.0 - flash_intensity, 0)
                else:
                    flash_start_time = None # Fine del flash
            
        elif state == "CLASSIFICA":
            frame = ui.draw_ranking_screen(frame, all_results)
            
        elif state == "FILTRO_ALI":
            frame = ui.apply_wings_effect(frame, final_winx)


        # gestione dito e collisione
        if state not in ["INTRO", "ANALISI"] and finger_pos:
            fx, fy = finger_pos
            particles.append([fx, fy, 1.0])
            frame = ui.draw_particles(frame, particles)
            frame = ui.draw_cursor(frame, fx, fy)
            
            if state == "MENU":
                if is_inside_button(finger_pos, config.BTN_AVVIA):
                    play_sfx(snd1)
                    if colors:
                        final_winx, final_perc, all_results = calculate_winx_match(colors['eyes'], colors['hair'], colors['skin'])
                        
                        video_path = getattr(config, 'WINX_VIDEOS_PATHS', {}).get(final_winx, getattr(config, 'BG_VIDEO_PATH', None))
                        if bg_cap is not None: bg_cap.release()
                        if video_path: bg_cap = cv2.VideoCapture(video_path)
                        
                        state = "TRASFORMAZIONE"
                        transformation_start_time = time.time() 
                        particles.clear() 
                        
                        try: pygame.mixer.music.play(-1)
                        except: pass
                        
                        time.sleep(0.5) 
                        
                elif is_inside_button(finger_pos, config.BTN_ESCI):
                    play_sfx(snd2)
                    break
                    
            elif state == "CALCOLO":
                if is_inside_button(finger_pos, config.BTN_STATISTICHE):
                    play_sfx(snd1)
                    state = "CLASSIFICA"
                    particles.clear()
                    time.sleep(0.5)
                    
            elif state == "CLASSIFICA":
                if is_inside_button(finger_pos, config.BTN_AVANTI):
                    play_sfx(snd1)
                    state = "FILTRO_ALI"
                    particles.clear()
                    time.sleep(0.5)
                    
            elif state == "FILTRO_ALI":
                if is_inside_button(finger_pos, config.BTN_MENU):
                    play_sfx(snd1)
                    state = "INTRO"
                    intro_start_time = time.time()
                    fade_start_time = None
                    flash_start_time = None
                    voice_rec.reset()
                    final_winx = ""
                    colors = None
                    particles.clear()
                    
                    if bg_cap is not None:
                        bg_cap.release()
                        bg_cap = None
                    
                    try: pygame.mixer.music.stop()
                    except: pass
                    time.sleep(0.5)
                    
                elif is_inside_button(finger_pos, getattr(config, 'BTN_ESCI_ALI', (0,0,0,0))):
                    play_sfx(snd2)
                    break
                    
        for p in particles:
            p[2] -= config.PARTICLE_DECAY_RATE
        particles = [p for p in particles if p[2] > 0]

        if frame is not None:
            cv2.imshow("Magic Winx: COMPUTER VISION!!", frame)
        
        # debug mode
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            voice_rec.stop()
            break
        elif key == ord('t'):
            voice_rec.trigger_manual()
            
        # tasti da 1 a 6
        elif state == "INTRO" and key in [ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6')]:
            debug_map = {
                ord('1'): "Bloom", ord('2'): "Stella", ord('3'): "Flora",
                ord('4'): "Tecna", ord('5'): "Musa", ord('6'): "Aisha"
            }
            
            final_winx = debug_map[key]
            final_perc = 100.0
            
            all_results = []
            for w in ["Bloom", "Stella", "Flora", "Aisha", "Musa", "Tecna"]:
                if w == final_winx:
                    all_results.append((w, 100.0, {'eyes': 100, 'hair': 100, 'skin': 100}))
                else:
                    all_results.append((w, 0.0, {'eyes': 0, 'hair': 0, 'skin': 0}))
                    
            all_results.sort(key=lambda x: x[1], reverse=True)
            
            video_path = getattr(config, 'WINX_VIDEOS_PATHS', {}).get(final_winx, getattr(config, 'BG_VIDEO_PATH', None))
            if bg_cap is not None: 
                bg_cap.release()
            if video_path: 
                bg_cap = cv2.VideoCapture(video_path)
            
            state = "TRASFORMAZIONE"
            transformation_start_time = time.time()
            particles.clear()
            voice_rec.reset() 
            
            try: 
                pygame.mixer.music.play(-1)
            except: 
                pass

# chiusura e pulizia
    cap.release()
    if bg_cap is not None: 
        bg_cap.release()
    cv2.destroyAllWindows()
    pygame.mixer.quit()

if __name__ == "__main__":
    main()