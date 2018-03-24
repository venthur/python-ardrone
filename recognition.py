#!/usr/bin/python

# Standard imports
import cv2
import numpy as np
import time
import pygame
from PIL import Image, ImageEnhance


def showme(pic):
    cv2.imshow('window', pic)
    cv2.waitKey()
    cv2.destroyAllWindows()


def invert(imagem):
    return 255 - imagem


def binarize2(arr, thresh=170):
    return (arr > thresh).astype(int) * 255


def check_lightness(im):
    under_horizon = False

    for x in xrange(len(im)):
        val = np.sum(im[x])
        if not under_horizon:
            im[x] = (im[x] < -1).astype(int)

            if val < 25*255:
                #print("Horizon is at y={}".format(x))
                under_horizon = True

    return im


def preprocess_image(im):
    # Preprocessing - Greyscale
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    #im = np.array(map(extract_red, im))

    # Preprocessing - Brightness / Contrast
    pil_im = Image.fromarray(im)
    pil_im = ImageEnhance.Brightness(pil_im).enhance(0.20)
    pil_im = ImageEnhance.Contrast(pil_im).enhance(7)
    pil_im = ImageEnhance.Brightness(pil_im).enhance(0.20)
    pil_im = ImageEnhance.Contrast(pil_im).enhance(7)

    # Convert back to cv2
    im = np.array(pil_im)

    im = binarize2(im)

    im = check_lightness(im)

    im = np.array(im, dtype=np.uint8)
    im = invert(im)
    return im


def process_image(im):

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

    #print("{} blob(s) found".format(len(keypoints)))

    if len(keypoints) == 0:
        return None, None

    # Get largest keypoint
    largest = None
    for kp in keypoints:
        if largest is None or kp.size > largest.size:
            largest = kp

    #print("Largest keypoint at {}".format(largest.pt))

    # Calculate offset
    x, y = largest.pt
    x_size, y_size = len(im[0]), len(im)
    print("Image size is {}x{}".format(x_size, y_size))
    offset = (x / x_size)-0.5, (y / y_size)-0.5

    #print("Offset from center is {}".format(offset))

    return largest, offset


def draw_keypoint(keypoint, im):
    return cv2.drawKeypoints(im, [keypoint], np.array([]), (255, 0, 0),
                             cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)


def plot_image(keypoint, im, screen, clock):
    # Draw detected blobs as red circles.
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures
    # the size of the circle corresponds to the size of blob
    surface = pygame.image.frombuffer(im, (W, H), 'RGB')
    screen.blit(surface, (0, 0))
    pygame.display.flip()
    clock.tick(20)
    pygame.display.set_caption("FPS: %.2f" % clock.get_fps())
    time.sleep(1)


def initialize(W, H):
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    clock = pygame.time.Clock()

    return screen, clock


if __name__ == "__main__":
    W, H = 1280, 720
    screen, clock = initialize(W, H)

    # Read image
    im = cv2.imread("test_images/far2.jpg")

    # Preprocess image
    im = preprocess_image(im)

    # Process image
    keypoint, offset = process_image(im)

    # Draw keypoints
    im = draw_keypoint(keypoint, im)

    # # Plot image
    plot_image(keypoint, im, screen, clock)
