import time
import threading
import speech_recognition as sr

class VoiceRecognizer:
    def __init__(self):
        self.magic_word_detected = False
        self.running = True
        self.thread = None

    def start(self):
        # avvia il thread di ascolto in background
        self.running = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()

    def stop(self):
        # ferma il ciclo di ascolto del thread
        self.running = False

    def reset(self):
        # resetta lo stato per permettere una nuova rilevazione
        self.magic_word_detected = False

    def trigger_manual(self):
        # attiva manualmente la parola magica
        self.magic_word_detected = True

    def _listen_loop(self):
        recognizer = sr.Recognizer()
        
        with sr.Microphone() as source:
            print("[Microfono] Calibrazione rumore di fondo in corso...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("[Microfono] In ascolto. Pronuncia la frase magica!")
            
            while self.running:
                if self.magic_word_detected:
                    time.sleep(0.3)
                    continue

                try:
                    audio = recognizer.listen(source, timeout=1, phrase_time_limit=4)
                    text = recognizer.recognize_google(audio, language="it-IT").lower()
                    print(f"[Speech-to-Text] Riconosciuto: {text}")
                    
                    keywords_magic = ["magic", "magik", "magia"]
                    keywords_winx = ["winx", "wings", "vincs", "winks"]
                    keywords_vision = ["vision", "visione"]

                    found_magic_or_winx = any(k in text for k in keywords_magic + keywords_winx)
                    found_vision = any(k in text for k in keywords_vision)

                    if found_magic_or_winx or found_vision:
                        print("PAROLA MAGICA RILEVATA!")
                        self.magic_word_detected = True
                        
                except sr.WaitTimeoutError:
                    continue 
                except sr.UnknownValueError:
                    pass 
                except sr.RequestError as e:
                    print(f"[Errore SR] Rete assente o API irraggiungibile: {e}")
                    pass