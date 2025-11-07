"""
Geometric Transformation Module
Provides functions for various geometric transformations including 
translation, rotation, scaling, reflection, and shearing.
"""

from skimage import data, transform, color
import matplotlib.pyplot as plt
import numpy as np


def translate_image(img, tx=50, ty=30):
    """
    Translate (shift) an image.
    
    Args:
        img: Input image
        tx: Translation in x direction (pixels)
        ty: Translation in y direction (pixels)
    
    Returns:
        Translated image
    """
    tform = transform.AffineTransform(translation=(tx, ty))
    return transform.warp(img, tform)


def rotate_image(img, angle_deg=45):
    """
    Rotate an image by specified angle.
    
    Args:
        img: Input image
        angle_deg: Rotation angle in degrees
    
    Returns:
        Rotated image
    """
    angle_rad = np.deg2rad(angle_deg)
    tform = transform.AffineTransform(rotation=angle_rad)
    return transform.warp(img, tform)


def scale_image(img, scale_x=0.5, scale_y=0.5):
    """
    Scale an image.
    
    Args:
        img: Input image
        scale_x: Scale factor in x direction
        scale_y: Scale factor in y direction
    
    Returns:
        Scaled image
    """
    tform = transform.AffineTransform(scale=(scale_x, scale_y))
    return transform.warp(img, tform)


def reflect_image(img, horizontal=True):
    """
    Reflect (flip) an image.
    
    Args:
        img: Input image
        horizontal: If True, flip horizontally; else vertically
    
    Returns:
        Reflected image
    """
    if horizontal:
        tform = transform.AffineTransform(
            scale=(-1, 1), 
            translation=(img.shape[1], 0)
        )
    else:
        tform = transform.AffineTransform(
            scale=(1, -1), 
            translation=(0, img.shape[0])
        )
    return transform.warp(img, tform)


def shear_image(img, shear_angle_deg=20):
    """
    Shear an image.
    
    Args:
        img: Input image
        shear_angle_deg: Shear angle in degrees
    
    Returns:
        Sheared image
    """
    shear_rad = np.deg2rad(shear_angle_deg)
    tform = transform.AffineTransform(shear=shear_rad)
    return transform.warp(img, tform)


def apply_all_transforms(img=None, display=True):
    """
    Apply all geometric transformations and display results.
    
    Args:
        img: Input image (if None, loads sample image)
        display: Whether to display the results
    
    Returns:
        Dictionary containing all transformed images
    """
    if img is None:
        img = data.astronaut()
    
    results = {
        'original': img,
        'translated': translate_image(img),
        'rotated': rotate_image(img),
        'scaled': scale_image(img),
        'reflected': reflect_image(img),
        'sheared': shear_image(img)
    }
    
    if display:
        plt.figure(figsize=(12, 8))
        
        titles = ['Original', 'Translated', 'Rotated', 'Scaled', 'Reflected', 'Sheared']
        images = [results[key] for key in ['original', 'translated', 'rotated', 
                                            'scaled', 'reflected', 'sheared']]
        
        for i, (image, title) in enumerate(zip(images, titles)):
            plt.subplot(2, 3, i+1)
            plt.imshow(image)
            plt.title(title)
            plt.axis('off')
        
        plt.tight_layout()
        plt.show()
    
    return results


def demo():
    """Run a demonstration of geometric transformations."""
    import inspect
    print("\n" + "="*80)
    print("MODULE 2: GEOMETRIC TRANSFORMATIONS - SOURCE CODE")
    print("="*80)
    
    # Try to get module source (works in .py files)
    try:
        module = inspect.getmodule(inspect.currentframe())
        if module is not None:
            print(inspect.getsource(module))
        else:
            # Fallback for Jupyter notebooks - print individual functions
            functions_to_show = [
                translate_image, rotate_image, scale_image,
                reflect_image, shear_image, apply_all_transforms, demo
            ]
            for func in functions_to_show:
                print(inspect.getsource(func))
    except Exception as e:
        print(f"Note: Could not display full source code: {e}")
        print("This is expected in some environments like Jupyter notebooks.")
    
    print("="*80)
    print("\n=== EXECUTING CODE - Geometric Transformations Demo ===\n")
    img = data.astronaut()
    print(f"Loaded image with shape: {img.shape}")
    apply_all_transforms(img)


if __name__ == "__main__":
    demo()
