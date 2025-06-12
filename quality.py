import os
import shutil
from PIL import Image
import cv2
import numpy as np

# Folders
input_folder = "motu"  # your input folder
low_quality_folder = "low_quality_images"
good_quality_folder = "good_quality_images"

# Create output folders
os.makedirs(low_quality_folder, exist_ok=True)
os.makedirs(good_quality_folder, exist_ok=True)

# Parameters
MIN_FILE_SIZE_KB = 50   # below this, likely low quality
MIN_RESOLUTION = (300, 300)  # min width, height
BLUR_THRESHOLD = 100.0

def is_low_filesize(file_path):
    file_size_kb = os.path.getsize(file_path) / 1024
    return file_size_kb < MIN_FILE_SIZE_KB

def is_low_resolution(file_path):
    with Image.open(file_path) as img:
        width, height = img.size
    return width < MIN_RESOLUTION[0] or height < MIN_RESOLUTION[1]

def is_blurry(file_path):
    image = cv2.imread(file_path)
    if image is None:
        return True
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var < BLUR_THRESHOLD

# Loop through images
for filename in os.listdir(input_folder):
    if not filename.lower().endswith('.png'):
        continue

    filepath = os.path.join(input_folder, filename)

    try:
        if is_low_filesize(filepath) or is_low_resolution(filepath) or is_blurry(filepath):
            print(f"Low quality: {filename}")
            shutil.move(filepath, os.path.join(low_quality_folder, filename))
        else:
            print(f"Good quality: {filename}")
            shutil.move(filepath, os.path.join(good_quality_folder, filename))
    except Exception as e:
        print(f"Error processing {filename}: {e}")
