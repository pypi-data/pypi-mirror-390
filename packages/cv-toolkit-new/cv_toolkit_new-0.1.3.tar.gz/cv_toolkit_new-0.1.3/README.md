# CV Toolkit

A comprehensive computer vision toolkit providing functionalities for image processing, geometric transformations, feature detection, and more.

## Features

- **Image Processing**: Load, resize, convert, and filter images
- **Geometric Transformations**: Translation, rotation, scaling, reflection, shearing
- **Homography Computation**: Compute and apply homography matrices
- **Perspective Transformation**: Perspective warping of images
- **Camera Calibration**: Calibrate cameras and undistort images
- **Fundamental Matrix**: Compute fundamental matrix from stereo images
- **Edge, Line & Corner Detection**: Canny, Hough, Harris, Shi-Tomasi
- **SIFT Features**: Scale-Invariant Feature Transform
- **SURF & HOG**: Feature descriptors for object detection

## Installation

### From PyPI (when published)

```bash
pip install cv-toolkit
```

### From Source (Local Development)

```bash
# Navigate to the directory containing setup.py
cd path/to/CV

# Install in editable mode
pip install -e .

# Or install normally
pip install .
```

## Quick Start

### Example 1: Image Processing

```python
from cv_toolkit import image_processing

# Run demo with sample image
image_processing.demo()

# Or use individual functions
img = image_processing.load_sample_image()
img_gray = image_processing.convert_to_grayscale(img)
img_blur = image_processing.apply_gaussian_blur(img, sigma=2)
```

### Example 2: Geometric Transformations

```python
from cv_toolkit import geometric_transforms

# Run demo
geometric_transforms.demo()

# Or use specific transformations
img = geometric_transforms.data.astronaut()
img_rotated = geometric_transforms.rotate_image(img, angle_deg=45)
img_scaled = geometric_transforms.scale_image(img, scale_x=0.5, scale_y=0.5)
```

### Example 3: Feature Detection (SIFT)

```python
from cv_toolkit import sift_descriptor

# Run demo
sift_descriptor.demo()

# Or use the pipeline
keypoints, descriptors, img_kp = sift_descriptor.sift_pipeline(
    img=your_image, 
    save_results=True
)
```

### Example 4: Edge and Corner Detection

```python
from cv_toolkit import edge_line_corner_detection

# Run full detection pipeline
results = edge_line_corner_detection.detection_pipeline(save_results=True)

# Or use individual functions
edges = edge_line_corner_detection.detect_edges(img)
lines_img = edge_line_corner_detection.detect_lines(img)
corners = edge_line_corner_detection.detect_shi_tomasi_corners(img)
```

### Example 5: Fundamental Matrix

```python
from cv_toolkit import fundamental_matrix

# Run demo with sample stereo images
F, matches, epi1, epi2 = fundamental_matrix.fundamental_matrix_pipeline(
    save_results=True
)
```

## Module Overview

| Module | Description |
|--------|-------------|
| `image_processing` | Basic image operations (load, resize, filter) |
| `geometric_transforms` | Geometric transformations (rotate, scale, etc.) |
| `homography` | Homography matrix computation |
| `perspective_transform` | Perspective transformations |
| `camera_calibration` | Camera calibration and undistortion |
| `fundamental_matrix` | Fundamental matrix from stereo pairs |
| `edge_line_corner_detection` | Edge, line, and corner detection |
| `sift_descriptor` | SIFT feature detection |
| `surf_hog_descriptor` | SURF and HOG descriptors |

## Requirements

- Python >= 3.7
- NumPy >= 1.19.0
- OpenCV >= 4.5.0
- scikit-image >= 0.18.0
- matplotlib >= 3.3.0

## Usage Examples

### Import All Modules

```python
from cv_toolkit import (
    image_processing,
    geometric_transforms,
    homography,
    perspective_transform,
    camera_calibration,
    fundamental_matrix,
    edge_line_corner_detection,
    sift_descriptor,
    surf_hog_descriptor
)
```

### Run All Demos

```python
import cv_toolkit.image_processing as ip
import cv_toolkit.geometric_transforms as gt
import cv_toolkit.sift_descriptor as sift

ip.demo()
gt.demo()
sift.demo()
```

## Development

### Install in Development Mode

```bash
pip install -e .[dev]
```

### Run Tests (when implemented)

```bash
pytest
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Your Name - your.email@example.com

## Acknowledgments

- Built using OpenCV, scikit-image, and NumPy
- Based on classical computer vision algorithms and techniques
