import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def test_mhhauto():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
            ],
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
        )
        page = await context.new_page()
        stealth = Stealth()
        await stealth.apply_stealth_async(page)

        print("Navigating to mhhauto.com/search/?q=cx-9 ...")
        await page.goto("https://mhhauto.com/search/?q=cx-9", wait_until="domcontentloaded")

        # Wait for Cloudflare challenge to potentially resolve
        for i in range(10):
            await asyncio.sleep(3)
            title = await page.title()
            print(f"  [{i*3}s] title: {title}")
            if "Just a moment" not in title:
                break

        url = page.url
        title = await page.title()
        content = await page.inner_text("body")
        print(f"\nFinal URL: {url}")
        print(f"Title: {title}")
        print(f"Content length: {len(content)}")

        if "Just a moment" not in title:
            print(f"\nContent preview:\n{content[:2000]}")

            links = await page.evaluate("""
                Array.from(document.querySelectorAll("a")).map(a => [a.href, a.innerText.trim()])
                    .filter(([href]) => href.includes('Thread'))
            """)
            seen = set()
            for href, text in links[:20]:
                if href not in seen and text:
                    seen.add(href)
                    print(f"  {text[:100]}")
                    print(f"  {href}")
                    print()
        else:
            print("\nFailed to bypass Cloudflare challenge after 30s")

        await page.screenshot(path="/Users/patricktrang/opencode-2607/mhhauto_playwright.png", full_page=True)
        print("Screenshot saved to mhhauto_playwright.png")
        await browser.close()

asyncio.run(test_mhhauto())