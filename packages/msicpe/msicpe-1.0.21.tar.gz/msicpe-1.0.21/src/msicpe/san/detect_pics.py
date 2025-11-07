import numpy as np

def detect_pics(spectre, freq_list, nu):
    """Fonction permettant de détecter les pics harmoniques dans un spectre.
    Args:
        spectre (ndarray): spectre du signal
        freq_list (list): liste des fréquences harmoniques à détecter
        nu (ndarray): vecteur des fréquences associées au spectre
    Returns:
        freq_peaks (ndarray): fréquences des pics détectés
        peak_amplitudes (ndarray): amplitudes des pics détectés
    """
    ind_peak = []
    Ve = nu[-1]*2  # *2 because only half spectrum is used
    ind_fond = int(freq_list[0] * len(spectre)*2 / Ve) # *2 because only half spectrum is used
    for k in range(1, len(freq_list)+1):
        search_range = range(k*ind_fond - 10, k*ind_fond + 11)
        ind_peak.append(search_range[np.argmax(spectre[search_range])])
    peak_amplitudes = spectre[ind_peak]
    freq_peaks = np.array(ind_peak) * Ve / (2*len(spectre))
    
    return freq_peaks, peak_amplitudes