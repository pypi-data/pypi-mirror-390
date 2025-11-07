"""
CV Toolkit - A Computer Vision Library
=======================================

A comprehensive computer vision toolkit providing functionalities for:
- Image handling and processing
- Geometric transformations
- Homography and perspective transformations
- Camera calibration
- Fundamental matrix computation
- Edge, line, and corner detection
- Feature descriptors (SIFT, SURF, HOG)

Usage (Simple Number-Based - Recommended):
    import cv_toolkit as cv
    cv.m1.demo()  # Module 1: Image Processing
    cv.m2.demo()  # Module 2: Geometric Transformations
    cv.m3.demo()  # Module 3: Homography
    cv.m4.demo()  # Module 4: Perspective Transform
    cv.m5.demo()  # Module 5: Camera Calibration
    cv.m6.demo()  # Module 6: Fundamental Matrix
    cv.m7.demo()  # Module 7: Edge/Line/Corner Detection
    cv.m8.demo()  # Module 8: SIFT Descriptor
    cv.m9.demo()  # Module 9: SURF & HOG Descriptor

Alternative (Full Names):
    from cv_toolkit import image_processing
    image_processing.demo()
"""

__version__ = "0.1.2"
__author__ = "Your Name"

# Import main modules
from . import image_processing
from . import geometric_transforms
from . import homography
from . import perspective_transform
from . import camera_calibration
from . import fundamental_matrix
from . import edge_line_corner_detection
from . import sift_descriptor
from . import surf_hog_descriptor
from . import code_display

# Create simple numbered aliases for easy access (m1, m2, ..., m9)
m1 = image_processing              # Module 1: Image Processing
m2 = geometric_transforms          # Module 2: Geometric Transformations
m3 = homography                    # Module 3: Homography
m4 = perspective_transform         # Module 4: Perspective Transform
m5 = camera_calibration            # Module 5: Camera Calibration
m6 = fundamental_matrix            # Module 6: Fundamental Matrix
m7 = edge_line_corner_detection    # Module 7: Edge/Line/Corner Detection
m8 = sift_descriptor               # Module 8: SIFT Descriptor
m9 = surf_hog_descriptor           # Module 9: SURF & HOG Descriptor

# Import code display utilities for easy access
from .code_display import display_code, display_module_code, show_code_and_run

__all__ = [
    # Original module names
    'image_processing',
    'geometric_transforms',
    'homography',
    'perspective_transform',
    'camera_calibration',
    'fundamental_matrix',
    'edge_line_corner_detection',
    'sift_descriptor',
    'surf_hog_descriptor',
    'code_display',
    # Numbered aliases (m1-m9)
    'm1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9',
    # Utilities
    'display_code',
    'display_module_code',
    'show_code_and_run'
]
