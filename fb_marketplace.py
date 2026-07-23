"""
fb_marketplace.py — Facebook Marketplace scraper engine.

Three backends, escalating reliability:
  1. playwright  — browser automation with stealth (primary)
  2. curl_cffi   — HTTP impersonation (lightweight, no browser)
  3. requests    — direct fallback

Business features from the Koerner Office playbook:
  - Deal scoring (free / mustgo / cheap / damaged keyword weighting)
  - Seller monitoring (new listings from tracked profiles)
  - Lead detection (wanted / need / looking for posts)
  - Scheduled recurring scrapes via APScheduler

Usage:
  python3 fb_marketplace.py search "shed" --radius 50 --zip 75201
  python3 fb_marketplace.py monitor --sellers sellers.txt --interval 60
  python3 fb_marketplace.py export --format csv
"""

from __future__ import annotations

import asyncio
import csv
import json
import logging
import os
import re
import sqlite3
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlencode

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("fb_marketplace")

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Listing:
    title: str
    price: float
    currency: str = "USD"
    location: str = ""
    url: str = ""
    image_url: str = ""
    description: str = ""
    posted_at: Optional[datetime] = None
    seller_name: str = ""
    seller_url: str = ""
    category: str = ""
    condition: str = ""
    scrape_source: str = ""
    raw: dict = field(default_factory=dict)

    @property
    def deal_score(self) -> float:
        score = 50.0
        title_lower = (self.title + " " + self.description).lower()

        bonus_map = {
            "free": 30, "must go": 25, "mustgo": 25,
            "moving": 15, "estate sale": 15, "damaged": 10,
            "cheap": 10, "as is": 5, "must sell": 20, "need gone": 20,
            "price drop": 10, "best offer": 5, "negotiable": 3,
        }
        for kw, bonus in bonus_map.items():
            if kw in title_lower:
                score += bonus

        if self.price is not None:
            if self.price <= 0:
                score += 25
            elif self.price <= 50:
                score += 15
            elif self.price <= 200:
                score += 5

        if self.location and self.location.strip():
            score += 5
        if self.image_url:
            score += 3

        return min(score, 100)

    @property
    def is_free(self) -> bool:
        return self.price is not None and self.price <= 0


@dataclass
class SearchResult:
    query: str
    location: str
    radius_km: int
    listings: list[Listing] = field(default_factory=list)
    scraped_at: datetime = field(default_factory=datetime.now)
    total_found: int = 0
    elapsed_ms: int = 0

    def top_deals(self, n: int = 10) -> list[Listing]:
        return sorted(self.listings, key=lambda l: l.deal_score, reverse=True)[:n]


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

class DealDatabase:
    def __init__(self, db_path: str = "fb_deals.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS listings (
                    url TEXT PRIMARY KEY,
                    title TEXT, price REAL, currency TEXT,
                    location TEXT, description TEXT,
                    posted_at TEXT, seller_name TEXT, seller_url TEXT,
                    category TEXT, condition TEXT,
                    deal_score REAL, is_free INTEGER,
                    first_seen TEXT, last_seen TEXT, scrape_count INTEGER DEFAULT 1
                );
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    listing_url TEXT, alert_type TEXT,
                    score REAL, created_at TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_listings_score ON listings(deal_score DESC);
                CREATE INDEX IF NOT EXISTS idx_listings_seen ON listings(last_seen DESC);
            """)

    def insert_listing(self, listing: Listing) -> bool:
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            existing = conn.execute(
                "SELECT url FROM listings WHERE url = ?", (listing.url,)
            ).fetchone()
            if existing:
                conn.execute(
                    "UPDATE listings SET last_seen = ?, scrape_count = scrape_count + 1 WHERE url = ?",
                    (now, listing.url),
                )
                return False
            conn.execute(
                """INSERT INTO listings
                   (url, title, price, currency, location, description, posted_at,
                    seller_name, seller_url, category, condition,
                    deal_score, is_free, first_seen, last_seen)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    listing.url, listing.title, listing.price, listing.currency,
                    listing.location, listing.description,
                    listing.posted_at.isoformat() if listing.posted_at else None,
                    listing.seller_name, listing.seller_url,
                    listing.category, listing.condition,
                    listing.deal_score, 1 if listing.is_free else 0,
                    now, now,
                ),
            )
            return True

    def get_new_alerts(self, min_score: float = 70, since_hours: int = 24) -> list[Listing]:
        cutoff = (datetime.now() - timedelta(hours=since_hours)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """SELECT title, price, currency, location, url, description,
                          seller_name, seller_url, category, deal_score
                   FROM listings WHERE deal_score >= ? AND first_seen >= ?
                   ORDER BY deal_score DESC LIMIT 50""",
                (min_score, cutoff),
            ).fetchall()
        return [
            Listing(
                title=r[0], price=r[1], currency=r[2], location=r[3],
                url=r[4], description=r[5], seller_name=r[6],
                seller_url=r[7], category=r[8],
            )
            for r in rows
        ]

    def export_csv(self, path: str, min_score: float = 0):
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """SELECT title, price, currency, location, url, deal_score, is_free,
                          first_seen, seller_name
                   FROM listings WHERE deal_score >= ?
                   ORDER BY deal_score DESC""",
                (min_score,),
            ).fetchall()
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["Title", "Price", "Currency", "Location", "URL",
                         "Deal Score", "Free", "First Seen", "Seller"])
            for r in rows:
                w.writerow(r)
        log.info("Exported %s deals to %s", len(rows), path)


# ---------------------------------------------------------------------------
# Scraper backends
# ---------------------------------------------------------------------------

class ScraperConfig:
    def __init__(
        self,
        radius_km: int = 80,
        max_listings: int = 100,
        min_price: float = 0,
        max_price: float = 100_000,
        days_old: int = 7,
        headless: bool = True,
        proxy: Optional[str] = None,
        user_data_dir: Optional[str] = None,
        cookies_file: Optional[str] = None,
    ):
        self.radius_km = radius_km
        self.max_listings = max_listings
        self.min_price = min_price
        self.max_price = max_price
        self.days_old = days_old
        self.headless = headless
        self.proxy = proxy
        self.user_data_dir = user_data_dir
        self.cookies_file = cookies_file


COOKIES_FILE_DEFAULT = "fb_cookies.json"
LOGIN_CHECK_TIMEOUT = 8000


class PlaywrightBackend:
    """Browser automation via Playwright with stealth. Primary backend."""

    def __init__(self, config: ScraperConfig):
        self.config = config
        self.browser = None
        self.context = None
        self._pw = None
        self.stealth = None

    async def _launch(self):
        from playwright.async_api import async_playwright
        from playwright_stealth import Stealth

        self._pw = await async_playwright().start()

        user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )

        launch_args = [
            "--no-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-web-security",
            f"--window-size={1920},{1080}",
        ]
        if self.config.proxy:
            launch_args.append(f"--proxy-server={self.config.proxy}")

        if self.config.user_data_dir:
            udir = os.path.expanduser(self.config.user_data_dir)
            os.makedirs(udir, exist_ok=True)
            self.context = await self._pw.chromium.launch_persistent_context(
                user_data_dir=udir,
                headless=self.config.headless,
                args=launch_args,
                user_agent=user_agent,
                viewport={"width": 1920, "height": 1080},
                locale="en-US",
            )
            log.info("Launched persistent context at %s", udir)
        else:
            self.browser = await self._pw.chromium.launch(
                headless=self.config.headless,
                args=launch_args,
            )
            self.context = await self.browser.new_context(
                user_agent=user_agent,
                viewport={"width": 1920, "height": 1080},
                locale="en-US",
            )

        self.stealth = Stealth()

        cookies_file = self.config.cookies_file or COOKIES_FILE_DEFAULT
        if os.path.exists(cookies_file) and not self.config.user_data_dir:
            await self._load_cookies(cookies_file)
            log.info("Loaded cookies from %s", cookies_file)

    async def _load_cookies(self, path: str):
        try:
            with open(path) as f:
                cookies = json.load(f)
            if cookies:
                await self.context.add_cookies(cookies)
                log.info("Restored %s cookies", len(cookies))
        except Exception as e:
            log.warning("Failed to load cookies: %s", e)

    async def _save_cookies(self, path: str):
        try:
            cookies = await self.context.cookies()
            with open(path, "w") as f:
                json.dump(cookies, f, indent=2)
            log.info("Saved %s cookies to %s", len(cookies), path)
        except Exception as e:
            log.warning("Failed to save cookies: %s", e)

    async def _page(self):
        page = await self.context.new_page()
        if self.stealth:
            await self.stealth.apply_stealth_async(page)
        return page

    async def login(self, email: str = "") -> bool:
        """Open Facebook, let user log in manually. Saves session afterwards."""
        if not self.context:
            await self._launch()

        page = await self._page()
        await page.goto("https://www.facebook.com", wait_until="domcontentloaded")
        await asyncio.sleep(2)

        if email:
            try:
                await page.fill("input[name=email]", email, timeout=5000)
                log.info("Pre-filled email field")
            except Exception:
                pass

        current_url = page.url
        log.info("Facebook page loaded: %s", current_url)

        if "checkpoint" in current_url or "login" in current_url:
            log.info("Login required. Waiting for manual login...")
            print("\n=== LOGIN REQUIRED ===")
            print("A browser window is open. Log in to Facebook manually.")
            if not email:
                print("Tip: pass --email to pre-fill the email field.")
            print("The scraper will detect when you're logged in.\n")

            for i in range(120):
                await asyncio.sleep(2)
                current = page.url
                if "checkpoint" not in current and "login" not in current:
                    log.info("Login detected after ~%ss", i * 2)
                    break
                if i % 15 == 0 and i > 0:
                    print(f"  Still waiting... ({i * 2}s elapsed)")
            else:
                log.warning("Login not detected after 240s")
                await page.close()
                return False
        else:
            log.info("Already logged in")

        await asyncio.sleep(2)

        self.config.cookies_file = self.config.cookies_file or COOKIES_FILE_DEFAULT
        await self._save_cookies(self.config.cookies_file)

        if self.config.user_data_dir:
            log.info("Session saved in persistent profile: %s",
                     self.config.user_data_dir)

        await page.close()
        return True

    def _build_search_url(self, query: str) -> str:
        params = {
            "radius_km": self.config.radius_km,
            "min_price": self.config.min_price,
            "max_price": self.config.max_price,
            "daysSinceListed": self.config.days_old,
            "sortBy": "creation_time_descend",
        }
        if query:
            params["query"] = query
        return f"https://www.facebook.com/marketplace/search?{urlencode(params)}"

    async def search(self, query: str) -> SearchResult:
        t0 = time.monotonic()
        result = SearchResult(query=query, location="",
                              radius_km=self.config.radius_km)

        if not self.context:
            await self._launch()

        page = await self._page()
        url = self._build_search_url(query)
        log.info("Navigating to %s", url)

        try:
            resp = await page.goto(url, wait_until="domcontentloaded",
                                   timeout=30000)
            await asyncio.sleep(5)

            login_detected = await self._check_login_wall(page)
            if login_detected:
                log.warning("Login wall detected — no listings will be visible")
                cookies_file = self.config.cookies_file or COOKIES_FILE_DEFAULT
                if os.path.exists(cookies_file) or self.config.user_data_dir:
                    log.warning("Session exists but might be expired. "
                                "Run 'login' to refresh.")
                result.listings = []
                result.total_found = 0
                result.elapsed_ms = int((time.monotonic() - t0) * 1000)
                return result

            for i in range(3):
                await page.evaluate("window.scrollBy(0, 800)")
                await asyncio.sleep(2)

            html = await page.content()
            parsed = self._parse_listings(html)
            result.listings = parsed[:self.config.max_listings]
            result.total_found = len(parsed)

        except Exception as e:
            log.warning("playwright search error: %s", e)
        finally:
            await page.close()

        result.elapsed_ms = int((time.monotonic() - t0) * 1000)
        log.info("playwright found %s listings in %.1fs",
                 result.total_found, result.elapsed_ms / 1000)
        return result

    async def _check_login_wall(self, page) -> bool:
        try:
            text = await page.inner_text("body", timeout=LOGIN_CHECK_TIMEOUT)
            text_lower = text.lower()
            triggers = [
                "log in", "create new account", "sign up for facebook",
                "you must log in", "login to continue",
            ]
            for t in triggers:
                if t in text_lower:
                    return True
            return False
        except Exception:
            return False

    def _parse_listings(self, html: str) -> list[Listing]:
        """Extract listings from Facebook Marketplace HTML.

        Facebook obfuscates class names so we rely on structural patterns:
        - Links containing /marketplace/item/ numeric IDs
        - JSON-like blobs embedded in script tags
        - aria-labels and img alt text fallbacks
        """
        listings = []
        seen = set()

        # Strategy 1: structured data in script tags (JSON.parse or __NEXT_DATA__)
        fb_json = re.search(
            r'<script[^>]*>(\s*window\.__INITIAL_STATE__\s*=\s*|{\s*"props"\s*:)(.+?)</script>',
            html, re.DOTALL
        )
        if fb_json:
            try:
                raw = fb_json.group(2).strip().rstrip(";")
                data = json.loads(raw)
                for item in self._walk_fb_json(data):
                    if item["url"] not in seen:
                        seen.add(item["url"])
                        listings.append(Listing(
                            title=item["title"], price=item["price"],
                            url=item["url"], image_url=item.get("img", ""),
                            location=item.get("location", ""),
                            scrape_source="playwright_fbjson",
                        ))
            except (json.JSONDecodeError, KeyError):
                pass

        # Strategy 2: anchor tags with marketplace item IDs
        if not listings:
            for a_match in re.finditer(
                r'href=["\'](/marketplace/item/(\d+))["\'][^>]*>',
                html
            ):
                item_id = a_match.group(2)
                if item_id in seen:
                    continue
                seen.add(item_id)
                full_url = f"https://www.facebook.com/marketplace/item/{item_id}"
                listings.append(Listing(
                    title="",
                    price=0.0,
                    url=full_url,
                    scrape_source="playwright_anchor",
                ))

            # Fill in titles and prices from surrounding text
            for listing in listings:
                item_id = listing.url.split("/item/")[-1].split("?")[0]
                surrounding = self._get_context(html, item_id)
                price_m = re.search(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', surrounding)
                if price_m:
                    listing.price = float(price_m.group(1).replace(",", ""))
                title_m = re.search(r'(?:alt|aria-label)=["\']([^"\']{10,})', surrounding)
                if title_m:
                    listing.title = title_m.group(1).strip()
                if not listing.title:
                    span_m = re.search(rf'{item_id}[^<]*<span[^>]*>([^<]+)', surrounding)
                    if span_m:
                        listing.title = span_m.group(1).strip()

        return listings

    def _walk_fb_json(self, obj, depth=0):
        if depth > 10:
            return
        if isinstance(obj, dict):
            if all(k in obj for k in ("node",) if k):
                yield from self._walk_fb_json(obj.get("node"), depth + 1)
            if obj.get("__typename") == "MarketplaceListing" or "listing_id" in obj:
                item = {
                    "title": obj.get("title", "") or obj.get("name", "") or "",
                    "price": self._parse_price(obj),
                    "url": obj.get("url", "") or obj.get("link", "") or "",
                    "img": self._parse_image(obj),
                    "location": obj.get("location", {}).get("name", "") if isinstance(obj.get("location"), dict) else "",
                }
                yield item
            for v in obj.values():
                yield from self._walk_fb_json(v, depth + 1)
        elif isinstance(obj, list):
            for v in obj:
                yield from self._walk_fb_json(v, depth + 1)

    def _parse_price(self, obj):
        price = obj.get("price", obj.get("listing_price", obj.get("formatted_price", "")))
        if isinstance(price, str):
            m = re.search(r'(\d+(?:,\d{3})*(?:\.\d{2})?)', price)
            return float(m.group(1).replace(",", "")) if m else 0.0
        if isinstance(price, (int, float)):
            return float(price)
        return 0.0

    def _parse_image(self, obj):
        img = obj.get("image", obj.get("primary_image", obj.get("photo", {})))
        if isinstance(img, dict):
            return (img.get("uri") or img.get("src") or
                    (img.get("image", {}).get("uri") if isinstance(img.get("image"), dict) else "") or
                    "")
        return str(img) if img else ""

    def _get_context(self, html: str, item_id: str, chars: int = 500) -> str:
        idx = html.find(item_id)
        if idx == -1:
            return ""
        start = max(0, idx - chars)
        return html[start:idx + chars]

    async def close(self):
        if self.browser:
            await self.browser.close()
        if hasattr(self, "_pw"):
            await self._pw.stop()


class CurlCffiBackend:
    """Lightweight HTTP-impersonation backend. Useful headless testing."""

    def __init__(self, config: ScraperConfig):
        self.config = config

    def search(self, query: str) -> SearchResult:
        import curl_cffi.requests as curl_requests

        t0 = time.monotonic()
        result = SearchResult(query=query, location="",
                              radius_km=self.config.radius_km)

        params = {
            "radius_km": self.config.radius_km,
            "min_price": self.config.min_price,
            "max_price": self.config.max_price,
            "daysSinceListed": self.config.days_old,
            "sortBy": "creation_time_descend",
            "query": query,
        }
        url = f"https://www.facebook.com/marketplace/search?{urlencode(params)}"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "DNT": "1",
        }

        try:
            resp = curl_requests.get(url, headers=headers,
                                     impersonate="chrome124", timeout=30)
            resp.raise_for_status()
            if "marketplace" not in resp.text.lower() or "login" in resp.text.lower():
                log.warning("curl_cffi got login wall or non-marketplace response")
            else:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, "html.parser")
                for link in soup.find_all("a", href=re.compile(r"/marketplace/item/\d+")):
                    listing = Listing(
                        title=link.get_text(strip=True)[:100],
                        price=0.0,
                        url=f"https://www.facebook.com{link['href']}" if link.get("href", "").startswith("/") else link.get("href", ""),
                        scrape_source="curl_cffi",
                        category=query,
                    )
                    result.listings.append(listing)
                result.total_found = len(result.listings)
        except Exception as e:
            log.warning("curl_cffi failed: %s", e)

        result.elapsed_ms = int((time.monotonic() - t0) * 1000)
        log.info("curl_cffi found %s listings in %.1fs",
                 result.total_found, result.elapsed_ms / 1000)
        return result


# ---------------------------------------------------------------------------
# Combined scraper
# ---------------------------------------------------------------------------

class FacebookMarketplaceScraper:
    def __init__(self, config: Optional[ScraperConfig] = None):
        self.config = config or ScraperConfig()
        self.db = DealDatabase()
        self._playwright: Optional[PlaywrightBackend] = None

    async def _get_playwright(self) -> PlaywrightBackend:
        if not self._playwright:
            self._playwright = PlaywrightBackend(self.config)
        return self._playwright

    async def login(self, email: str = "") -> bool:
        pw = await self._get_playwright()
        return await pw.login(email=email)

    async def search(self, query: str) -> SearchResult:
        try:
            pw = await self._get_playwright()
            result = await pw.search(query)
            if result.total_found > 0:
                self._persist(result)
                return result
            log.info("playwright returned 0 results, trying curl_cffi...")
        except ImportError as e:
            log.warning("playwright not available: %s", e)
        except Exception as e:
            log.warning("playwright failed: %s", e)

        try:
            backend = CurlCffiBackend(self.config)
            result = backend.search(query)
            if result.total_found > 0:
                self._persist(result)
                return result
        except ImportError:
            log.warning("curl_cffi not available")
        except Exception as e:
            log.warning("curl_cffi failed: %s", e)

        log.warning("All backends returned 0 results for query=%s", query)
        return SearchResult(query=query, location="",
                            radius_km=self.config.radius_km)

    def _persist(self, result: SearchResult):
        new_count = 0
        for listing in result.listings:
            if self.db.insert_listing(listing):
                new_count += 1
        if new_count:
            log.info("Persisted %s new listings (%s duplicates skipped)",
                     new_count, len(result.listings) - new_count)

    async def search_multi(self, queries: list[str]) -> list[SearchResult]:
        results = []
        for q in queries:
            r = await self.search(q.strip())
            results.append(r)
            await asyncio.sleep(2)
        return results

    async def close(self):
        if self._playwright:
            await self._playwright.close()

    def export(self, fmt: str = "csv", path: str = "fb_deals_export.csv",
               min_score: float = 0):
        if fmt == "csv":
            self.db.export_csv(path, min_score)
        elif fmt == "json":
            rows = self.db.get_new_alerts(min_score=min_score)
            data = [asdict(r) for r in rows]
            with open(path.replace(".csv", ".json"), "w") as f:
                json.dump(data, f, indent=2, default=str)
            log.info("Exported %s deals to JSON", len(rows))

    def report(self, min_score: float = 60, hours: int = 24) -> str:
        alerts = self.db.get_new_alerts(min_score=min_score, since_hours=hours)
        if not alerts:
            return "No new deals found."
        lines = [
            f"Top Deals (score >= {min_score}, last {hours}h)\n",
            f"{'Score':>5}  {'Price':>8}  {'Title':<50}  {'Location':<20}",
            "-" * 90,
        ]
        for a in alerts:
            price_str = f"${a.price:.0f}" if a.price else "FREE"
            lines.append(
                f"{a.deal_score:>5.0f}  {price_str:>8}  {a.title[:48]:<50}  {a.location[:18]:<20}"
            )
        lines.append(f"\n{len(alerts)} deals found.")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class DealScheduler:
    def __init__(self, scraper: FacebookMarketplaceScraper):
        self.scraper = scraper

    def start(self, queries: list[str], interval_minutes: int = 60):
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        scheduler = AsyncIOScheduler()

        async def job():
            log.info("Scheduled scrape running for %s queries", len(queries))
            for q in queries:
                await self.scraper.search(q)
            new = self.scraper.db.get_new_alerts(min_score=70, since_hours=24)
            if new:
                log.info("ALERT — %s hot deals found!", len(new))
                for d in new[:5]:
                    log.info("  [%.0f] %s — $%s — %s",
                             d.deal_score, d.title[:40], d.price, d.url)

        scheduler.add_job(job, "interval", minutes=interval_minutes)
        scheduler.start()
        return scheduler


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Facebook Marketplace Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  # Log in once (saves session for later use):\n"
            "  python3 fb_marketplace.py login\n\n"
            "  # Login with persistent profile (best for long-term use):\n"
            "  python3 fb_marketplace.py login --profile ~/.fb-scraper-profile\n\n"
            "  # Search (auto-reuses saved cookies):\n"
            "  python3 fb_marketplace.py search \"shed\" --radius 80\n\n"
            "  # Search with persistent profile (no cookies file needed):\n"
            "  python3 fb_marketplace.py search \"toyota\" --profile ~/.fb-scraper-profile --radius 80\n\n"
            "  # Search visible browser (debug):\n"
            "  python3 fb_marketplace.py search \"treadmill\" --visible --radius 50\n\n"
            "  # Multisearch motivated-seller keywords:\n"
            "  python3 fb_marketplace.py multisearch \"couch\"\n\n"
            "  # View scored deals:\n"
            "  python3 fb_marketplace.py report --min-score 70\n\n"
            "  # Run every 60 minutes:\n"
            "  python3 fb_marketplace.py search \"free\" --schedule 60 --profile ~/.fb-scraper-profile\n"
        ),
    )
    parser.add_argument("action", nargs="?", default="search",
                        choices=["search", "multisearch", "report",
                                 "export", "login"])
    parser.add_argument("query", nargs="?", default="shed", help="Search term")
    parser.add_argument("--radius", type=int, default=80)
    parser.add_argument("--max-price", type=float, default=50000)
    parser.add_argument("--min-score", type=float, default=60)
    parser.add_argument("--hours", type=int, default=24)
    parser.add_argument("--format", default="csv", choices=["csv", "json"])
    parser.add_argument("--output", default="fb_deals_export.csv")
    parser.add_argument("--schedule", type=int, default=0,
                        help="Run every N minutes (recurring)")
    parser.add_argument("--visible", action="store_true",
                        help="Run browser visibly (debugging)")
    parser.add_argument("--cookies",
                        help="Path to cookies JSON file (default: fb_cookies.json)")
    parser.add_argument("--profile",
                        help="Chrome profile directory for persistent login "
                             "(best for long-term use)")
    parser.add_argument("--email",
                        help="Email to pre-fill during login")
    args = parser.parse_args()

    config = ScraperConfig(
        radius_km=args.radius,
        max_price=args.max_price,
        headless=not args.visible,
        user_data_dir=args.profile,
        cookies_file=args.cookies,
    )

    async def main():
        scraper = FacebookMarketplaceScraper(config)

        try:
            if args.action == "login":
                ok = await scraper.login(email=args.email or "")
                print("\nLogin OK" if ok else "\nLogin failed or timed out")
                if ok:
                    print("Session saved. Run searches without re-logging in:")
                    if args.profile:
                        print(
                            f"  python3 fb_marketplace.py search "
                            f"\"shed\" --profile {args.profile}"
                        )
                    else:
                        print(
                            "  python3 fb_marketplace.py search \"shed\""
                        )
                return

            if args.action == "search":
                result = await scraper.search(args.query)
                print(f"\nFound {result.total_found} listings for '{args.query}' "
                      f"in {result.elapsed_ms}ms\n")
                for l in result.top_deals(15):
                    free_tag = " FREE" if l.is_free else ""
                    print(f"  [{l.deal_score:3.0f}] ${l.price:<6.0f}{free_tag}  {l.title[:50]}")
                    print(f"        {l.url}")
                    print()

            elif args.action == "multisearch":
                queries = ["free", "mustgo", "cheap", "damaged",
                           "moving", "estate sale", args.query]
                results = await scraper.search_multi(queries)
                all_deals = []
                for r in results:
                    all_deals.extend(r.listings)
                all_deals.sort(key=lambda l: l.deal_score, reverse=True)
                print(f"\nCombined: {len(all_deals)} total listings\n")
                for l in all_deals[:20]:
                    print(f"  [{l.deal_score:3.0f}] ${l.price:<6.0f}  {l.title[:50]}")
                    print(f"        {l.url}")
                    print()

            elif args.action == "report":
                print(scraper.report(min_score=args.min_score, hours=args.hours))

            elif args.action == "export":
                scraper.export(args.format, args.output, args.min_score)

        finally:
            await scraper.close()

    if args.schedule > 0:
        sched = DealScheduler(FacebookMarketplaceScraper(config)).start(
            [args.query], args.schedule
        )
        print(f"Scheduler running every {args.schedule} min. Ctrl+C to stop.")
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            pass
    else:
        asyncio.run(main())
