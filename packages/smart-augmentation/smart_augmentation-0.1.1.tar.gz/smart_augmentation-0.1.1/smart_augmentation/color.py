import cv2
import numpy as np

def adjust_brightness(image_path, factor=1.2):
    img = cv2.imread(image_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv[..., 2] = np.clip(hsv[..., 2] * factor, 0, 255)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def adjust_contrast(image_path, factor=1.2):
    img = cv2.imread(image_path)
    return cv2.convertScaleAbs(img, alpha=factor, beta=0)

def adjust_saturation(image_path, factor=1.2):
    img = cv2.imread(image_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv[..., 1] = np.clip(hsv[..., 1] * factor, 0, 255)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def adjust_hue(image_path, delta=10):
    img = cv2.imread(image_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv[..., 0] = (hsv[..., 0] + delta) % 180
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
