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
        "https://lexica.art/?q=c626a5cd-0d47-47a6-9113-572b5becbd7a",
        "https://lexica.art/?q=07a1c80f-01eb-4c8e-9af9-1bb853008a0c",
        "https://lexica.art/?q=848abab0-1808-4e0b-b8ae-0abb05d3cb37",
        "https://lexica.art/?q=9dfce783-dd1e-40e2-a0bc-fd2901f3dfb9",
        "https://lexica.art/?q=01cdb0ef-bffc-4ba6-83b2-10483e3446e3",
        "https://lexica.art/?q=2c05bffa-2df0-4ec5-8e70-e29eadd40a19",
        "https://lexica.art/?q=265f3b51-25df-4095-88f8-a0dddf3560d5",
        "https://lexica.art/?q=435d729c-6400-46bf-b86d-2d63ccd49aa4",
        "https://lexica.art/?q=0dcaef0c-e532-4ef6-84a9-1908e7a48141",
        "https://lexica.art/?q=212fc945-f438-4a5e-9314-d483fa634608",
        "https://lexica.art/?q=0241bd83-e713-4353-b7dd-efbca9785138",
        "https://lexica.art/?q=3e3e09c3-fcfc-4718-b4da-ff1946629a9c",
        "https://lexica.art/?q=196f5f19-78a8-4850-9bf3-b5cc7c898ba5",
        "https://lexica.art/?q=388fc3b8-9abd-4299-b7b3-9e6703e7458c",
        "https://lexica.art/?q=19bc1ee1-8678-4b5f-b43d-5fea93ca96c3",
        "https://lexica.art/?q=33cc3996-0f4c-4504-9eee-fb70977c7b92",
        "https://lexica.art/?q=7d3992f8-535f-4577-8cd7-534e13d60697",
        "https://lexica.art/?q=f527fc34-ad1e-49a8-bc03-d42d0b0116dc",
        "https://lexica.art/?q=d0d5ee39-c6fa-4234-b243-c17e6fc493e8",
        "https://lexica.art/?q=880c3895-b9e7-4bb9-bb20-b15f9657d61d",
        "https://lexica.art/?q=2dda4659-d2ed-492f-a01a-cc3701de2781",
        "https://lexica.art/?q=10fbd7bd-ca1b-4627-8df7-e0f58a7e4e38",
        "https://lexica.art/?q=b03930ad-afaf-4ee4-9cba-011fc89eefb4",
        "https://lexica.art/?q=05437f80-607a-4311-aa3f-08f6b80fbd26",
        "https://lexica.art/?q=41df0c49-e1e9-490e-b2c9-9a0dd4567771",
        "https://lexica.art/?q=0d10531c-9f18-4f50-8285-9205510b4c0b",
        "https://lexica.art/?q=acc66017-5f11-47f2-a487-2068dfd4cf6a",
        "https://lexica.art/?q=521afb7c-217a-49ed-a44d-bc27c403f142",
        "https://lexica.art/?q=b1ece9fa-3ede-4057-86e3-cc7f3008f7d0",
        "https://lexica.art/?q=b19dd898-985c-4597-b4ad-e336da2ff0eb",
        "https://lexica.art/?q=cc347176-92e7-4e2e-a08d-51f4316939bc",
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