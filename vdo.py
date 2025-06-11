import os
import re
import requests
import hashlib

# Path to your input txt file
input_file = 'input.txt'
# Output folder to save videos
output_folder = 'downloaded_videos'

# Create output directory if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Regular expression to extract URLs from file
url_pattern = re.compile(r'"url":\s*"([^"]+)"')

# Set to store hashes of downloaded files for uniqueness
downloaded_hashes = set()

# Function to generate hash of content for uniqueness
def get_hash(content):
    return hashlib.sha256(content).hexdigest()

# Read and extract URLs
with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()
    urls = url_pattern.findall(content)

print(f"Found {len(urls)} URLs in the file.")

# Start downloading
for idx, url in enumerate(urls, 1):
    try:
        print(f"Downloading ({idx}/{len(urls)}): {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        file_hash = get_hash(response.content)
        if file_hash in downloaded_hashes:
            print("Duplicate file detected, skipping...")
            continue
        
        downloaded_hashes.add(file_hash)

        # Generate a safe filename
        filename = url.split("/")[-1].split("?")[0]
        save_path = os.path.join(output_folder, filename)

        with open(save_path, 'wb') as out_file:
            out_file.write(response.content)

        print(f"Saved: {save_path}")

    except Exception as e:
        print(f"Failed to download: {url}\nError: {e}")

print("Download complete.")
