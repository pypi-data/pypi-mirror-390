import numpy as np

def next_pow2_of(n):
    """
    Calcule la plus petite puissance de 2 supérieure ou égale à un nombre donné.

    Cette fonction renvoie le plus petit entier de la forme 2^k tel que 2^k >= n.
    Elle est utile, par exemple, pour le dimensionnement d'algorithmes FFT ou
    pour des opérations nécessitant des tailles en puissances de deux.

    Parameters
    ----------
    n : int ou float
        Le nombre d’entrée (doit être strictement positif).

    Returns
    --------
    int
        La plus petite puissance de 2 supérieure ou égale à `n`.

    Examples
    --------
    >>> next_pow2_of(5)
    8
    >>> next_pow2_of(16)
    16
    >>> next_pow2_of(1.3)
    2

    Notes
    -----
    - Si `n` est inférieur ou égal à 0, le résultat n’est pas défini (erreur mathématique).
    - Utilise la fonction `np.log2` et l’arrondi supérieur `np.ceil` pour déterminer l’exposant.

    """
    return 2**int(np.ceil(np.log2(n)))