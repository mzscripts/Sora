import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://lexica.art/?q=317a5fe9-4600-4829-b67d-dba07887ba6e", wait_until="networkidle")
        await asyncio.sleep(5)

        seen_imgs = set()

        with open("lexica_scraped.html", "w", encoding='utf-8') as f:
            f.write("<html><body>\n")  # Start writing HTML

        for i in range(50):  # number of scroll steps
            await page.mouse.wheel(0, 5000)
            await asyncio.sleep(2)

            # Extract all image containers (they are inside div with class 'block relative group ...')
            containers = await page.query_selector_all("div.block.relative.group")

            for container in containers:
                # Get image src
                img = await container.query_selector("img")
                src = await img.get_attribute("src") if img else None

                # Get prompt href
                a_tag = await container.query_selector("a")
                href = await a_tag.get_attribute("href") if a_tag else None

                if src and src not in seen_imgs:
                    seen_imgs.add(src)

                    with open("lexica_scraped.html", "a", encoding='utf-8') as f:
                        f.write(f'<a href="{href}"><img src="{src}" width="520" height="720"></a>\n')

            print(f"Scroll {i+1}: Total collected images: {len(seen_imgs)}")

        with open("lexica_scraped.html", "a", encoding='utf-8') as f:
            f.write("</body></html>")  # Close HTML

        await browser.close()

asyncio.run(main())
