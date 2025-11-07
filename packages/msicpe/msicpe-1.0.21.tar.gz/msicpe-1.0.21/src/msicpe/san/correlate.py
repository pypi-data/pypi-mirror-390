import numpy as np

def correlate(x,y,D):
    """
    Calcule la fonction d'inter-corrélation de deux signaux x et y de même durée D.
   
    Parameters:
    x (array) : signal 1
    y (array) : signal 2
    D (float) : durée des signaux
   
    Returns:
    gamma_xy (array) : vecteur contenant les valeurs de la fonction d'auto-corrélation
    tau (array) : vecteur contenant les décalages
    """
 
    if len(x) != len(y):
        raise ValueError("Les signaux x et y doivent avoir la même taille")
   
    Te = D / len(x)
    gamma_xy = np.correlate(x, y, mode = 'full') * Te
    tau = np.arange(-len(x) + 1, len(x)) * Te
    return gamma_xy, tau