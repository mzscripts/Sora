from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://sora.chatgpt.com/explore"
OUTPUT_DIR = "downloaded_images"

def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=chrome_options)

def fetch_rendered_html_with_scroll(url, scroll_count=5):
    driver = init_driver()
    driver.get(url)

    for _ in range(scroll_count):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for content to load

    html = driver.page_source
    driver.quit()
    return html

def download_and_save(img_url, folder):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(img_url, headers=headers)
    response.raise_for_status()
    ext = img_url.split('.')[-1].split('?')[0]
    filename = f"image.{ext if len(ext) <= 5 else 'jpg'}"
    path = os.path.join(folder, filename)
    with open(path, "wb") as f:
        f.write(response.content)
    return path

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    html = fetch_rendered_html_with_scroll(BASE_URL)
    soup = BeautifulSoup(html, "html.parser")

    # Collect all image URLs from <img> and style="background-image"
    img_urls = []

    # Extract from <img src=...>
    for tag in soup.find_all("img"):
        src = tag.get("src")
        if src and src.startswith("http"):
            img_urls.append(src)

    # Extract from style="background-image: url(...)"
    for div in soup.find_all("div"):
        style = div.get("style", "")
        if "background-image" in style and "url(" in style:
            start = style.find("url(") + 4
            end = style.find(")", start)
            url = style[start:end].strip("'\"")
            if url.startswith("http"):
                img_urls.append(url)

    # Deduplicate
    img_urls = list(set(img_urls))

    html_lines = ["<html><body><h1>Image Gallery</h1>"]
    count = 0

    for idx, src in enumerate(img_urls, start=1):
        folder = os.path.join(OUTPUT_DIR, f"image_{idx}")
        os.makedirs(folder, exist_ok=True)

        try:
            img_path = download_and_save(src, folder)
            html_lines.append(f"<div><h3>Image {idx}</h3><img src='{img_path}' width='300'></div>")
            print(f"✅ Saved Image {idx} → {img_path}")
            count += 1
        except Exception as e:
            print(f"❌ Failed to download {src}: {e}")

    html_lines.append("</body></html>")
    with open("custompage.html", "w") as f:
        f.write("\n".join(html_lines))

    print(f"\n✅ Done – custompage.html generated with {count} images.")

if __name__ == "__main__":
    main()
