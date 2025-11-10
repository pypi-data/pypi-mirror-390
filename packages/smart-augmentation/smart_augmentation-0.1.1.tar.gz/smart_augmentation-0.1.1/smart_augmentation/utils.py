import os
import cv2
from smart_augmentation import geometric, color, noise, occlusion

def augment_folder(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    for file in os.listdir(input_folder):
        if file.lower().endswith(('.jpg', '.png', '.jpeg')):
            img_path = os.path.join(input_folder, file)

            transformations = {
                'rotated': geometric.rotate(img_path, 45),
                'flipped': geometric.flip(img_path),
                'bright': color.adjust_brightness(img_path),
                'gauss': noise.add_gaussian(img_path),
                'erase': occlusion.random_erasing(img_path)
            }

            for name, img in transformations.items():
                save_path = os.path.join(output_folder, f"{name}_{file}")
                cv2.imwrite(save_path, img)
