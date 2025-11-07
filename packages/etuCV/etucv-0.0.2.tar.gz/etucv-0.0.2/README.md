# etuCV

etuCV is a Computer Vision library tailored to a specific university syllabus. It provides high-level, easy-to-use functions for core computer vision algorithms, making it ideal for educational purposes. All image displays are handled by Matplotlib for high-quality, consistent plotting.

## Installation

You can install etuCV using pip:

```bash
pip install etuCV
```

## Usage

Here is a simple example of how to use the library to detect Harris corners in an image:

```python
from etuCV.etuCV import etuCV

# Initialize the library with the path to your image
try:
    vision = etuCV('path/to/your/image.jpg')
    vision.find_harris_corners()
except FileNotFoundError as e:
    print(e)
```    

## Features

*   Laplacian of Gaussian (LoG) edge detection.
*   Difference of Gaussians (DoG) for blob and edge highlighting.
*   Histogram of Oriented Gradients (HOG) feature computation and visualization.
*   Harris Corner detection.