import os
import shutil
import hashlib
from PIL import Image

# Set working directories
source_folders = [
    "downloaded_images",
    "downloaded_images2",
    "downloaded_images3",
    "downloaded_images4",
    "downloaded_images5",
    "downloaded_images6",
    "downloaded_images7fat"
]

output_folder = "combined_images"
os.makedirs(output_folder, exist_ok=True)

# Store hashes to detect duplicates
hashes = set()

def calculate_hash(image_path):
    """Calculate SHA256 hash of an image file"""
    try:
        with Image.open(image_path) as img:
            img = img.convert('RGB')  # Ensure consistent format
            hash_md5 = hashlib.sha256(img.tobytes()).hexdigest()
            return hash_md5
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

# Process all images
for folder in source_folders:
    for root, dirs, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            file_hash = calculate_hash(file_path)
            
            if file_hash and file_hash not in hashes:
                hashes.add(file_hash)
                
                # Ensure unique filenames in output folder
                base, ext = os.path.splitext(file)
                new_filename = f"{base}{ext}"
                counter = 1
                while os.path.exists(os.path.join(output_folder, new_filename)):
                    new_filename = f"{base}_{counter}{ext}"
                    counter += 1
                    
                shutil.copy(file_path, os.path.join(output_folder, new_filename))
                print(f"Copied: {file_path} -> {new_filename}")
            else:
                print(f"Duplicate found: {file_path}")

print("Merging completed!")
