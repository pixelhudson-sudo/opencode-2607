"""
Upload Helper — semi-automated Amazon Merch upload via browser automation.
Amazon Merch has no public API, so we use Playwright to fill the upload form.
This is SEMI-AUTO: you handle login/captcha, the script fills in listing data.

REQUIRES: pip install playwright && playwright install chromium

How it works:
1. Script opens Chromium with your existing Chrome profile (so you're logged in)
2. For each draft listing, it navigates to Merch upload page
3. Fills title, bullets, description, brand, price, colors, keywords
4. You manually handle image upload (drag/drop) and final submission
5. After manual submit, script captures the ASIN and updates the tracker
"""

import json
import time
import sys
from pathlib import Path
from typing import Optional

try:
    from playwright.sync_api import sync_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("[WARNING] Playwright not installed. Run: pip install playwright && playwright install chromium")


class MerchUploadHelper:
    """
    Semi-automated upload helper for Amazon Merch on Demand.
    Uses your existing Chrome profile so you stay logged in.
    """

    MERCH_URL = "https://merch.amazon.com/"
    UPLOAD_URL = "https://merch.amazon.com/create"
    DASHBOARD_URL = "https://merch.amazon.com/dashboard"

    def __init__(self, chrome_profile_path: Optional[str] = None):
        """
        chrome_profile_path: Path to your Chrome user data directory.
        On Mac: ~/Library/Application Support/Google/Chrome
        On Windows: %LOCALAPPDATA%\Google\Chrome\User Data
        If None, uses a fresh temporary profile (you'll need to log in).
        """
        self.profile_path = chrome_profile_path
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None

    def start(self):
        """Launch browser and navigate to Merch dashboard."""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not installed")

        self.playwright = sync_playwright().start()

        launch_args = {"headless": False, "slow_mo": 100}
        if self.profile_path:
            launch_args["args"] = [f"--user-data-dir={self.profile_path}"]

        self.browser = self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.profile_path or "/tmp/merch-profile",
            headless=False,
            slow_mo=100,
        ) if self.profile_path else self.playwright.chromium.launch(**launch_args)

        if self.profile_path:
            self.page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()
        else:
            self.page = self.browser.new_page()

        self.page.goto(self.DASHBOARD_URL)
        input("\n[ACTION REQUIRED] Log in to Amazon Merch, then press ENTER here...")

    def fill_listing(self, listing_data: dict):
        """
        Navigate to create page and fill in all text fields.
        listing_data keys: title, bullets (str with | separators), description,
                           brand, price, colors, keywords
        """
        self.page.goto(self.UPLOAD_URL)
        time.sleep(3)

        # ---- BRAND ----
        brand_el = self.page.locator('input[name="brandName"]')
        if brand_el.count() > 0:
            brand_el.fill(listing_data.get("brand", "Generic Brand"))

        # ---- TITLE ----
        title_el = self.page.locator('input[name="title"]')
        if title_el.count() > 0:
            title_el.fill(listing_data.get("title", ""))

        # ---- BULLETS ----
        bullets_text = listing_data.get("bullets", "")
        bullet_lines = [b.strip() for b in bullets_text.split("|") if b.strip()]
        for i, bullet in enumerate(bullet_lines[:5]):
            field = self.page.locator(f'textarea[name="bullet{i + 1}"]')
            if field.count() > 0:
                field.fill(bullet)

        # ---- DESCRIPTION ----
        desc_el = self.page.locator('textarea[name="description"]')
        if desc_el.count() > 0:
            desc_el.fill(listing_data.get("description", ""))

        # ---- PRICE (select dropdown) ----
        price = listing_data.get("price", 19.99)
        price_el = self.page.locator('select[name="price"]')
        if price_el.count() > 0:
            price_options = price_el.locator("option")
            option_count = price_options.count()
            # Try to select closest price
            for i in range(option_count):
                opt_text = price_options.nth(i).text_content()
                if opt_text and str(price) in opt_text:
                    price_el.select_option(value=price_options.nth(i).get_attribute("value") or "")
                    break

        # ---- COLORS (checkboxes) ----
        colors = listing_data.get("colors", "Black,Navy,Charcoal")
        for color in colors.split(","):
            color = color.strip()
            cb = self.page.locator(f'label:has-text("{color}") input[type="checkbox"]')
            if cb.count() > 0:
                cb.check()

        # ---- KEYWORDS (backend search terms) ----
        kw_el = self.page.locator('textarea[name="searchTerms"]')
        if kw_el.count() > 0:
            kw_el.fill(listing_data.get("keywords", ""))

        # ---- FIT TYPES ----
        fits = listing_data.get("fits", "Men,Women,Youth")
        for fit in fits.split(","):
            fit = fit.strip()
            cb = self.page.locator(f'label:has-text("{fit}") input[type="checkbox"]')
            if cb.count() > 0:
                cb.check()

        print("\n[DONE] All text fields filled.")
        print("[NEXT] Upload your design image (drag & drop), review everything, and submit.")
        print("[NEXT] After publishing, copy the ASIN from the dashboard.")
        print("[NEXT] Run: tracker.publish_listing(listing_id, asin='B0XXXXXXX', url='...')\n")

        asin = input("[OPTIONAL] Paste ASIN now (or press ENTER to skip): ").strip()
        return asin if asin else None

    def batch_upload(self, listings: list[dict]):
        """Process multiple listings one by one."""
        results = []
        for i, listing in enumerate(listings, 1):
            print(f"\n{'='*60}")
            print(f"LISTING {i}/{len(listings)}: {listing.get('title', 'Untitled')[:60]}...")
            print(f"{'='*60}")

            asin = self.fill_listing(listing)
            results.append({**listing, "asin": asin})

            if i < len(listings):
                cont = input("\nContinue to next listing? [Y/n]: ").strip().lower()
                if cont == "n":
                    break

        return results

    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()


def load_drafts_from_tracker(db_path: str) -> list[dict]:
    """Load draft listings from the SQLite tracker."""
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM listings WHERE status = 'draft'"
    ).fetchall()
    conn.close()

    listings = []
    for row in rows:
        listings.append({
            "id": row["id"],
            "design_id": row["design_id"],
            "title": row["title"],
            "bullets": row["bullets"],
            "description": row["description"],
            "keywords": row["backend_terms"],
            "price": row["price"],
            "brand": "Generic Brand",
            "colors": "Black,Navy,Charcoal,Dark Heather",
            "fits": "Men,Women",
        })
    return listings


if __name__ == "__main__":
    import sys

    tracker_db = str(Path(__file__).parent.parent / "tracker" / "merch_tracker.db")

    if not Path(tracker_db).exists():
        print(f"[ERROR] Tracker DB not found at {tracker_db}")
        print("Run tracker.py first to set up your listings.")
        sys.exit(1)

    drafts = load_drafts_from_tracker(tracker_db)
    if not drafts:
        print("[INFO] No draft listings found in tracker.")
        sys.exit(0)

    print(f"[INFO] Found {len(drafts)} draft listings ready to upload.\n")
    for d in drafts:
        print(f"  #{d['id']}: {d['title'][:70]} — ${d['price']:.2f}")

    print("\n[NOTE] This is semi-automated. You handle: login, image upload, final submit.")
    print("[NOTE] Script handles: all text fields, checkboxes, pricing.\n")

    input("Press ENTER to launch browser...")

    helper = MerchUploadHelper()
    helper.start()
    results = helper.batch_upload(drafts)

    # Save results
    output_path = Path(__file__).parent.parent / "tracker" / "upload_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n[DONE] Results saved to {output_path}")
    print("[ACTION] For each published listing, update your tracker:")
    print("  python -c \"from tracker import Tracker; t = Tracker(); t.publish_listing(ID, asin='B0XXXXX', url='...')\"")

    helper.close()
