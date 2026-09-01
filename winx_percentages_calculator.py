import math
import colorsys

# Dizionario con i profili esatti (valori in HEX)
WINX_PROFILES_HEX = {
    "Bloom": {"eyes": "7ca69d", "hair": "b32821", "skin": "f0d3a1"}, 
    "Stella": {"eyes": "8c5914", "hair": "d1a124", "skin": "f2c991"},
    "Flora": {"eyes": "778742", "hair": "6e3d23", "skin": "e08f55"}, 
    "Aisha": {"eyes": "31545e", "hair": "3b2306", "skin": "995a25"}, 
    "Musa": {"eyes": "222d42", "hair": "1f1c36", "skin": "ebd1c5"},  
    "Tecna": {"eyes": "176e73", "hair": "852b72", "skin": "e8ccc1"}  
}

#pesi per ciascun tratto
WEIGHTS = {
    "hair": 0.60,  # I capelli contano al 60%
    "eyes": 0.20,  # Gli occhi al 20%
    "skin": 0.20   # La pelle al 20%
}

def hex_to_rgb(hex_code):
    """Converte un codice esadecimale in una tupla RGB."""
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

"""
def calculate_color_distance(color1, color2):
    #Calcola la Distanza Euclidea tra due colori RGB.
    return math.sqrt(
        (color1[0] - color2[0])**2 + 
        (color1[1] - color2[1])**2 + 
        (color1[2] - color2[2])**2
    )
"""
def calculate_color_distance(color1_rgb, color2_rgb):
    """Calcola la distanza tra due colori basandosi QUASI SOLO sulla tinta (Hue)."""
    
    h1, s1, v1 = colorsys.rgb_to_hsv(color1_rgb[0]/255, color1_rgb[1]/255, color1_rgb[2]/255)
    h2, s2, v2 = colorsys.rgb_to_hsv(color2_rgb[0]/255, color2_rgb[1]/255, color2_rgb[2]/255)

    dh = min(abs(h1 - h2), 1.0 - abs(h1 - h2)) * 2.0 
    ds = abs(s1 - s2)
    dv = abs(v1 - v2)

    # IL NUOVO BILANCIAMENTO: 
    # Tinta al 90% (ci interessa di che colore è)
    # Saturazione e Luminosità al 5% (ignoriamo se è sbiadito o in ombra)
    distance = math.sqrt((dh * 0.90)**2 + (ds * 0.05)**2 + (dv * 0.05)**2)
    
    return distance * 400


def calculate_winx_match(eye_color, hair_color, skin_color):
    print("\n--- AVVIO CALCOLO MAGIC WINX ---")
    print(f"I tuoi colori -> Occhi: {eye_color}, Capelli: {hair_color}, Pelle: {skin_color}")
    
    best_match = None
    min_total_distance = float('inf')
    results = {}
    
    MAX_POSSIBLE_DISTANCE = 365.0

    for winx_name, profile in WINX_PROFILES_HEX.items():
        # Convertiamo i colori della Winx in RGB
        winx_eyes_rgb = hex_to_rgb(profile["eyes"])
        winx_hair_rgb = hex_to_rgb(profile["hair"])
        winx_skin_rgb = hex_to_rgb(profile["skin"])
        
        # Calcoliamo le distanze parziali
        dist_eyes = calculate_color_distance(eye_color, winx_eyes_rgb)
        dist_hair = calculate_color_distance(hair_color, winx_hair_rgb)
        dist_skin = calculate_color_distance(skin_color, winx_skin_rgb)
        
        # Distanza totale
        total_distance = (
            (dist_eyes * WEIGHTS["eyes"]) + 
            (dist_hair * WEIGHTS["hair"]) + 
            (dist_skin * WEIGHTS["skin"])
        )
        
        # Percentuale di affinità
        affinity_percentage = max(0, 100 * (1 - (total_distance / MAX_POSSIBLE_DISTANCE)))
        results[winx_name] = affinity_percentage
        
        if total_distance < min_total_distance:
            min_total_distance = total_distance
            best_match = winx_name

    sorted_results = sorted(results.items(), key=lambda item: item[1], reverse=True)
    
    print("\n--- CLASSIFICA AFFINITÀ ---")
    for winx, perc in sorted_results:
        print(f"{winx}: {perc:.1f}%")
        
    print(f"\nRISULTATO FINALE: Sei {best_match}!")
    return best_match, sorted_results[0][1]