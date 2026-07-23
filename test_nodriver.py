import asyncio
import nodriver as uc

async def test_mhhauto():
    browser = await uc.start(
        headless=True,
        no_sandbox=True,
        browser_args=[
            "--headless=new",
            "--disable-blink-features=AutomationControlled",
        ],
    )
    try:
        page = await browser.get("https://mhhauto.com/search/?q=cx-9")

        # Wait longer and check if we pass CF
        for i in range(6):
            await page.wait(5)
            title = await page.evaluate("document.title")
            print(f"  [{i*5}s] title: {title}")
            if "Just a moment" not in title:
                break

        content = await page.evaluate("document.body.innerText")
        url = await page.evaluate("location.href")
        print(f"\nFinal URL: {url}")
        print(f"Title: {title}")
        print(f"Content length: {len(content)}")

        if "Just a moment" not in title:
            print(f"\nContent preview:\n{content[:2000]}")
            raw_links = await page.evaluate("""
                Array.from(document.querySelectorAll("a")).map(a => ({
                    href: a.href || '',
                    text: (a.innerText || '').trim()
                })).filter(l => l.href.includes('Thread'))
            """)
            seen = set()
            for l in raw_links:
                h = l.get('href', '')
                t = l.get('text', '')
                if h and h not in seen and t:
                    seen.add(h)
                    print(f"  {t[:100]}")
                    print(f"  {h}")
                    print()

        await page.save_screenshot("/Users/patricktrang/opencode-2607/mhhauto_screenshot.png")
        print("Screenshot saved.")
    finally:
        browser.stop()

asyncio.run(test_mhhauto())