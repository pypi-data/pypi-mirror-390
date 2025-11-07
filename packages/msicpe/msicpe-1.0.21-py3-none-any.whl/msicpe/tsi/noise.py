import numpy as np
import cv2


def add_gaussian_noise(img,sigma=.05):
    max_dyn = 2**int(np.ceil(np.log2(np.max(img))))
    if max_dyn > 1:
        max_dyn -= 1
    
    noisy = img.astype(float) + sigma*np.random.standard_normal((img.shape))
    noisy -= np.min(noisy)
    noisy = noisy/np.max(noisy)*max_dyn
    
    return noisy.astype(type(img[0,0]))

def add_salt_and_pepper_noise(img,noise_percentage=.1):
    # with noise_percentage: the percentage of pixels that should contain noise
    
    
    # Determine the size of the noise based on the noise precentage
    img_size = img.size
    noise_size = int(noise_percentage*img_size)

    # Randomly select indices for adding noise
    random_indices = np.random.choice(img_size, size=noise_size)

    # Create a copy of the original image that serves as a template for the noised image
    noisy = img.copy()

    # Create a noise list with random placements of min and max values of the image pixels
    max_dyn = 2**int(np.ceil(np.log2(np.max(img))))
    if max_dyn > 1:
        max_dyn -= 1
    noise = np.random.choice([0,max_dyn], size=noise_size)

    # Replace the values of the templated noised image at random indices with the noise, to obtain the final noised image
    noisy.flat[random_indices] = noise
    
    return noisy.astype(type(img[0,0]))


def mse(im0,im1):
    return np.round(np.sum((im0.astype(float)-im1.astype(float))**2)/im0.size,3)