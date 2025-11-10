import cv2
import numpy as np
import matplotlib.pyplot as plt

def augment_image(img):
    augmented = []

    augmented.append(("original", img))

    flipped = cv2.flip(img, 1)
    augmented.append(("flipped", flipped))

    kernel_sharp = np.array([[0, -1, 0],
                             [-1, 5, -1],
                             [0, -1, 0]])
    sharpened = cv2.filter2D(img, -1, kernel_sharp)
    augmented.append(("sharpened", sharpened))

    gaussian = cv2.GaussianBlur(img, (5, 5), 0)
    augmented.append(("gaussian_blur", gaussian))

    median = cv2.medianBlur(img, 5)
    augmented.append(("median_blur", median))

    kernel_highpass = np.array([[-1, -1, -1],
                                [-1,  9, -1],
                                [-1, -1, -1]])
    highpass = cv2.filter2D(img, -1, kernel_highpass)
    augmented.append(("highpass_filter", highpass))

    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(img, kernel, iterations=1)
    augmented.append(("dilated", dilated))

    eroded = cv2.erode(img, kernel, iterations=1)
    augmented.append(("eroded", eroded))

    return augmented

def display_images(named_images):
    """
    named_images must be a list of tuples: (name, image)
    """
    for name, img in named_images:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        plt.figure()
        plt.title(name)
        plt.imshow(img_rgb)
        plt.axis("off")
        plt.show()

