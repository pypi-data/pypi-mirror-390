import numpy as np
import cv2

def bweuler(im: np.ndarray) -> int:
    """
    Calcule le nombre d'Euler number.
    
    Le nombre d'Euler est une mesure de la topologie de l'image.
    Il est défini comme le nombre total d'objets (composantes 
    connexes) dans l'image moins le nombre de trous présents 
    dans ces objets.
    
    Parameters
    ----------
    im : np.ndarray
        Image d'entrée à analyser

    Returns
    --------
    euler : int
        Nombre d'Euler de l'image
    """
    # from: https://gist.github.com/Nico-Curti/136bffef4546504551beacd8b52b2df1
    
    # check binary mask
    assert np.unique(im).size <= 2
    im = im.astype(np.uint8)

    # get the number of connected components, aka objects
    ncomp, *_ = cv2.connectedComponents(im)
    
    # invert the image to get the holes
    not_image = cv2.bitwise_not(im)
    
    # get the number of connected components, aka holes
    # NOTE: In the image inversion the background is
    # interpreted as hole and therefore we need to
    # subtract 1 to the number of obtained holes
    nholes, *_ = cv2.connectedComponents(not_image)

    return ncomp - (nholes-1)