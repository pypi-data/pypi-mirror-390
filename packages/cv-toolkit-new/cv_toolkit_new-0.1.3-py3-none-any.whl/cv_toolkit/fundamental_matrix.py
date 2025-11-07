"""
Fundamental Matrix Computation Module
Provides functions to compute fundamental matrix from stereo images
and draw epipolar lines.
"""

import cv2
import numpy as np
from sklearn.datasets import load_sample_images


def load_sample_image_pair():
    """
    Load sample images from sklearn dataset.
    
    Returns:
        Tuple of (img1, img2) - two sample images
    """
    sample_images = load_sample_images()
    images = sample_images.images
    
    img1 = images[0]
    img2 = images[1]
    
    # Convert to uint8 if needed
    if img1.dtype != np.uint8:
        img1 = (img1 * 255).astype(np.uint8)
    if img2.dtype != np.uint8:
        img2 = (img2 * 255).astype(np.uint8)
    
    # Convert RGB to BGR for OpenCV
    img1 = cv2.cvtColor(img1, cv2.COLOR_RGB2BGR)
    img2 = cv2.cvtColor(img2, cv2.COLOR_RGB2BGR)
    
    return img1, img2


def detect_and_match_features(img1, img2, ratio_threshold=0.75):
    """
    Detect SIFT features and match them between two images.
    
    Args:
        img1: First image
        img2: Second image
        ratio_threshold: Lowe's ratio test threshold
    
    Returns:
        Tuple of (good_matches, pts1, pts2, kp1, kp2)
    """
    # Convert to grayscale
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # Detect SIFT keypoints and descriptors
    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(gray1, None)
    kp2, des2 = sift.detectAndCompute(gray2, None)
    
    # Match features
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    
    # Apply Lowe's ratio test
    good = []
    pts1 = []
    pts2 = []
    for m, n in matches:
        if m.distance < ratio_threshold * n.distance:
            good.append(m)
            pts1.append(kp1[m.queryIdx].pt)
            pts2.append(kp2[m.trainIdx].pt)
    
    pts1 = np.int32(pts1)
    pts2 = np.int32(pts2)
    
    return good, pts1, pts2, kp1, kp2


def compute_fundamental_matrix(pts1, pts2):
    """
    Compute fundamental matrix from matched points.
    
    Args:
        pts1: Points in first image
        pts2: Points in second image
    
    Returns:
        Tuple of (fundamental_matrix, mask)
    """
    F, mask = cv2.findFundamentalMat(pts1, pts2, cv2.FM_RANSAC)
    return F, mask


def draw_epipolar_lines(img1, img2, lines, pts1, pts2):
    """
    Draw epipolar lines on images.
    
    Args:
        img1: First image
        img2: Second image
        lines: Epipolar lines
        pts1: Points in first image
        pts2: Points in second image
    
    Returns:
        Tuple of (img1_with_lines, img2_with_lines)
    """
    img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    img1_color = cv2.cvtColor(img1, cv2.COLOR_GRAY2BGR)
    img2_color = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR)
    r, c = img1.shape[:2]
    
    for rline, pt1, pt2 in zip(lines, pts1, pts2):
        color = tuple(np.random.randint(0, 255, 3).tolist())
        x0, y0 = map(int, [0, -rline[2] / rline[1]])
        x1, y1 = map(int, [c, -(rline[2] + rline[0] * c) / rline[1]])
        cv2.line(img2_color, (x0, y0), (x1, y1), color, 1)
        cv2.circle(img1_color, tuple(pt1), 5, color, -1)
        cv2.circle(img2_color, tuple(pt2), 5, color, -1)
    
    return img1_color, img2_color


def fundamental_matrix_pipeline(img1=None, img2=None, save_results=False):
    """
    Complete fundamental matrix computation pipeline.
    
    Args:
        img1: First image (if None, loads sample images)
        img2: Second image (if None, loads sample images)
        save_results: Whether to save output images
    
    Returns:
        Tuple of (fundamental_matrix, matches_img, epilines_img1, epilines_img2)
    """
    # Load sample images if not provided
    if img1 is None or img2 is None:
        print("Loading sample images...")
        img1, img2 = load_sample_image_pair()
        print("Images loaded successfully.")
    
    # Detect and match features
    good, pts1, pts2, kp1, kp2 = detect_and_match_features(img1, img2)
    
    if len(good) < 8:
        print("Not enough matches. Found:", len(good))
        return None, None, None, None
    
    print("Found", len(good), "good matches")
    
    # Compute fundamental matrix
    F, mask = compute_fundamental_matrix(pts1, pts2)
    print("\nFundamental Matrix:")
    print(F)
    
    # Filter inliers
    pts1_in = pts1[mask.ravel() == 1]
    pts2_in = pts2[mask.ravel() == 1]
    
    # Compute epipolar lines
    lines1 = cv2.computeCorrespondEpilines(pts2_in.reshape(-1, 1, 2), 2, F)
    lines1 = lines1.reshape(-1, 3)
    
    # Draw epipolar lines
    img_epi1, img_epi2 = draw_epipolar_lines(img1, img2, lines1, pts1_in, pts2_in)
    
    # Draw matches
    matches_img = cv2.drawMatches(img1, kp1, img2, kp2, good, None, flags=2)
    
    if save_results:
        cv2.imwrite("matches_v2.jpg", matches_img)
        cv2.imwrite("epilines_left_v2.jpg", img_epi1)
        cv2.imwrite("epilines_right_v2.jpg", img_epi2)
        np.save("fundamental_matrix_v2.npy", F)
        print("\nSaved: matches_v2.jpg, epilines_left_v2.jpg, epilines_right_v2.jpg, fundamental_matrix_v2.npy")
    
    return F, matches_img, img_epi1, img_epi2


def demo(show_code=True):
    """
    Run a demonstration of fundamental matrix computation.
    
    Args:
        show_code: Whether to display source code (default: True)
    """
    if show_code:
        import inspect
        print("\n" + "="*80)
        print("MODULE 6: FUNDAMENTAL MATRIX - SOURCE CODE")
        print("="*80)
        
        # Try to get module source (works in .py files)
        try:
            module = inspect.getmodule(inspect.currentframe())
            if module is not None:
                print(inspect.getsource(module))
            else:
                # Fallback for Jupyter notebooks - print individual functions
                functions_to_show = [
                    load_sample_image_pair, detect_and_match_features,
                    compute_fundamental_matrix, draw_epipolar_lines,
                    fundamental_matrix_pipeline, demo
                ]
                for func in functions_to_show:
                    print(inspect.getsource(func))
        except Exception as e:
            print(f"Note: Could not display full source code: {e}")
            print("This is expected in some environments like Jupyter notebooks.")
        
        print("="*80)
    
    print("\n=== EXECUTING CODE - Fundamental Matrix Computation Demo ===\n")
    fundamental_matrix_pipeline(save_results=True)


if __name__ == "__main__":
    # When run as script, don't show code (user has the code already)
    demo(show_code=False)
