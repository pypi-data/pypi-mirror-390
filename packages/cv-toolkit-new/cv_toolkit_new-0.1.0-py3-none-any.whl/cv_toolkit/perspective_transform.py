"""
Perspective Transformation Module
Provides functions for perspective transformations (a specific type of projective transform).
"""

import numpy as np
import matplotlib.pyplot as plt
from skimage import data, transform, color


def compute_perspective_transform(src_points, dst_points):
    """
    Compute perspective transformation matrix.
    
    Args:
        src_points: Source points (4x2 array for corners)
        dst_points: Destination points (4x2 array for corners)
    
    Returns:
        ProjectiveTransform object
    """
    tform = transform.ProjectiveTransform()
    tform.estimate(src_points, dst_points)
    return tform


def apply_perspective_transform(img, tform, output_shape=None):
    """
    Apply perspective transformation to an image.
    
    Args:
        img: Input image
        tform: ProjectiveTransform object
        output_shape: Output image shape (if None, uses input shape)
    
    Returns:
        Transformed image
    """
    if output_shape is None:
        output_shape = img.shape
    return transform.warp(img, tform, output_shape=output_shape)


def perspective_transform_pipeline(img=None, src=None, dst=None, display=True):
    """
    Complete perspective transformation pipeline.
    
    Args:
        img: Input image (if None, loads sample image)
        src: Source corner points (if None, uses default)
        dst: Destination corner points (if None, uses default)
        display: Whether to display results
    
    Returns:
        Tuple of (transformed_image, transformation_matrix)
    """
    if img is None:
        img = data.astronaut()
    
    # Default corners
    if src is None:
        src = np.array([[50, 50], [200, 50], [50, 200], [200, 200]], dtype=np.float32)
    
    if dst is None:
        dst = np.array([[10, 100], [220, 50], [80, 250], [250, 220]], dtype=np.float32)
    
    # Compute and apply transformation
    tform = compute_perspective_transform(src, dst)
    img_transformed = apply_perspective_transform(img, tform)
    
    if display:
        plt.figure(figsize=(10, 5))
        
        plt.subplot(1, 2, 1)
        plt.imshow(img)
        plt.title("Original Image")
        plt.axis('off')
        
        plt.subplot(1, 2, 2)
        plt.imshow(img_transformed)
        plt.title("Perspective Transformed Image")
        plt.axis('off')
        
        plt.tight_layout()
        plt.show()
        
        print("Perspective Transformation Matrix:")
        print(tform.params)
    
    return img_transformed, tform.params


def demo():
    """Run a demonstration of perspective transformation."""
    import inspect
    print("\n" + "="*80)
    print("MODULE 4: PERSPECTIVE TRANSFORMATION - SOURCE CODE")
    print("="*80)
    print(inspect.getsource(inspect.getmodule(inspect.currentframe())))
    print("="*80)
    print("\n=== EXECUTING CODE - Perspective Transformation Demo ===\n")
    img = data.astronaut()
    print(f"Loaded image with shape: {img.shape}")
    perspective_transform_pipeline(img)


if __name__ == "__main__":
    demo()
