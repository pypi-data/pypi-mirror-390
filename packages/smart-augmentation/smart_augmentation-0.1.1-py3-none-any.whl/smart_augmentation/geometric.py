import cv2
import numpy as np
import os

def load_image(image_path):
    return cv2.imread(image_path)

def save_image(output_path, image):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, image)

def rotate(image_path, angle):
    img = load_image(image_path)
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1)
    rotated = cv2.warpAffine(img, M, (w, h))
    return rotated

def flip(image_path, mode='horizontal'):
    img = load_image(image_path)
    if mode == 'horizontal':
        return cv2.flip(img, 1)
    elif mode == 'vertical':
        return cv2.flip(img, 0)
    else:
        raise ValueError("mode must be 'horizontal' or 'vertical'")

def translate(image_path, tx, ty):
    img = load_image(image_path)
    M = np.float32([[1, 0, tx], [0, 1, ty]])
    return cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))

def scale(image_path, fx, fy):
    img = load_image(image_path)
    return cv2.resize(img, None, fx=fx, fy=fy)

def shear(image_path, shear_x=0.2, shear_y=0.2):
    img = load_image(image_path)
    h, w = img.shape[:2]
    M = np.float32([[1, shear_x, 0], [shear_y, 1, 0]])
    return cv2.warpAffine(img, M, (w, h))
