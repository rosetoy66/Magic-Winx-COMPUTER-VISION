import time
import threading
import json
import pyaudio
from config import model_path
from vosk import Model, KaldiRecognizer

class VoiceRecognizer:
    def __init__(self, model_path = model_path):
        self.magic_word_detected = False
        self.running = True
        self.thread = None
        
        # carica il modello Vosk interamente in locale
        #print("[Sistema] Caricamento modello locale in corso...")
        self.model = Model(model_path)
        #print("[Sistema] Modello caricato con successo.")

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
        # inizializza il riconoscitore a 16000 hz
        recognizer = KaldiRecognizer(self.model, 16000)
        p = pyaudio.PyAudio()
        
        # apre lo stream del microfono
        stream = p.open(format=pyaudio.paInt16, 
                        channels=1, 
                        rate=16000, 
                        input=True, 
                        frames_per_buffer=8192)
        stream.start_stream()
        
        # print("Microfono in ascolto. Pronuncia la frase magica!")
        
        while self.running:
            if self.magic_word_detected:
                time.sleep(0.3)
                continue

            # legge i dati grezzi dal microfono
            data = stream.read(4096, exception_on_overflow=False)
            
            # restituisce true quando rileva una pausa nel parlato
            if recognizer.AcceptWaveform(data):
                # estrae il testo dal json restituito da vosk
                result = json.loads(recognizer.Result())
                text = result.get("text", "").lower()
                
                if text:
                    # print(f" Riconosciuto: {text}")
                    
                    keywords_magic = ["magic", "magik", "magia", "megic"]
                    keywords_winx = ["winx", "wings", "vincs", "winks"]
                    keywords_vision = ["vision", "visione"]

                    found_magic_or_winx = any(k in text for k in keywords_magic + keywords_winx)
                    found_vision = any(k in text for k in keywords_vision)

                    if found_magic_or_winx or found_vision:
                        #print("PAROLA MAGICA RILEVATA!")
                        self.magic_word_detected = True