"""
Homography Matrix Computation Module
Provides functions to compute and apply homography transformations.
"""

import numpy as np
import matplotlib.pyplot as plt
from skimage import data, transform, color


def compute_homography(src_points, dst_points):
    """
    Compute homography matrix from source to destination points.
    
    Args:
        src_points: Source points (Nx2 array)
        dst_points: Destination points (Nx2 array)
    
    Returns:
        ProjectiveTransform object containing the homography matrix
    """
    tform = transform.ProjectiveTransform()
    tform.estimate(src_points, dst_points)
    return tform


def apply_homography(img, tform, output_shape=None):
    """
    Apply homography transformation to an image.
    
    Args:
        img: Input image
        tform: ProjectiveTransform object
        output_shape: Output image shape (if None, uses input shape)
    
    Returns:
        Warped image
    """
    if output_shape is None:
        output_shape = img.shape
    return transform.warp(img, tform, output_shape=output_shape)


def compute_and_apply_homography(img=None, src=None, dst=None, display=True):
    """
    Complete pipeline: compute homography and apply to image.
    
    Args:
        img: Input image (if None, loads sample image)
        src: Source points (if None, uses default)
        dst: Destination points (if None, uses default)
        display: Whether to display results
    
    Returns:
        Tuple of (warped_image, homography_matrix)
    """
    if img is None:
        img = data.astronaut()
    
    # Default source and destination points
    if src is None:
        src = np.array([[50, 50], [200, 50], [50, 200], [200, 200]], dtype=np.float32)
    
    if dst is None:
        dst = np.array([[10, 100], [220, 50], [80, 250], [250, 220]], dtype=np.float32)
    
    # Compute homography
    tform = compute_homography(src, dst)
    
    # Apply transformation
    img_warped = apply_homography(img, tform)
    
    if display:
        plt.figure(figsize=(10, 5))
        
        plt.subplot(1, 2, 1)
        plt.imshow(img)
        plt.title("Original")
        plt.axis('off')
        
        plt.subplot(1, 2, 2)
        plt.imshow(img_warped)
        plt.title("Warped Image")
        plt.axis('off')
        
        plt.tight_layout()
        plt.show()
        
        print("Homography Matrix:")
        print(tform.params)
    
    return img_warped, tform.params


def demo():
    """Run a demonstration of homography computation."""
    import inspect
    print("\n" + "="*80)
    print("MODULE 3: HOMOGRAPHY COMPUTATION - SOURCE CODE")
    print("="*80)
    print(inspect.getsource(inspect.getmodule(inspect.currentframe())))
    print("="*80)
    print("\n=== EXECUTING CODE - Homography Computation Demo ===\n")
    img = data.astronaut()
    print(f"Loaded image with shape: {img.shape}")
    compute_and_apply_homography(img)


if __name__ == "__main__":
    demo()
