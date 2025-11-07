"""
Image Handling and Processing Module
Provides functions for basic image operations like loading, resizing, 
color conversion, and filtering.
"""

from skimage import data, io, color, transform, filters
import matplotlib.pyplot as plt
import numpy as np


def load_sample_image():
    """Load a sample astronaut image."""
    return data.astronaut()


def display_image(img, title="Image"):
    """Display an image with matplotlib."""
    plt.imshow(img)
    plt.title(title)
    plt.axis('off')
    plt.show()


def resize_image(img, output_shape=(200, 200)):
    """
    Resize an image to specified dimensions.
    
    Args:
        img: Input image
        output_shape: Tuple of (height, width)
    
    Returns:
        Resized image (float in range [0, 1])
    """
    return transform.resize(img, output_shape)


def convert_to_grayscale(img):
    """
    Convert RGB image to grayscale.
    
    Args:
        img: Input RGB image
    
    Returns:
        Grayscale image (float in range [0, 1])
    """
    return color.rgb2gray(img)


def apply_gaussian_blur(img, sigma=2):
    """
    Apply Gaussian blur to an image.
    
    Args:
        img: Input image
        sigma: Standard deviation for Gaussian kernel
    
    Returns:
        Blurred image
    """
    if len(img.shape) == 3:  # Color image
        return filters.gaussian(img, sigma=sigma, channel_axis=-1)
    else:  # Grayscale
        return filters.gaussian(img, sigma=sigma)


def process_and_display(img=None, show_resize=True, show_gray=True, show_blur=True):
    """
    Complete image processing pipeline with visualization.
    
    Args:
        img: Input image (if None, loads sample image)
        show_resize: Whether to show resized image
        show_gray: Whether to show grayscale conversion
        show_blur: Whether to show blurred image
    """
    if img is None:
        img = load_sample_image()
    
    results = []
    titles = ["Original"]
    images = [img]
    
    if show_resize:
        img_resized = resize_image(img)
        images.append(img_resized)
        titles.append("Resized")
    
    if show_gray:
        img_gray = convert_to_grayscale(img)
        images.append(img_gray)
        titles.append("Grayscale")
    
    if show_blur:
        img_blur = apply_gaussian_blur(img)
        images.append(img_blur)
        titles.append("Blurred")
    
    # Display all images
    n = len(images)
    plt.figure(figsize=(4*n, 4))
    
    for i, (image, title) in enumerate(zip(images, titles)):
        plt.subplot(1, n, i+1)
        if title == "Grayscale":
            plt.imshow(image, cmap='gray')
        else:
            plt.imshow(image)
        plt.title(title)
        plt.axis('off')
    
    plt.tight_layout()
    plt.show()
    
    return images


def demo():
    """Run a demonstration of image processing functions."""
    import inspect
    print("\n" + "="*80)
    print("MODULE 1: IMAGE PROCESSING - SOURCE CODE")
    print("="*80)
    print(inspect.getsource(inspect.getmodule(inspect.currentframe())))
    print("="*80)
    print("\n=== EXECUTING CODE - Image Processing Demo ===\n")
    img = load_sample_image()
    print(f"Loaded image with shape: {img.shape}")
    process_and_display(img)


if __name__ == "__main__":
    demo()
