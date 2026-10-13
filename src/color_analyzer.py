import cv2
import numpy as np
from sklearn.cluster import KMeans

def get_dominant_color(bgr_image, mask=None):
    # estrae il colore dominante usando il clustering K-Means
    # converte da BGR (OpenCV) a RGB (per il confronto Winx)
    rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
    
    # se c'è una maschera, applica un operatore AND
    if mask is not None:
        masked_image = cv2.bitwise_and(rgb_image, rgb_image, mask=mask)
        # estrae solo i pixel validi (non neri)
        pixels = masked_image[mask == 255]
    else:
        # se è un semplice ritaglio (crop), prende tutti i pixel
        pixels = rgb_image.reshape(-1, 3)
    
    # se non ci sono pixel validi, restituisce nero come fallback
    if len(pixels) == 0:
        return (0, 0, 0)
        
    # applica il K-Means Clustering con K=1 (cerca il centroide principale)
    kmeans = KMeans(n_clusters=1, n_init=5)
    kmeans.fit(pixels)
    
    dominant_color = kmeans.cluster_centers_[0]
    return (int(dominant_color[0]), int(dominant_color[1]), int(dominant_color[2]))