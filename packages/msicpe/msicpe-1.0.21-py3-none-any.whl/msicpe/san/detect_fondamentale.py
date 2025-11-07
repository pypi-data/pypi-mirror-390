import numpy as np
from .detect_pics import detect_pics

def detect_fondamentale(spectre, nu, threshold=0.25):
    """Fonction permettant de déterminer la fréquence fondamentale d'un signal à partir de son spectre.
    Args:
        spectre (ndarray): spectre du signal
        nu (ndarray): vecteur des fréquences associées au spectre
        threshold (float, optional): seuil pour la détection de la fréquence fondamentale. Default à 0.25.
    Returns:
        nu_fond (float): fréquence fondamentale détectée en Hz
    """
    Ve = nu[-1]*2  # *2 because only half spectrum is used
    spectrum_thresholded = np.abs(np.diff(spectre, n=4, prepend=[0,0], append=[0,0]))
    spectrum_thresholded[spectrum_thresholded < threshold] = 0
    ind_fond = np.where(spectrum_thresholded > 0)[0][0]
    nu = np.arange(len(spectre)) * Ve / (2*len(spectre))  # Assuming spectrum is half the FFT length
    nu_fond = nu[ind_fond]
    nu_fond,_ = detect_pics(spectre, [nu_fond], nu)  # To verify the presence of harmonics
    return nu_fond[0]

