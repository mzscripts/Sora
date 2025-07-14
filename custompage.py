import asyncio
from playwright.async_api import async_playwright
import aiohttp
from urllib.parse import urlparse, parse_qs
import os

async def is_suitable_for_wallpaper(src, page):
    """Check if image has suitable aspect ratio for mobile wallpaper."""
    try:
        # Create a temporary image element to get dimensions
        await page.evaluate(f"""
            () => {{
                const img = document.createElement('img');
                img.src = '{src}';
                document.body.appendChild(img);
            }}
        """)
        dimensions = await page.evaluate(f"""
            () => {{
                const img = document.querySelector('img[src="{src}"]');
                if (img && img.naturalWidth && img.naturalHeight) {{
                    return {{ width: img.naturalWidth, height: img.naturalHeight }};
                }}
                return null;
            }}
        """)
        await page.evaluate(f"""
            () => {{
                const img = document.querySelector('img[src="{src}"]');
                if (img) img.remove();
            }}
        """)
        
        if dimensions:
            width, height = dimensions['width'], dimensions['height']
            if width == 0 or height == 0:
                return False
            aspect_ratio = height / width
            # Typical mobile wallpaper aspect ratio: ~1.77 (9:16) to ~2.16 (19.5:9)
            return 1.5 <= aspect_ratio <= 2.5
        return False
    except Exception:
        return False

async def scrape_url(url, output_dir="output"):
    """Scrape images from the third scroll of a given URL."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="networkidle")
            await asyncio.sleep(5)

            seen_imgs = set()
            # Generate output filename from URL query parameter
            query = parse_qs(urlparse(url).query)
            query_id = query.get('q', [f"url_{hash(url)}"])[0]
            output_file = f"{output_dir}/lexica_{query_id}.html"

            # Perform three scrolls
            for i in range(3):
                await page.mouse.wheel(0, 5000)
                await asyncio.sleep(2)

            # Collect images after the third scroll
            img_elements = await page.query_selector_all("img")
            with open(output_file, "w", encoding='utf-8') as f:
                f.write("<html><body>\n")

            for img in img_elements:
                src = await img.get_attribute("src")
                if src and src not in seen_imgs and await is_suitable_for_wallpaper(src, page):
                    seen_imgs.add(src)
                    outer_html = await img.evaluate("(element) => element.outerHTML")
                    with open(output_file, "a", encoding='utf-8') as f:
                        f.write(outer_html + "\n")

            with open(output_file, "a", encoding='utf-8') as f:
                f.write("</body></html>")

            print(f"URL {url}: Collected {len(seen_imgs)} suitable images in {output_file}")
        except Exception as e:
            print(f"Error processing {url}: {e}")
        finally:
            await browser.close()

async def main():
    urls = [
        "https://lexica.art"
    ]
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Process all URLs concurrently with a semaphore to limit concurrent browsers
    semaphore = asyncio.Semaphore(3)  # Limit to 3 browsers at a time

    async def sem_scrape(url):
        async with semaphore:
            await scrape_url(url, output_dir=output_dir)

    tasks = [sem_scrape(url) for url in urls]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    output_dir = "output"
    asyncio.run(main())