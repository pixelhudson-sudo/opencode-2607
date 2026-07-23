import asyncio
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

print("Starting UC (undetected-chrome) driver...")
driver = Driver(
    uc=True,
    headless=True,
    browser="chrome",
    no_sandbox=True,
    agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
)

try:
    print("Navigating to mhhauto.com/search/?q=cx-9 ...")
    driver.get("https://mhhauto.com/search/?q=cx-9")

    # Wait for page to resolve
    for i in range(10):
        time.sleep(3)
        title = driver.title
        print(f"  [{i*3}s] title: {title}")
        if "Just a moment" not in title:
            break

    url = driver.current_url
    title = driver.title
    body = driver.find_element(By.TAG_NAME, "body").text
    print(f"\nFinal URL: {url}")
    print(f"Title: {title}")
    print(f"Content length: {len(body)}")

    if "Just a moment" not in title:
        print(f"\nContent preview:\n{body[:2000]}")
        links = driver.find_elements(By.CSS_SELECTOR, "a[href*='Thread']")
        seen = set()
        for link in links[:25]:
            href = link.get_attribute("href")
            text = link.text.strip()
            if href and text and href not in seen:
                seen.add(href)
                print(f"  {text[:100]}")
                print(f"  {href}")
                print()
    else:
        print("\nCloudflare challenge NOT passed after 30s")

    driver.save_screenshot("/Users/patricktrang/opencode-2607/mhhauto_sb.png")
    print("Screenshot saved.")
finally:
    driver.quit()