import cv2
import numpy as np
import matplotlib.pyplot as plt

def load_image(image_path):
    """Loads an image in grayscale."""
    return cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

def apply_averaging_filter(image, kernel_size):
    return cv2.blur(image, (kernel_size, kernel_size))

def apply_gaussian_filter(image, kernel_size):
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)

def apply_average_filter(image):
    kernel = np.ones((3, 3), np.float32) / 9
    return cv2.filter2D(image, -1, kernel)

def apply_weighted_average_filter(image):
    kernel = np.array([[1, 2, 1],
                       [2, 4, 2],
                       [1, 2, 1]], np.float32)
    kernel /= kernel.sum()
    return cv2.filter2D(image, -1, kernel)

def apply_median_filter(image, kernel_size):
    return cv2.medianBlur(image, kernel_size)

def display_image(original, filtered, title):
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.imshow(original, cmap='gray')
    plt.title("Original")
    plt.axis("off")

    plt.subplot(1, 2, 2)
    plt.imshow(filtered, cmap='gray')
    plt.title(title)
    plt.axis("off")

    plt.tight_layout()
    plt.show()

def apply_filter(image_path, filter_type="averaging", kernel_size=3):
    """
    Apply a selected filter to an image.
    
    Parameters:
        image_path (str): Path to the image.
        filter_type (str): One of ['averaging', 'gaussian', 'average', 'weighted', 'median'].
        kernel_size (int): Kernel size (odd number like 3, 5, 7).
    """
    image = load_image(image_path)
    if image is None:
        raise ValueError("Could not load image. Check the path.")

    filter_type = filter_type.lower()

    if filter_type == "averaging":
        filtered = apply_averaging_filter(image, kernel_size)
    elif filter_type == "gaussian":
        filtered = apply_gaussian_filter(image, kernel_size)
    elif filter_type == "average":
        filtered = apply_average_filter(image)
    elif filter_type == "weighted":
        filtered = apply_weighted_average_filter(image)
    elif filter_type == "median":
        filtered = apply_median_filter(image, kernel_size)
    else:
        raise ValueError(f"Unknown filter type '{filter_type}'")

    display_image(image, filtered, f"{filter_type.capitalize()} Filter ({kernel_size}x{kernel_size})")
