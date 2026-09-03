import cv2
import numpy as np
from sklearn.cluster import KMeans

def get_dominant_color(bgr_image, mask=None):
    """Estrae il colore dominante usando il clustering K-Means."""
    # Convertiamo da BGR (OpenCV) a RGB (per il confronto Winx)
    rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
    
    # Se c'è una maschera, applichiamo un operatore bit-wise AND
    if mask is not None:
        masked_image = cv2.bitwise_and(rgb_image, rgb_image, mask=mask)
        # Estraiamo solo i pixel validi (non neri)
        pixels = masked_image[mask == 255]
    else:
        # Se è un semplice ritaglio (crop), prendiamo tutti i pixel
        pixels = rgb_image.reshape(-1, 3)
    
    # Se non ci sono pixel validi, restituiamo nero come fallback
    if len(pixels) == 0:
        return (0, 0, 0)
        
    # Applichiamo il K-Means Clustering con K=1 (cerchiamo il centroide principale)
    kmeans = KMeans(n_clusters=1, n_init=5)
    kmeans.fit(pixels)
    
    dominant_color = kmeans.cluster_centers_[0]
    return (int(dominant_color[0]), int(dominant_color[1]), int(dominant_color[2]))