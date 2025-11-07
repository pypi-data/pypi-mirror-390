"""
SURF and HOG Feature Descriptor Module
Provides functions for SURF (using SIFT as alternative) and 
HOG (Histogram of Oriented Gradients) feature descriptors.
"""

import cv2
import numpy as np
from sklearn.datasets import load_sample_images


def load_sample_image():
    """
    Load a sample image from sklearn dataset.
    
    Returns:
        Sample image in BGR format
    """
    sample_images = load_sample_images()
    images = sample_images.images
    img = images[0]
    
    # Convert to uint8 if needed
    if img.dtype != np.uint8:
        img = (img * 255).astype(np.uint8)
    
    # Convert RGB to BGR for OpenCV
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    return img


def detect_surf_features(img, nfeatures=0):
    """
    Detect SURF-like features using SIFT (SURF is patented).
    
    Args:
        img: Input image (grayscale)
        nfeatures: Number of features to retain (0 = all)
    
    Returns:
        Tuple of (keypoints, descriptors)
    """
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    
    # Using SIFT as SURF alternative
    sift = cv2.SIFT_create(nfeatures=nfeatures)
    keypoints, descriptors = sift.detectAndCompute(gray, None)
    
    return keypoints, descriptors


def compute_hog_descriptor(img, win_size=(64, 128)):
    """
    Compute HOG (Histogram of Oriented Gradients) descriptor.
    
    Args:
        img: Input image (grayscale)
        win_size: Window size for HOG (width, height)
    
    Returns:
        HOG descriptor array
    """
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    
    # Resize image to standard HOG window size
    img_resized = cv2.resize(gray, win_size)
    
    # Create HOG descriptor
    hog = cv2.HOGDescriptor()
    descriptor = hog.compute(img_resized)
    
    return descriptor


def detect_people_hog(img):
    """
    Detect people in image using HOG descriptor.
    
    Args:
        img: Input image
    
    Returns:
        Tuple of (detected_boxes, img_with_detections)
    """
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    
    # Detect people
    boxes, weights = hog.detectMultiScale(img, winStride=(8, 8), padding=(8, 8), scale=1.05)
    
    # Draw bounding boxes
    img_detected = img.copy()
    for (x, y, w, h) in boxes:
        cv2.rectangle(img_detected, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    return boxes, img_detected


def surf_hog_pipeline(img=None, save_results=False):
    """
    Complete SURF and HOG feature extraction pipeline.
    
    Args:
        img: Input image (if None, loads sample)
        save_results: Whether to save outputs
    
    Returns:
        Dictionary containing SURF and HOG results
    """
    if img is None:
        print("Loading sample image...")
        img = load_sample_image()
        print("Image loaded successfully!")
    
    print(f"Image shape: {img.shape}")
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # SURF (SIFT) feature detection
    kp, des = detect_surf_features(img)
    print("SIFT Keypoints:", len(kp))
    
    # Draw keypoints
    img_kp = cv2.drawKeypoints(img, kp, None, 
                               flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    
    if save_results:
        cv2.imwrite("sift_keypoints_v2.jpg", img_kp)
        if des is not None:
            np.save("sift_descriptors_v2.npy", des)
    
    # HOG descriptor computation
    hog = compute_hog_descriptor(gray)
    if save_results:
        np.save("hog_descriptor_v2.npy", hog)
    
    print("HOG Descriptor shape:", hog.shape)
    print("Saved: sift_keypoints_v2.jpg, sift_descriptors_v2.npy, hog_descriptor_v2.npy")
    
    results = {
        'sift_keypoints': kp,
        'sift_descriptors': des,
        'sift_image': img_kp,
        'hog_descriptor': hog
    }
    
    return results


def demo():
    """Run a demonstration of SURF and HOG descriptors."""
    import inspect
    print("\n" + "="*80)
    print("MODULE 9: SURF & HOG FEATURE DESCRIPTOR - SOURCE CODE")
    print("="*80)
    
    # Try to get module source (works in .py files)
    try:
        module = inspect.getmodule(inspect.currentframe())
        if module is not None:
            print(inspect.getsource(module))
        else:
            # Fallback for Jupyter notebooks - print individual functions
            functions_to_show = [
                load_sample_image, detect_surf_features,
                compute_hog_descriptor, surf_hog_pipeline, demo
            ]
            for func in functions_to_show:
                print(inspect.getsource(func))
    except Exception as e:
        print(f"Note: Could not display full source code: {e}")
        print("This is expected in some environments like Jupyter notebooks.")
    
    print("="*80)
    print("\n=== EXECUTING CODE - SURF and HOG Feature Descriptor Demo ===\n")
    surf_hog_pipeline(save_results=True)


if __name__ == "__main__":
    demo()
