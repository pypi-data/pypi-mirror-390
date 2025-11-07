"""
Edge, Line, and Corner Detection Module
Provides functions for detecting edges (Canny), lines (Hough), 
and corners (Harris, Shi-Tomasi).
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


def detect_edges(img, low_threshold=50, high_threshold=150):
    """
    Detect edges using Canny edge detector.
    
    Args:
        img: Input image (color or grayscale)
        low_threshold: Lower threshold for Canny
        high_threshold: Upper threshold for Canny
    
    Returns:
        Edge image
    """
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    
    edges = cv2.Canny(gray, low_threshold, high_threshold)
    return edges


def detect_lines(img, edges=None, threshold=100, min_line_length=100, max_line_gap=10):
    """
    Detect lines using Hough Line Transform.
    
    Args:
        img: Input image
        edges: Edge image (if None, computes edges)
        threshold: Accumulator threshold
        min_line_length: Minimum line length
        max_line_gap: Maximum gap between line segments
    
    Returns:
        Image with detected lines drawn
    """
    if edges is None:
        edges = detect_edges(img)
    
    lines_img = img.copy()
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 
                            threshold=threshold, 
                            minLineLength=min_line_length, 
                            maxLineGap=max_line_gap)
    
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(lines_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
    
    return lines_img


def detect_harris_corners(img, block_size=2, ksize=3, k=0.04, threshold=0.01):
    """
    Detect corners using Harris Corner Detection.
    
    Args:
        img: Input image
        block_size: Neighborhood size
        ksize: Aperture parameter for Sobel
        k: Harris detector free parameter
        threshold: Threshold for corner detection
    
    Returns:
        Image with detected corners marked
    """
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    
    gray_f = np.float32(gray)
    harris = cv2.cornerHarris(gray_f, block_size, ksize, k)
    harris = cv2.dilate(harris, None)
    
    harris_img = img.copy() if len(img.shape) == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    harris_img[harris > threshold * harris.max()] = [0, 255, 0]
    
    return harris_img


def detect_shi_tomasi_corners(img, max_corners=200, quality_level=0.01, min_distance=10):
    """
    Detect corners using Shi-Tomasi Corner Detection.
    
    Args:
        img: Input image
        max_corners: Maximum number of corners to detect
        quality_level: Quality level parameter
        min_distance: Minimum distance between corners
    
    Returns:
        Image with detected corners marked
    """
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    
    shi_img = img.copy() if len(img.shape) == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    corners = cv2.goodFeaturesToTrack(gray, 
                                      maxCorners=max_corners,
                                      qualityLevel=quality_level,
                                      minDistance=min_distance)
    
    if corners is not None:
        corners = np.int32(corners)
        for c in corners:
            x, y = c.ravel()
            cv2.circle(shi_img, (x, y), 4, (255, 0, 0), -1)
    
    return shi_img


def detection_pipeline(img=None, save_results=False):
    """
    Complete edge, line, and corner detection pipeline.
    
    Args:
        img: Input image (if None, loads sample)
        save_results: Whether to save output images
    
    Returns:
        Dictionary containing all detection results
    """
    if img is None:
        print("Loading sample image...")
        img = load_sample_image()
        print("Image loaded successfully!")
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Perform all detections
    edges = detect_edges(img)
    if save_results:
        cv2.imwrite("edges_v2.jpg", edges)
    
    lines_img = detect_lines(img, edges)
    if save_results:
        cv2.imwrite("lines_v2.jpg", lines_img)
    
    harris_img = detect_harris_corners(img)
    if save_results:
        cv2.imwrite("harris_corners_v2.jpg", harris_img)
    
    shi_img = detect_shi_tomasi_corners(img)
    if save_results:
        cv2.imwrite("shi_tomasi_corners_v2.jpg", shi_img)
        print("Saved: edges_v2.jpg, lines_v2.jpg, harris_corners_v2.jpg, shi_tomasi_corners_v2.jpg")
    
    results = {
        'edges': edges,
        'lines': lines_img,
        'harris_corners': harris_img,
        'shi_tomasi_corners': shi_img
    }
    
    return results


def demo():
    """Run a demonstration of edge, line, and corner detection."""
    import inspect
    print("\n" + "="*80)
    print("MODULE 7: EDGE, LINE & CORNER DETECTION - SOURCE CODE")
    print("="*80)
    print(inspect.getsource(inspect.getmodule(inspect.currentframe())))
    print("="*80)
    print("\n=== EXECUTING CODE - Edge, Line, and Corner Detection Demo ===\n")
    detection_pipeline(save_results=True)


if __name__ == "__main__":
    demo()
