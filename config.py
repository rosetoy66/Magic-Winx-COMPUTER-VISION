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

FONT_PATH = "./Utilz/winx_font.ttf"

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

# effetti
CURSOR_PATH = "./Utilz/cursor.png" # puntatore
SPARKLE_PATH = "./Utilz/sparkle.png" # immagine della singola particella scia

CURSOR_SIZE = (50, 50) # dimensione cursore
SPARKLE_SIZE = (20, 20) # dimensione scintille

PARTICLE_DECAY_RATE = 0.08 # velocità con cui svaniscono le particelle

# immagini winx
WINX_IMAGES = {
    "Bloom": "./Utilz/bloom.png",
    "Stella": "./Utilz/stella.png",
    "Flora": "./Utilz/flora.png",
    "Aisha": "./Utilz/aisha.png",
    "Musa": "./Utilz/musa.png",
    "Tecna": "./Utilz/tecna.png"
}

# --- TRASFORMAZIONE 
BG_VIDEO_PATH = "./Utilz/magic_bg.mp4"
TINT_COLOR_BGR = (220, 130, 255)       #colore

# --- CLASSIFICA E FILTRO ALI ---
# Colori BGR specifici per il grafico a barre di ogni Winx
WINX_COLORS_BGR = {
    "Bloom": (33, 40, 179),    # Rosso/Blu
    "Stella": (36, 161, 209),  # Giallo/Arancio
    "Flora": (35, 61, 110),    # Verde/Marrone
    "Aisha": (148, 116, 50),   # Verde acqua/Sabbia
    "Musa": (131, 28, 64),     # Blu/Magenta scuro
    "Tecna": (114, 43, 133)    # Viola
}

# Coordinate dei nuovi bottoni
BTN_AVANTI = (40, 400, 200, 460)     # Spostato in basso a SINISTRA
BTN_PROSEGUI = (460, 400, 620, 460)  # Per passare da CLASSIFICA a FILTRO_ALI
BTN_MENU = (20, 20, 120, 80)         # Per tornare al menu dal Filtro Ali

WINGS_PATH = "./Utilz/wings.png"     # PNG trasparente delle ali da fata

WINX_WINGS_PATHS = {
    "Bloom": "Utilz/bloom_ali.png",
    "Stella": "Utilz/stella_ali.png",
    "Flora": "Utilz/flora_ali.png",
    "Musa": "Utilz/musa_ali.png",
    "Tecna": "Utilz/tecna_ali.png",
    "Aisha": "Utilz/aisha_ali.png"
}