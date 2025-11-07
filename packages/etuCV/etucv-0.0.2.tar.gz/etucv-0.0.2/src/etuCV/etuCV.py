import cv2
import numpy as np
import matplotlib.pyplot as plt

try:
    from skimage.feature import hog
    from skimage import exposure
    SKIMAGE_INSTALLED = True
except ImportError:
    SKIMAGE_INSTALLED = False

class etuCV:
    """
    A Computer Vision library tailored to a specific university syllabus.

    This class provides high-level functions for core CV algorithms like
    edge detection and feature description. All image displays are handled
    by Matplotlib for high-quality, consistent plotting.
    """
    def __init__(self, filepath):
        """Initializes the class by loading an image from the given path."""
        self.image = cv2.imread(filepath)
        if self.image is None:
            raise FileNotFoundError(f"Image not found at path: {filepath}")
        self.gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

    def show(self, window_name, image_to_show):
        """
        Displays an image using Matplotlib, handling color space conversion.
        """
        if len(image_to_show.shape) == 2:
            cmap = 'gray'
        else:
            # OpenCV loads images in BGR, but Matplotlib displays in RGB.
            # This conversion is necessary for correct color display.
            image_to_show = cv2.cvtColor(image_to_show, cv2.COLOR_BGR2RGB)
            cmap = None

        plt.figure(figsize=(8, 6))
        plt.imshow(image_to_show, cmap=cmap)
        plt.title(window_name, fontsize=14)
        plt.axis('off')
        plt.show()

    def detect_log_edges(self, kernel_size=5):
        """
        Applies Laplacian of Gaussian (LoG) to detect edges in the image.

        :param kernel_size: The size of the Gaussian blur kernel. Defaults to 5.
        """
        print(f"-> Applying Laplacian of Gaussian (LoG)...")
        blur = cv2.GaussianBlur(self.gray_image, (kernel_size, kernel_size), 0)
        laplacian = cv2.Laplacian(blur, cv2.CV_64F)
        log_edges = cv2.convertScaleAbs(laplacian)
        self.show("LoG Edges", log_edges)
        return log_edges

    def detect_dog_features(self, low_sigma=1.0, high_sigma=1.6):
        """
        Applies Difference of Gaussians (DoG) to highlight blobs and edges.

        :param low_sigma: Sigma for the weaker Gaussian blur. Defaults to 1.0.
        :param high_sigma: Sigma for the stronger Gaussian blur. Defaults to 1.6.
        """
        print(f"-> Applying Difference of Gaussians (DoG)...")
        blur1 = cv2.GaussianBlur(self.gray_image, (0, 0), sigmaX=low_sigma)
        blur2 = cv2.GaussianBlur(self.gray_image, (0, 0), sigmaX=high_sigma)
        dog_image = cv2.normalize(blur1 - blur2, None, 255, 0, cv2.NORM_MINMAX, cv2.CV_8U)
        self.show("Difference of Gaussians (DoG)", dog_image)
        return dog_image

    def compute_and_visualize_hog(self):
        """
        Computes and visualizes Histogram of Oriented Gradients (HOG) features.
        Requires 'scikit-image' and 'matplotlib' to be installed.
        """
        if not SKIMAGE_INSTALLED:
            raise ImportError("Please install scikit-image and matplotlib to use this feature.")

        print(f"-> Computing Histogram of Oriented Gradients (HOG)...")
        fd, hog_image = hog(self.gray_image, orientations=8, pixels_per_cell=(16, 16),
                            cells_per_block=(1, 1), visualize=True)
        hog_image_rescaled = exposure.rescale_intensity(hog_image, in_range=(0, 10))
        self.show("HOG Visualization", hog_image_rescaled)
        return fd

    def find_harris_corners(self, block_size=2, ksize=3, k=0.04):
        """
        Finds corners using the Harris Corner detection algorithm.

        :param block_size: Neighborhood size for corner detection. Defaults to 2.
        :param ksize: Aperture parameter for the Sobel operator. Defaults to 3.
        :param k: Harris detector free parameter in the equation. Defaults to 0.04.
        """
        print(f"-> Finding Harris Corners...")
        # The cornerHarris function requires a float32 input image.
        gray_float = np.float32(self.gray_image)
        dst = cv2.cornerHarris(gray_float, blockSize=block_size, ksize=ksize, k=k)
        
        output_image = self.image.copy()
        output_image[dst > 0.01 * dst.max()] = [0, 0, 255] # Mark corners in red
        
        self.show("Harris Corners", output_image)
        return output_image