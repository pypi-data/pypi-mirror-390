"""
Command-line interface for CV Toolkit
"""

import sys


def main():
    """Main CLI entry point."""
    print("=" * 60)
    print("CV Toolkit - Computer Vision Library")
    print("=" * 60)
    print("\nAvailable demos:")
    print("  1. Image Processing")
    print("  2. Geometric Transformations")
    print("  3. Homography Computation")
    print("  4. Perspective Transformation")
    print("  5. Camera Calibration")
    print("  6. Fundamental Matrix")
    print("  7. Edge, Line & Corner Detection")
    print("  8. SIFT Feature Descriptor")
    print("  9. SURF & HOG Descriptors")
    print("  0. Run All Demos")
    print("\nUsage in Python:")
    print("  from cv_toolkit import image_processing")
    print("  image_processing.demo()")
    print()
    
    choice = input("Enter demo number to run (or 'q' to quit): ")
    
    if choice == 'q':
        sys.exit(0)
    
    try:
        choice = int(choice)
        
        if choice == 1:
            from . import image_processing
            image_processing.demo()
        elif choice == 2:
            from . import geometric_transforms
            geometric_transforms.demo()
        elif choice == 3:
            from . import homography
            homography.demo()
        elif choice == 4:
            from . import perspective_transform
            perspective_transform.demo()
        elif choice == 5:
            from . import camera_calibration
            camera_calibration.demo()
        elif choice == 6:
            from . import fundamental_matrix
            fundamental_matrix.demo()
        elif choice == 7:
            from . import edge_line_corner_detection
            edge_line_corner_detection.demo()
        elif choice == 8:
            from . import sift_descriptor
            sift_descriptor.demo()
        elif choice == 9:
            from . import surf_hog_descriptor
            surf_hog_descriptor.demo()
        elif choice == 0:
            print("\nRunning all demos...")
            run_all_demos()
        else:
            print("Invalid choice!")
    except ValueError:
        print("Invalid input!")
    except Exception as e:
        print(f"Error: {e}")


def run_all_demos():
    """Run all available demos."""
    from . import (
        image_processing,
        geometric_transforms,
        homography,
        perspective_transform,
        camera_calibration,
        sift_descriptor,
    )
    
    print("\n--- Demo 1: Image Processing ---")
    image_processing.demo()
    
    print("\n--- Demo 2: Geometric Transformations ---")
    geometric_transforms.demo()
    
    print("\n--- Demo 3: Homography ---")
    homography.demo()
    
    print("\n--- Demo 4: Perspective Transform ---")
    perspective_transform.demo()
    
    print("\n--- Demo 5: Camera Calibration ---")
    camera_calibration.demo()
    
    print("\n--- Demo 8: SIFT ---")
    sift_descriptor.demo()
    
    print("\nAll demos completed!")


if __name__ == "__main__":
    main()
