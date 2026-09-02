import math
import colorsys
import config

def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def calculate_color_distance(color1_rgb, color2_rgb):

    h1, s1, v1 = colorsys.rgb_to_hsv(color1_rgb[0]/255, color1_rgb[1]/255, color1_rgb[2]/255)
    h2, s2, v2 = colorsys.rgb_to_hsv(color2_rgb[0]/255, color2_rgb[1]/255, color2_rgb[2]/255)

    dh = min(abs(h1 - h2), 1.0 - abs(h1 - h2)) * 2.0 
    ds = abs(s1 - s2)
    dv = abs(v1 - v2)

    distance = math.sqrt((dh * 0.50)**2 + (ds * 0.25)**2 + (dv * 0.25)**2)
    return distance * 400

def calculate_winx_match(eye_color, hair_color, skin_color):
    print("\n--- AVVIO CALCOLO MAGIC WINX ---")
    print(f"I tuoi colori -> Occhi: {eye_color}, Capelli: {hair_color}, Pelle: {skin_color}")
    
    best_match = None
    min_total_distance = float('inf')
    results = [] # Ora usiamo una lista per immagazzinare tuple con i dettagli
    
    for winx_name, profile in config.WINX_PROFILES_HEX.items():
        winx_eyes_rgb = hex_to_rgb(profile["eyes"])
        winx_hair_rgb = hex_to_rgb(profile["hair"])
        winx_skin_rgb = hex_to_rgb(profile["skin"])
        
        dist_eyes = calculate_color_distance(eye_color, winx_eyes_rgb)
        dist_hair = calculate_color_distance(hair_color, winx_hair_rgb)
        dist_skin = calculate_color_distance(skin_color, winx_skin_rgb)
        
        # Distanza totale (pesata)
        total_distance = (
            (dist_eyes * config.WEIGHTS["eyes"]) + 
            (dist_hair * config.WEIGHTS["hair"]) + 
            (dist_skin * config.WEIGHTS["skin"])
        )
        
        # Percentuale complessiva
        affinity_percentage = max(0, 100 * (1 - (total_distance / config.MAX_POSSIBLE_DISTANCE)))
        
        # Percentuali singole non pesate (per i dettagli a schermo)
        perc_eyes = max(0, 100 * (1 - (dist_eyes / config.MAX_POSSIBLE_DISTANCE)))
        perc_hair = max(0, 100 * (1 - (dist_hair / config.MAX_POSSIBLE_DISTANCE)))
        perc_skin = max(0, 100 * (1 - (dist_skin / config.MAX_POSSIBLE_DISTANCE)))
        
        # Creiamo un dizionario con i dettagli
        details = {"eyes": perc_eyes, "hair": perc_hair, "skin": perc_skin}
        
        # Aggiungiamo alla lista: Nome, % Totale, Dettagli
        results.append((winx_name, affinity_percentage, details))
        
        if total_distance < min_total_distance:
            min_total_distance = total_distance
            best_match = winx_name

    # Ordiniamo in base al secondo elemento (la percentuale totale)
    sorted_results = sorted(results, key=lambda item: item[1], reverse=True)
    
    print("\n--- CLASSIFICA AFFINITÀ ---")
    for winx, perc, details in sorted_results:
        print(f"{winx}: {perc:.1f}% (Occhi: {details['eyes']:.0f}%, Capelli: {details['hair']:.0f}%, Pelle: {details['skin']:.0f}%)")
        
    print(f"\nRISULTATO FINALE: Sei {best_match}!")
    
    return best_match, sorted_results[0][1], sorted_results