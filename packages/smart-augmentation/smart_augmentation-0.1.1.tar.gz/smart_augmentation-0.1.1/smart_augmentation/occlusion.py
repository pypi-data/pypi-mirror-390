import cv2
import numpy as np
import random

def random_erasing(image_path, num_patches=3, size_ratio=(0.1, 0.3)):
    img = cv2.imread(image_path)
    h, w, _ = img.shape
    for _ in range(num_patches):
        erase_w = int(random.uniform(size_ratio[0], size_ratio[1]) * w)
        erase_h = int(random.uniform(size_ratio[0], size_ratio[1]) * h)
        x1 = random.randint(0, w - erase_w)
        y1 = random.randint(0, h - erase_h)
        img[y1:y1+erase_h, x1:x1+erase_w] = np.random.randint(0, 255, (erase_h, erase_w, 3), dtype=np.uint8)
    return img

def coarse_dropout(image_path, holes=8, hole_size=(15, 40)):
    img = cv2.imread(image_path)
    h, w, _ = img.shape
    for _ in range(holes):
        y = random.randint(0, h - hole_size[1])
        x = random.randint(0, w - hole_size[0])
        hole_w = random.randint(hole_size[0], hole_size[1])
        hole_h = random.randint(hole_size[0], hole_size[1])
        img[y:y+hole_h, x:x+hole_w] = 0
    return img
