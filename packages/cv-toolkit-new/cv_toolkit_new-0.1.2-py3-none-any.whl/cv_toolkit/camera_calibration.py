"""
Camera Calibration Module
Provides functions for camera calibration and image undistortion.
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt


def create_grid_image(size=400):
    """
    Create a grid pattern image for demonstrating distortion.
    
    Args:
        size: Size of the square image
    
    Returns:
        Grid pattern image
    """
    img = np.ones((size, size), dtype=np.uint8) * 255
    for i in range(0, size, 40):
        cv2.line(img, (i, 0), (i, size), 0, 1)
        cv2.line(img, (0, i), (size, i), 0, 1)
    cv2.putText(img, "Grid Pattern", (120, 190), cv2.FONT_HERSHEY_SIMPLEX, 1, 0, 2)
    return img


def apply_barrel_distortion(img, k1=0.3, k2=0.1):
    """
    Apply barrel distortion to an image.
    
    Args:
        img: Input image
        k1: First radial distortion coefficient
        k2: Second radial distortion coefficient
    
    Returns:
        Tuple of (distorted_image, camera_matrix, distortion_coefficients)
    """
    h, w = img.shape[:2]
    
    mtx = np.array([
        [w/2, 0, w/2],
        [0, w/2, h/2],
        [0, 0, 1]
    ], dtype=np.float32)
    
    dist_coeffs = np.array([k1, k2, 0, 0], dtype=np.float32)
    
    distorted = cv2.undistort(img, mtx, dist_coeffs)
    return distorted, mtx, dist_coeffs


def undistort_image(img, camera_matrix, dist_coeffs):
    """
    Undistort an image using camera calibration parameters.
    
    Args:
        img: Input distorted image
        camera_matrix: Camera matrix from calibration
        dist_coeffs: Distortion coefficients from calibration
    
    Returns:
        Undistorted image
    """
    h, w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(
        camera_matrix, dist_coeffs, (w, h), 1, (w, h)
    )
    undistorted = cv2.undistort(img, camera_matrix, dist_coeffs, None, newcameramtx)
    return undistorted


def camera_calibration_demo(display=True, save_results=False):
    """
    Complete camera calibration demonstration.
    Shows original, distorted, and undistorted images.
    
    Args:
        display: Whether to display results
        save_results: Whether to save output images
    
    Returns:
        Tuple of (camera_matrix, dist_coeffs, undistorted_image)
    """
    h, w = 400, 400
    img = create_grid_image(400)
    
    print("Original image shape:", img.shape)
    
    # Apply barrel distortion
    distorted, mtx, dist = apply_barrel_distortion(img, k1=0.3, k2=0.1)
    
    print("Camera Matrix:\n", mtx)
    print("Distortion Coefficients:\n", dist)
    
    # Undistort the image
    undistorted = undistort_image(distorted, mtx, dist)
    
    if display:
        plt.figure(figsize=(15, 5))
        
        plt.subplot(1, 3, 1)
        plt.imshow(img, cmap='gray')
        plt.title("Original (No Distortion)")
        plt.axis('off')
        
        plt.subplot(1, 3, 2)
        plt.imshow(distorted, cmap='gray')
        plt.title("With Barrel Distortion (Curved)")
        plt.axis('off')
        
        plt.subplot(1, 3, 3)
        plt.imshow(undistorted, cmap='gray')
        plt.title("Undistorted (Corrected)")
        plt.axis('off')
        
        plt.tight_layout()
        
        if save_results:
            plt.savefig("camera_calibration_comparison.png", dpi=100, bbox_inches='tight')
            print("Saved: camera_calibration_comparison.png")
        
        plt.show()
    
    return mtx, dist, undistorted


def demo():
    """Run a demonstration of camera calibration."""
    import inspect
    print("\n" + "="*80)
    print("MODULE 5: CAMERA CALIBRATION - SOURCE CODE")
    print("="*80)
    
    # Try to get module source (works in .py files)
    try:
        module = inspect.getmodule(inspect.currentframe())
        if module is not None:
            print(inspect.getsource(module))
        else:
            # Fallback for Jupyter notebooks - print individual functions
            functions_to_show = [
                create_grid_image, apply_barrel_distortion,
                undistort_image, camera_calibration_demo, demo
            ]
            for func in functions_to_show:
                print(inspect.getsource(func))
    except Exception as e:
        print(f"Note: Could not display full source code: {e}")
        print("This is expected in some environments like Jupyter notebooks.")
    
    print("="*80)
    print("\n=== EXECUTING CODE - Camera Calibration Demo ===\n")
    camera_calibration_demo(display=True, save_results=True)


if __name__ == "__main__":
    demo()
