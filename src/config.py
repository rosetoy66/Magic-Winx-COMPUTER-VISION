# palette winx
WINX_PROFILES_HEX = {
    "Bloom": {"eyes": "7ca69d", "hair": "b32821", "skin": "f0d3a1"}, 
    "Stella": {"eyes": "8c5914", "hair": "c49a37", "skin": "f2c991"},
    "Flora": {"eyes": "778742", "hair": "5c3a21", "skin": "fac49d"}, 
    "Aisha": {"eyes": "31545e", "hair": "3b2306", "skin": "995a25"}, 
    "Musa": {"eyes": "222d42", "hair": "1f1c36", "skin": "ebd1c5"},
    "Tecna": {"eyes": "176e73", "hair": "852b72", "skin": "e8ccc1"}  
}

WEIGHTS = {
    "hair": 0.65,
    "eyes": 0.05,
    "skin": 0.30
}

MAX_POSSIBLE_DISTANCE = 365.0

FONT_PATH = "./assets/winx_font.ttf"

# coordinate bottoni 
BTN_AVVIA = (70, 360, 270, 440)
BTN_ESCI = (370, 360, 570, 440) 
BTN_CHIUDI = (500, 20, 620, 80)

# BGR
BG_AVVIA_BGR = (243, 179, 128)
BG_ESCI_BGR = (67, 205, 194)
BORDER_PINK_BGR = (140, 0, 237)

# RGB
SHADOW_RGB = (70, 30, 70)
TEXT_PINK_RGB = (237, 0, 140)

# colori per il Bottone Statistiche
BTN_STATS_BG_RGB = (180, 194, 221)
BTN_STATS_PINK_RGB = (237, 3, 124)
BTN_STATS_SHADOW_RGB = (0, 0, 0)

# effetti
CURSOR_PATH = "./assets/cursor.png" # puntatore
SPARKLE_PATH = "./assets/sparkle.png" # immagine della singola particella scia

CURSOR_SIZE = (50, 50) # dimensione cursore
SPARKLE_SIZE = (20, 20) # dimensione scintille

PARTICLE_DECAY_RATE = 0.08 # velocità con cui svaniscono le particelle

# immagini winx
WINX_IMAGES = {
    "Bloom": "./assets/bloom.png",
    "Stella": "./assets/stella.png",
    "Flora": "./assets/flora.png",
    "Aisha": "./assets/aisha.png",
    "Musa": "./assets/musa.png",
    "Tecna": "./assets/tecna.png"
}

# video trasformazione 
BG_VIDEO_PATH = "./assets/magic_bg.mp4"
TINT_COLOR_BGR = (220, 130, 255)       #colore

# BGR per il grafico a barre di ogni Winx
WINX_COLORS_BGR = {
    "Bloom": (33, 40, 179),    # Rosso/Blu
    "Stella": (36, 161, 209),  # Giallo/Arancio
    "Flora": (35, 61, 110),    # Verde/Marrone
    "Aisha": (148, 116, 50),   # Verde acqua/Sabbia
    "Musa": (131, 28, 64),     # Blu/Magenta scuro
    "Tecna": (114, 43, 133)    # Viola
}

# coordinate dei nuovi bottoni
BTN_STATISTICHE = (40, 400, 200, 460)
BTN_AVANTI = (460, 400, 620, 460)
BTN_MENU = (20, 20, 380, 80) 
BTN_ESCI_ALI = (480, 20, 620, 80)

WINGS_PATH = "./assets/wings.png"  

WINX_WINGS_PATHS = {
    "Bloom": "assets/bloom_ali.png",
    "Stella": "assets/stella_ali.png",
    "Flora": "assets/flora_ali.png",
    "Musa": "assets/musa_ali.png",
    "Tecna": "assets/tecna_ali.png",
    "Aisha": "assets/aisha_ali.png"
}

WINX_GROUP_PATH = "./assets/winx.png"

# video di trasformazione in base alla Winx assegnata
WINX_VIDEOS_PATHS = {
    "Bloom": "./assets/bloom_video.mp4",
    "Stella": "./assets/stella_video.mp4",
    "Flora": "./assets/flora_video.mp4",
    "Musa": "./assets/musa_video.mp4",
    "Tecna": "./assets/tecna_video.mp4",
    "Aisha": "./assets/aisha_video.mp4"
}

# audio
SOUND1_PATH = "./assets/suono1.mp3" 
SOUND2_PATH = "./assets/suono2.mp3" 
BGM_PATH = "./assets/musica_trasformazione.mp3"

model_path = "./assets/model_it" 