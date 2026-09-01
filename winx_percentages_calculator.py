import math
import colorsys
import config

def hex_to_rgb(hex_code):
    """Converte un codice esadecimale in una tupla RGB."""
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def calculate_color_distance(color1_rgb, color2_rgb):
    """Calcola la distanza tra due colori basandosi QUASI SOLO sulla tinta (Hue)."""
    h1, s1, v1 = colorsys.rgb_to_hsv(color1_rgb[0]/255, color1_rgb[1]/255, color1_rgb[2]/255)
    h2, s2, v2 = colorsys.rgb_to_hsv(color2_rgb[0]/255, color2_rgb[1]/255, color2_rgb[2]/255)

    dh = min(abs(h1 - h2), 1.0 - abs(h1 - h2)) * 2.0 
    ds = abs(s1 - s2)
    dv = abs(v1 - v2)

    distance = math.sqrt((dh * 0.90)**2 + (ds * 0.05)**2 + (dv * 0.05)**2)
    return distance * 400

def calculate_winx_match(eye_color, hair_color, skin_color):
    print("\n--- AVVIO CALCOLO MAGIC WINX ---")
    print(f"I tuoi colori -> Occhi: {eye_color}, Capelli: {hair_color}, Pelle: {skin_color}")
    
    best_match = None
    min_total_distance = float('inf')
    results = {}
    
    for winx_name, profile in config.WINX_PROFILES_HEX.items():
        winx_eyes_rgb = hex_to_rgb(profile["eyes"])
        winx_hair_rgb = hex_to_rgb(profile["hair"])
        winx_skin_rgb = hex_to_rgb(profile["skin"])
        
        dist_eyes = calculate_color_distance(eye_color, winx_eyes_rgb)
        dist_hair = calculate_color_distance(hair_color, winx_hair_rgb)
        dist_skin = calculate_color_distance(skin_color, winx_skin_rgb)
        
        total_distance = (
            (dist_eyes * config.WEIGHTS["eyes"]) + 
            (dist_hair * config.WEIGHTS["hair"]) + 
            (dist_skin * config.WEIGHTS["skin"])
        )
        
        affinity_percentage = max(0, 100 * (1 - (total_distance / config.MAX_POSSIBLE_DISTANCE)))
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