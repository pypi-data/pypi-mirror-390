import numpy as np

def trans_fourier(signal, temps):
    """Fonction permettant de calculer la transformée de Fourier d'un signal.
    Args:
        signal (ndarray): signal temporel à analyser
        temps (ndarray): vecteur temps associé au signal
    Returns:
        nu (ndarray): vecteur des fréquences (positives)
        S (ndarray): transformée de Fourier du signal
    """
    N = len(signal)
    S = np.fft.fft(signal.flatten(), n=N)
    Te = temps[1] - temps[0]
    nu = np.arange(N) / Te / N
    
    return nu[:N//2], S[:N//2]