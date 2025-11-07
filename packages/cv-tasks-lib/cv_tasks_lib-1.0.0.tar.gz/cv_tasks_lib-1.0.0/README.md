# CVLIB - Computer Vision Library

A Python library that displays complete source code for 9 computer vision tasks.

## Installation

```bash
pip install cvlib
```

## Usage

Import and display the source code of any task:

```python
import cvlib

# Display individual tasks
cvlib.show_task_1()    # Image handling
cvlib.show_task_2()    # Geometric transformations
cvlib.show_task_3()    # Homography matrix
cvlib.show_task_4()    # Perspective transformation
cvlib.show_task_5()    # Camera calibration
cvlib.show_task_6()    # Fundamental matrix
cvlib.show_task_7()    # Edge, line, corner detection
cvlib.show_task_8()    # SIFT features
cvlib.show_task_9()    # SIFT and HOG descriptors

# Display all 9 tasks
cvlib.show_all()
```

## Available Functions

- `show_task_1()` - Image operations (resize, rotate, flip, blur)
- `show_task_2()` - Geometric transformations (translation, rotation, scaling, shearing)
- `show_task_3()` - Homography matrix computation
- `show_task_4()` - Perspective transformation
- `show_task_5()` - Camera calibration with barrel distortion
- `show_task_6()` - Fundamental matrix from stereo images
- `show_task_7()` - Canny edges, Hough lines, Harris/Shi-Tomasi corners
- `show_task_8()` - SIFT keypoint detection and descriptors
- `show_task_9()` - SIFT and HOG descriptors
- `show_all()` - Display all 9 tasks

## Example

```python
import cvlib

# See the complete code for task 1
cvlib.show_task_1()

# Output:
# ================================================================================
# TASK 1: IMAGE HANDLING AND PROCESSING
# ================================================================================
# def image_operations(image_path=None):
#     """Task 1: Perform basic image operations: resize, rotate, flip, blur"""
#     if image_path is None:
#         from skimage import data
#         img = data.astronaut()
#     ...
```

## Requirements

- Python >= 3.7
- opencv-python
- numpy
- matplotlib
- scikit-image
- scikit-learn

## License

MIT
