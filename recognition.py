#!/usr/bin/python

# Standard imports
import cv2
import numpy as np
import time
from PIL import Image, ImageEnhance
from matplotlib import pyplot as plt


def showme(pic):
    cv2.imshow('window', pic)
    cv2.waitKey()
    cv2.destroyAllWindows()


def invert(imagem):
    return 255 - imagem


def binarize2(arr, thresh=200):
    return (arr > thresh).astype(int) * 255


def binarize_array(numpy_array, threshold=200):
    """Binarize a numpy array."""

    for i in range(len(numpy_array)):
        for j in range(len(numpy_array[0])):
            if numpy_array[i][j] > threshold:
                numpy_array[i][j] = 255
            else:
                numpy_array[i][j] = 0
    return numpy_array


def preprocess_image(im):
    # Preprocessing - Greyscale
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    # Preprocessing - Brightness / Contrast
    pil_im = Image.fromarray(im)
    pil_im = ImageEnhance.Brightness(pil_im).enhance(0.18)
    pil_im = ImageEnhance.Contrast(pil_im).enhance(7)
    pil_im = ImageEnhance.Brightness(pil_im).enhance(0.18)
    pil_im = ImageEnhance.Contrast(pil_im).enhance(7)

    # Convert back to cv2
    im = np.array(pil_im)
    im = binarize2(im)
    im = np.array(im, dtype=np.uint8)
    im = invert(im)
    return im


def process_image(im):
    start = time.time()
    end = time.time()
    print("Preprocessing took {} seconds".format(end - start))

    # Setup SimpleBlobDetector parameters.
    params = cv2.SimpleBlobDetector_Params()

    # Change thresholds
    params.minThreshold = 5
    params.maxThreshold = 200

    # Filter by Area.
    params.filterByArea = True
    params.minArea = 100
    params.maxArea = 1000000000

    # Filter by Circularity
    params.filterByCircularity = False
    params.minCircularity = 0.1

    # Filter by Convexity
    params.filterByConvexity = False
    params.minConvexity = 0.87

    # Filter by Inertia
    params.filterByInertia = False
    params.minInertiaRatio = 0.01

    # Create a detector with the parameters
    detector = cv2.SimpleBlobDetector_create(params)

    # Detect blobs.
    keypoints = detector.detect(im)

    print("{} blob(s) found".format(len(keypoints)))

    if len(keypoints) == 0:
        return None, None, im

    # Get largest keypoint
    largest = None
    for kp in keypoints:
        if largest is None or kp.size > largest.size:
            largest = kp

    print("Largest keypoint at {}".format(largest.pt))

    # Calculate offset
    x, y = largest.pt
    x_size, y_size = len(im[0]), len(im)
    print("Image size is {}x{}".format(x_size, y_size))
    offset = (x / x_size)-0.5, (y / y_size)-0.5

    print("Offset from center is {}".format(offset))

    return largest, offset, im


def plot_image(keypoint, im):
    # Draw detected blobs as red circles.
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures
    # the size of the circle corresponds to the size of blob

    im_with_keypoints = cv2.drawKeypoints(im, [keypoint], np.array([]), (255, 0, 0),
                                          cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    title = 'Blobs Detected'
    image = im_with_keypoints

    plt.subplot(1, 1, 1), plt.imshow(image, 'gray')
    plt.title(title)
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis

    plt.show()


if __name__ == "__main__":
    # Read image
    im = cv2.imread("test_iamges/far2.jpg")

    # Preprocess image
    im = preprocess_image(im)

    # Process image
    keypoint, offset = process_image(im)

    # Plot image
    plot_image(keypoint, im)
