# import asyncio
# from playwright.async_api import async_playwright

# async def save_html():
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=True)
#         page = await browser.new_page()
#         await page.goto("https://lexica.art/", wait_until="networkidle")
#         await asyncio.sleep(5)  # allow JS fully load
#         html = await page.content()
#         with open("lexica_rendered.html", "w", encoding="utf-8") as f:
#             f.write(html)
#         await browser.close()

# asyncio.run(save_html())
# import asyncio
# from playwright.async_api import async_playwright

# async def main():
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)
#         page = await browser.new_page()
#         await page.goto("https://lexica.art/", wait_until="networkidle")
#         await asyncio.sleep(5)

#         # Auto scroll
#         for _ in range(50):  # number of scrolls
#             await page.mouse.wheel(0, 5000)
#             await asyncio.sleep(2)

#         # Save rendered HTML after scrolling
#         content = await page.content()
#         with open("lex_full.html", "w", encoding='utf-8') as f:
#             f.write(content)

#         await browser.close()

# asyncio.run(main())
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://lexica.art/", wait_until="networkidle")
        await asyncio.sleep(5)

        seen_imgs = set()

        with open("lex_live.html", "w", encoding='utf-8') as f:
            f.write("<html><body>\n")  # Start writing HTML

        for i in range(50):  # number of scroll steps
            await page.mouse.wheel(0, 5000)
            await asyncio.sleep(2)

            # Extract all img elements currently in DOM
            img_elements = await page.query_selector_all("img")

            for img in img_elements:
                src = await img.get_attribute("src")
                if src and src not in seen_imgs:
                    seen_imgs.add(src)
                    # Get outer HTML of image tag
                    outer_html = await img.evaluate("(element) => element.outerHTML")
                    with open("lex_live.html", "a", encoding='utf-8') as f:
                        f.write(outer_html + "\n")

            print(f"Scroll {i+1}: Total collected images: {len(seen_imgs)}")

        with open("lex_live.html", "a", encoding='utf-8') as f:
            f.write("</body></html>")  # Close HTML

        await browser.close()

asyncio.run(main())
