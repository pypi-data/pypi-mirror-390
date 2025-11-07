"""
SIFT Feature Descriptor Module
Provides functions for SIFT (Scale-Invariant Feature Transform) 
feature detection and description.
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


def detect_sift_features(img, nfeatures=0):
    """
    Detect SIFT keypoints and compute descriptors.
    
    Args:
        img: Input image (grayscale)
        nfeatures: Number of best features to retain (0 = all)
    
    Returns:
        Tuple of (keypoints, descriptors)
    """
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    
    sift = cv2.SIFT_create(nfeatures=nfeatures)
    keypoints, descriptors = sift.detectAndCompute(gray, None)
    
    return keypoints, descriptors


def draw_sift_keypoints(img, keypoints, flags=None):
    """
    Draw SIFT keypoints on image.
    
    Args:
        img: Input image
        keypoints: Detected keypoints
        flags: Drawing flags
    
    Returns:
        Image with keypoints drawn
    """
    if flags is None:
        flags = cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
    
    img_keypoints = cv2.drawKeypoints(img, keypoints, None, flags=flags)
    return img_keypoints


def sift_pipeline(img=None, nfeatures=0, save_results=False):
    """
    Complete SIFT feature detection pipeline.
    
    Args:
        img: Input image (if None, loads sample)
        nfeatures: Number of features to detect (0 = all)
        save_results: Whether to save output
    
    Returns:
        Tuple of (keypoints, descriptors, img_with_keypoints)
    """
    if img is None:
        print("Loading sample image...")
        img = load_sample_image()
        print("Image loaded successfully!")
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detect SIFT features
    keypoints, descriptors = detect_sift_features(img, nfeatures)
    
    print("Keypoints detected:", len(keypoints))
    if descriptors is not None:
        print("Descriptor shape:", descriptors.shape)
    
    # Draw keypoints
    img_keypoints = draw_sift_keypoints(img, keypoints)
    
    if save_results:
        cv2.imwrite("sift_keypoints_v2.jpg", img_keypoints)
        if descriptors is not None:
            np.save("sift_descriptors_v2.npy", descriptors)
        print("Saved: sift_keypoints_v2.jpg, sift_descriptors_v2.npy")
    
    return keypoints, descriptors, img_keypoints


def match_sift_features(img1, img2, ratio_threshold=0.75):
    """
    Match SIFT features between two images.
    
    Args:
        img1: First image
        img2: Second image
        ratio_threshold: Lowe's ratio test threshold
    
    Returns:
        Tuple of (good_matches, keypoints1, keypoints2)
    """
    # Detect features
    kp1, des1 = detect_sift_features(img1)
    kp2, des2 = detect_sift_features(img2)
    
    # Match features
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    
    # Apply Lowe's ratio test
    good = []
    for m, n in matches:
        if m.distance < ratio_threshold * n.distance:
            good.append(m)
    
    print(f"Found {len(good)} good matches out of {len(matches)} total matches")
    
    return good, kp1, kp2


def demo():
    """Run a demonstration of SIFT feature detection."""
    import inspect
    print("\n" + "="*80)
    print("MODULE 8: SIFT FEATURE DESCRIPTOR - SOURCE CODE")
    print("="*80)
    print(inspect.getsource(inspect.getmodule(inspect.currentframe())))
    print("="*80)
    print("\n=== EXECUTING CODE - SIFT Feature Descriptor Demo ===\n")
    sift_pipeline(save_results=True)


if __name__ == "__main__":
    demo()
