import asyncio
from playwright.async_api import async_playwright
import os

async def scrape_url(url, output_file, seen_imgs):
    """Scrape images from five scrolls of a given URL with improved loading detection."""
    async with async_playwright() as p:
        browser = None
        try:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            # Ensure URL is valid before navigating
            if not url.startswith("http"):
                print(f"Skipping invalid URL: {url}")
                return
            
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(5)  # Initial wait for page load

            # Perform five scrolls with dynamic image checking
            for i in range(5):
                # Get current number of images
                initial_images = await page.query_selector_all("img")
                initial_count = len(initial_images)
                
                # Scroll down
                await page.mouse.wheel(0, 5000)
                await asyncio.sleep(3)  # Wait for images to load

                # Wait for new images to appear or timeout after 10 seconds
                timeout = 10
                start_time = asyncio.get_event_loop().time()
                while True:
                    current_images = await page.query_selector_all("img")
                    current_count = len(current_images)
                    if current_count > initial_count or (asyncio.get_event_loop().time() - start_time) > timeout:
                        break
                    await asyncio.sleep(1)  # Check every second

            # Collect images after scrolling
            img_elements = await page.query_selector_all("img")
            new_images = 0
            for img in img_elements:
                src = await img.get_attribute("src")
                if src and src not in seen_imgs:
                    seen_imgs.add(src)
                    outer_html = await img.evaluate("(element) => element.outerHTML")
                    with open(output_file, "a", encoding='utf-8') as f:
                        f.write(outer_html + "\n")
                    new_images += 1

            print(f"URL {url}: Added {new_images} images to {output_file}")
        except Exception as e:
            print(f"Error processing {url}: {e}")
        finally:
            if browser:
                await browser.close()

async def main():
    # Read and clean URLs from file
    try:
        with open("urls.txt", "r") as f:
            # Strip whitespace, quotes, and trailing commas
            urls = [line.strip().strip('"').strip(",") for line in f if line.strip()]
            urls = [url for url in urls if url]  # Remove empty strings
    except FileNotFoundError:
        print("urls.txt not found")
        return

    # Create output directory if it doesn't exist
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Single output file for all images
    output_file = f"{output_dir}/customAll.html"
    
    # Initialize HTML file
    with open(output_file, "w", encoding='utf-8') as f:
        f.write("<html><body>\n")

    seen_imgs = set()
    # Process all URLs concurrently with a semaphore to limit concurrent browsers
    semaphore = asyncio.Semaphore(3)  # Limit to 3 browsers at a time

    async def sem_scrape(url):
        async with semaphore:
            await scrape_url(url, output_file, seen_imgs)

    try:
        tasks = [sem_scrape(url) for url in urls]
        await asyncio.gather(*tasks, return_exceptions=True)
    except asyncio.CancelledError:
        print("Script was interrupted, cleaning up...")
    finally:
        # Close HTML file
        with open(output_file, "a", encoding='utf-8') as f:
            f.write("</body></html>")

        print(f"Total unique images collected: {len(seen_imgs)} in {output_file}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Script terminated by user, ensuring cleanup...")
    except Exception as e:
        print(f"Unexpected error: {e}")