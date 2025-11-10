import cv2
import numpy as np

def add_gaussian(image_path, mean=0, sigma=25):
    img = cv2.imread(image_path)
    gauss = np.random.normal(mean, sigma, img.shape).astype(np.uint8)
    return cv2.add(img, gauss)

def add_salt_pepper(image_path, prob=0.01):
    img = cv2.imread(image_path)
    output = np.copy(img)
    black = np.where(np.random.rand(*img.shape[:2]) < prob / 2)
    white = np.where(np.random.rand(*img.shape[:2]) < prob / 2)
    output[black] = [0, 0, 0]
    output[white] = [255, 255, 255]
    return output

def blur(image_path, ksize=5):
    img = cv2.imread(image_path)
    return cv2.GaussianBlur(img, (ksize, ksize), 0)

def motion_blur(image_path, size=15):
    img = cv2.imread(image_path)
    kernel = np.zeros((size, size))
    kernel[int((size-1)/2), :] = np.ones(size)
    kernel /= size
    return cv2.filter2D(img, -1, kernel)
