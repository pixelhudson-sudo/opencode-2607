"""
Amazon Merch Scraper — scrapes public listing data from search results.
Uses rotating user agents and polite delays to avoid rate limiting.
Best used on Merch by Amazon search pages: amazon.com/s?k=t-shirt+[niche]&rh=n:10445813011
"""

import requests
import time
import random
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from typing import Optional

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
]


@dataclass
class Listing:
    title: str
    brand: str
    price: Optional[float]
    bsr: Optional[str]
    rating: Optional[float]
    review_count: Optional[int]
    img_url: Optional[str]
    url: Optional[str]
    scraped_at: str


class AmazonMerchScraper:
    def __init__(self, delay_min: float = 2.0, delay_max: float = 5.0):
        self.session = requests.Session()
        self.delay_min = delay_min
        self.delay_max = delay_max

    def _headers(self) -> dict:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def _polite_sleep(self):
        time.sleep(random.uniform(self.delay_min, self.delay_max))

    def search(self, keyword: str, pages: int = 3) -> list[Listing]:
        """
        Search Amazon Merch for a keyword and scrape listing data.
        Amazon Merch products live under node ID 10445813011.
        """
        all_listings = []

        for page in range(1, pages + 1):
            url = f"https://www.amazon.com/s?k=t-shirt+{keyword.replace(' ', '+')}&rh=n:10445813011&page={page}"
            listings = self._scrape_page(url)
            all_listings.extend(listings)

            if page < pages:
                self._polite_sleep()

        return all_listings

    def scrape_bestsellers(self, category: str = "novelty") -> list[Listing]:
        """Scrape the Amazon Merch bestsellers page for a given category."""
        category_map = {
            "novelty": "10445813011",
            "funny": "1045642",
            "sports": "1045648",
            "animals": "1045650",
        }
        node = category_map.get(category, "10445813011")
        url = f"https://www.amazon.com/Best-Sellers-Clothing/zgbs/fashion/{node}"
        return self._scrape_page(url)

    def _scrape_page(self, url: str) -> list[Listing]:
        listings = []
        try:
            resp = self.session.get(url, headers=self._headers(), timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            for card in soup.select('[data-component-type="s-search-result"]'):
                listing = self._parse_card(card)
                if listing and listing.title:
                    listings.append(listing)

        except requests.RequestException as e:
            print(f"[SCRAPER ERROR] {url}: {e}")

        return listings

    def _parse_card(self, card) -> Optional[Listing]:
        try:
            title_elem = card.select_one("h2 a span")
            title = title_elem.text.strip() if title_elem else None
            if not title:
                return None

            price_whole = card.select_one(".a-price-whole")
            price_fraction = card.select_one(".a-price-fraction")
            price = None
            if price_whole:
                whole = price_whole.text.strip().replace(",", "")
                frac = price_fraction.text.strip() if price_fraction else "00"
                price = float(f"{whole}.{frac}")

            rating_elem = card.select_one(".a-icon-alt")
            rating = None
            if rating_elem:
                match = re.search(r"(\d+\.?\d*)", rating_elem.text)
                if match:
                    rating = float(match.group(1))

            review_elem = card.select_one('[aria-label*="stars"] + span')
            review_count = None
            if not review_elem:
                review_elem = card.select_one(".a-size-base.s-underline-text")
            if review_elem:
                match = re.search(r"([\d,]+)", review_elem.text)
                if match:
                    review_count = int(match.group(1).replace(",", ""))

            img_elem = card.select_one("img.s-image")
            img_url = img_elem.get("src") if img_elem else None

            link_elem = card.select_one("a.a-link-normal.s-no-outline")
            url = None
            if link_elem:
                href = link_elem.get("href", "")
                url = f"https://www.amazon.com{href}" if href.startswith("/") else href

            return Listing(
                title=title,
                brand="Generic",
                price=price,
                bsr=None,
                rating=rating,
                review_count=review_count,
                img_url=img_url,
                url=url,
                scraped_at=datetime.now().isoformat(),
            )
        except Exception as e:
            print(f"[PARSE ERROR] {e}")
            return None

    def to_json(self, listings: list[Listing], filepath: str):
        with open(filepath, "w") as f:
            json.dump([asdict(l) for l in listings], f, indent=2)

    def to_raw_text(self, listings: list[Listing]) -> str:
        """Dump listings as raw text for feeding into the AI scraper-parser prompt."""
        lines = []
        for i, l in enumerate(listings, 1):
            lines.append(f"---ITEM_{i}---")
            lines.append(f"TITLE: {l.title}")
            lines.append(f"BRAND: {l.brand}")
            lines.append(f"PRICE: ${l.price:.2f}" if l.price else "PRICE: N/A")
            lines.append(f"RATING: {l.rating} ({l.review_count} reviews)" if l.rating else "RATING: N/A")
            lines.append(f"BSR: {l.bsr or 'N/A'}")
            lines.append(f"URL: {l.url or 'N/A'}")
            lines.append(f"IMG: {l.img_url or 'N/A'}")
            lines.append("")
        return "\n".join(lines)


if __name__ == "__main__":
    scraper = AmazonMerchScraper(delay_min=2.0, delay_max=4.0)

    keywords = ["funny nurse", "dog mom", "teacher life", "hiking lover"]
    all_data = []

    for kw in keywords:
        print(f"[SCRAPING] '{kw}'...")
        listings = scraper.search(kw, pages=2)
        all_data.extend(listings)
        print(f"  -> Got {len(listings)} listings")
        time.sleep(3)

    scraper.to_json(all_data, "scraped_listings.json")
    print(f"\n[DONE] {len(all_data)} total listings saved to scraped_listings.json")

    raw = scraper.to_raw_text(all_data)
    with open("scraped_raw.txt", "w") as f:
        f.write(raw)
    print("[DONE] Raw text saved to scraped_raw.txt (feed this to 02-scraper-parser.txt)")
