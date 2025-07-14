import asyncio
import logging
from playwright.async_api import async_playwright
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def extract_and_save_image_urls(page):
    # Wait for the page to load
    logger.info("Waiting for page to load")
    await page.wait_for_load_state("load")

    # Extract all img tags and their src attributes
    logger.info("Extracting image URLs")
    img_elements = await page.query_selector_all("img")
    image_urls = []
    for img in img_elements:
        src = await img.get_attribute("src")
        if src and src.startswith("http"):
            image_urls.append(src)
            logger.debug(f"Found image URL: {src}")

    # Save URLs to a file
    if image_urls:
        with open("image_urls.txt", "w") as f:
            for url in image_urls:
                f.write(url + "\n")
        logger.info(f"Saved {len(image_urls)} image URLs to image_urls.txt")
    else:
        logger.warning("No image URLs found")

async def main():
    try:
        async with async_playwright() as p:
            logger.info("Launching Chromium browser")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Load the local HTML file (replace 'explore.html' with your file path)
            html_file_path = os.path.abspath("explore.html")
            logger.info(f"Loading HTML file: {html_file_path}")
            await page.goto(f"file://{html_file_path}")

            await extract_and_save_image_urls(page)

            logger.info("Closing browser")
            await browser.close()
    except Exception as e:
        logger.error(f"Main process failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())