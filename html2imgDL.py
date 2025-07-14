import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

HTML_FILE = 'output\customAll.html'
OUTPUT_FOLDER = 'Danger'
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ext_map = {
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/webp': '.webp',
}

# Read and parse HTML
with open(HTML_FILE, 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')
img_tags = soup.find_all('img')

# Collect unique image URLs
image_urls = []

for img in img_tags:
    src = img.get('src')
    if src and src.startswith('https://image.lexica.art/'):
        image_urls.append(src)

image_urls = list(set(image_urls))
print(f"Found {len(image_urls)} unique lexica images.")

# Download function
def download_image(url):
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            content_type = resp.headers.get('Content-Type')
            ext = ext_map.get(content_type, '')  # default: no extension if unknown
            uuid = url.split('/')[-1].split('?')[0]
            filename = f"{uuid}{ext}"
            file_path = os.path.join(OUTPUT_FOLDER, filename)
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(resp.content)
            return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
    return False

# Parallel download using ThreadPoolExecutor
MAX_WORKERS = 16  # You can tune this depending on your system

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {executor.submit(download_image, url): url for url in image_urls}
    for _ in tqdm(as_completed(futures), total=len(futures)):
        pass

print("✅ All downloads complete!")
