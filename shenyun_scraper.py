#!/usr/bin/env python3
"""
Shen Yun Showtime Scraper
==========================
Scrapes showtimes from all Shen Yun city pages every 3 days,
stores them in SQLite, and reports any changes.

Usage:
    python3 shenyun_scraper.py                     # Run a full scrape + change report
    python3 shenyun_scraper.py --no-report          # Scrape without change report
    python3 shenyun_scraper.py --report-only        # Show changes from last scan
    python3 shenyun_scraper.py --force              # Force rescrape even if < 3 days
"""

import argparse
import json
import os
import re
import sqlite3
import sys
import time
from datetime import datetime, timezone, timedelta
from urllib.parse import urljoin, quote_plus

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.shenyun.com"
TICKETS_URL = urljoin(BASE_URL, "/tickets")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shenyun_showtimes.db")
SCAN_INTERVAL_DAYS = 3
REQUEST_DELAY = 0.5  # seconds between API calls

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": BASE_URL,
}


def google_maps_url(theater_name, address):
    query = f"{theater_name}, {address}" if address else theater_name
    return f"https://www.google.com/maps/search/{quote_plus(query)}"


def parse_showtime_datetime(time_start_str):
    """Parse API timeStart string into ISO datetime."""
    try:
        dt = datetime.strptime(time_start_str, "%Y-%m-%d %H:%M:%S")
        return dt.isoformat()
    except ValueError:
        return time_start_str


class ShenyunScraper:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database schema."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_time TEXT NOT NULL,
                cities_scraped INTEGER DEFAULT 0,
                showtimes_found INTEGER DEFAULT 0,
                status TEXT DEFAULT 'completed'
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS showtimes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER NOT NULL,
                city TEXT NOT NULL,
                country TEXT NOT NULL,
                theater_name TEXT NOT NULL,
                theater_address TEXT DEFAULT '',
                google_maps_url TEXT DEFAULT '',
                showtime_datetime TEXT NOT NULL,
                showtime_display TEXT DEFAULT '',
                city_url TEXT DEFAULT '',
                api_event_id TEXT DEFAULT '',
                theater_group TEXT DEFAULT '',
                FOREIGN KEY (scan_id) REFERENCES scan_history(id)
            )
        """)

        c.execute("""
            CREATE INDEX IF NOT EXISTS idx_showtimes_scan
            ON showtimes(scan_id)
        """)

        c.execute("""
            CREATE INDEX IF NOT EXISTS idx_showtimes_lookup
            ON showtimes(city, theater_name, showtime_datetime)
        """)

        # Migrate existing databases — add theater_group if missing
        try:
            c.execute("ALTER TABLE showtimes ADD COLUMN theater_group TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass  # column already exists

        conn.commit()
        conn.close()

    def get_cities(self):
        """
        Scrape the main tickets page to get all city listings.
        Returns list of dicts: {city, venue, url}
        """
        print("Fetching main tickets page...")
        resp = self.session.get(TICKETS_URL, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        cities = []
        seen = set()

        for link in soup.find_all("a", class_="ticket-finder-city"):
            href = link.get("href", "").strip()
            if not href or not href.startswith("/"):
                continue

            city_text = link.get_text(strip=True)
            parent_li = link.find_parent("li")
            venue = ""
            if parent_li:
                hidden_divs = parent_li.find_all("div", class_="is-hidden")
                if hidden_divs:
                    venue = hidden_divs[0].get_text(strip=True)

            # Extract city alias from URL path
            path_parts = href.strip("/").split("/")
            alias = path_parts[0] if path_parts else ""

            key = (alias, venue)
            if key in seen:
                continue
            seen.add(key)

            cities.append({
                "city": city_text,
                "venue": venue,
                "url": urljoin(BASE_URL, href),
                "alias": alias,
            })

        print(f"Found {len(cities)} unique city+venue entries")
        return cities

    def extract_address_from_page(self, page_url):
        """Fetch a city page HTML and extract address from JSON-LD."""
        try:
            resp = self.session.get(page_url, timeout=15)
            if resp.status_code != 200:
                return ""
            for match in re.finditer(
                r'<script[^>]*type=[\"\']application/ld\+json[\"\'][^>]*>(.*?)</script>',
                resp.text, re.DOTALL
            ):
                try:
                    data = json.loads(match.group(1))
                    if data.get("@type") == "Event":
                        loc = data.get("location", {})
                        addr = loc.get("address", {})
                        if isinstance(addr, dict):
                            return self._join_address(addr)
                        return str(addr)
                except json.JSONDecodeError:
                    continue
        except requests.RequestException:
            pass
        return ""

    @staticmethod
    def _join_address(addr):
        street = (addr.get("streetAddress") or "").strip()
        city = (addr.get("addressLocality") or "").strip()
        region = (addr.get("addressRegion") or "").strip()
        postal = (addr.get("postalCode") or "").strip()
        # Omit addressCountry — we store it separately
        parts = [p for p in [street, city] if p]
        if region and postal:
            parts.append(f"{region} {postal}")
        elif postal:
            parts.append(postal)
        elif region:
            parts.append(region)
        return ", ".join(parts)

    def get_city_showtimes(self, alias):
        """
        Call the city-specific API to get showtime data.
        Returns dict with city data and event items, or None on failure.
        """
        api_url = urljoin(BASE_URL, f"/{alias}/get-city-api?")
        try:
            resp = self.session.get(api_url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            city_data = data.get("cityData", {})
            event_items = city_data.get("eventItems", [])

            return {
                "city_name": city_data.get("cityName", ""),
                "country_name": city_data.get("countryName", ""),
                "country_code": city_data.get("countryCode", ""),
                "province": city_data.get("province", ""),
                "theater_name": city_data.get("theaterName", ""),
                "theater_address": (city_data.get("boxOfficeInfo") or "").strip(),
                "event_items": event_items,
            }
        except requests.RequestException as e:
            print(f"  [WARN] API request failed for {alias}: {e}")
            return None
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  [WARN] API parse error for {alias}: {e}")
            return None

    def scrape_all(self):
        """Full scrape: get cities, call APIs, store in DB, report changes."""
        print("=" * 60)
        print(f"Shen Yun Showtime Scraper — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        cities = self.get_cities()
        if not cities:
            print("ERROR: No cities found on tickets page.")
            return

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        scan_time = datetime.now(timezone.utc).isoformat()
        c.execute(
            "INSERT INTO scan_history (scan_time, status) VALUES (?, 'in_progress')",
            (scan_time,),
        )
        scan_id = c.lastrowid
        conn.commit()

        total_showtimes = 0
        failed_cities = []
        fetched_aliases = set()

        for i, city in enumerate(cities):
            alias = city["alias"]
            print(f"\n[{i+1}/{len(cities)}] {city['city']} ({city['venue']}) — alias: {alias}")

            if alias in fetched_aliases:
                print(f"  [SKIP] alias already fetched this run")
                continue
            fetched_aliases.add(alias)

            api_data = self.get_city_showtimes(alias)
            time.sleep(REQUEST_DELAY)

            if api_data is None:
                failed_cities.append(alias)
                continue

            items = api_data.get("event_items", [])
            if not items:
                print(f"  No showtimes found")
                continue

            # Prefer JSON-LD address from the city page (cleaner), fall back to boxOfficeInfo
            page_addr = self.extract_address_from_page(city["url"])
            time.sleep(REQUEST_DELAY)
            if page_addr:
                theater_address = page_addr
                print(f"  [address from page] {page_addr[:70]}...")
            else:
                theater_address = (api_data.get("theater_address", "") or "").strip()
                bo_hint = re.match(r'^[^,]+(?:Street?|Road|Avenue?|Boulevard?|Drive|Lane|Way|Place|Square|Blvd|Dr|Rd|Ave|St|Ln)\b', theater_address, re.IGNORECASE)
                if not bo_hint:
                    theater_address = ""
            country = api_data.get("country_name", "")
            theater_name = api_data.get("theater_name", city["venue"])
            api_city_name = api_data.get("city_name", city["city"])
            gmaps_url = google_maps_url(theater_name, theater_address)

            for item in items:
                showtime_dt = item.get("timeStart", "")
                showtime_display = item.get("showTime", "")
                event_id = str(item.get("id", ""))

                c.execute(
                    """INSERT INTO showtimes
                       (scan_id, city, country, theater_name, theater_address,
                        google_maps_url, showtime_datetime, showtime_display,
                        city_url, api_event_id, theater_group)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        scan_id,
                        api_city_name,
                        country,
                        theater_name,
                        theater_address,
                        gmaps_url,
                        showtime_dt,
                        showtime_display,
                        city["url"],
                        event_id,
                        "",
                    ),
                )
                total_showtimes += 1

            print(f"  → {len(items)} showtimes from {country}")

        c.execute(
            "UPDATE scan_history SET cities_scraped = ?, showtimes_found = ?, status = 'completed' WHERE id = ?",
            (len(cities) - len(failed_cities), total_showtimes, scan_id),
        )
        conn.commit()

        print(f"\n{'=' * 60}")
        print(f"Scrape complete: {total_showtimes} showtimes from {len(cities) - len(failed_cities)} cities")
        if failed_cities:
            print(f"Failed cities ({len(failed_cities)}): {', '.join(failed_cities)}")

        changes = self.detect_changes(conn)
        # Attach scrape counts so write_update_md can use them
        if changes.get("new"):
            changes["showtimes_found"] = total_showtimes
            changes["cities_scraped"] = len(cities) - len(failed_cities)
        self.print_changes(changes)
        self.write_update_md(changes)

        conn.close()
        return changes

    def detect_changes(self, conn=None):
        """
        Compare the latest two completed scans and return changes.
        Returns dict with added, removed, and changed showtimes.
        """
        close_conn = False
        if conn is None:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            close_conn = True
        else:
            conn.row_factory = sqlite3.Row

        try:
            c = conn.cursor()

            # Get the latest two completed scan IDs
            c.execute(
                "SELECT id, scan_time FROM scan_history WHERE status = 'completed' ORDER BY id DESC LIMIT 2"
            )
            scans = c.fetchall()

            if len(scans) < 2:
                return {"new": True, "scan_id": scans[0]["id"] if scans else None}

            latest_id = scans[0]["id"]
            previous_id = scans[1]["id"]

            # Get showtimes from both scans
            c.execute(
                "SELECT city, country, theater_name, theater_address, google_maps_url, "
                "showtime_datetime, showtime_display, city_url, api_event_id "
                "FROM showtimes WHERE scan_id = ?",
                (latest_id,),
            )
            latest_rows = {(r["city_url"], r["showtime_datetime"]): dict(r) for r in c.fetchall()}

            c.execute(
                "SELECT city, country, theater_name, theater_address, google_maps_url, "
                "showtime_datetime, showtime_display, city_url, api_event_id "
                "FROM showtimes WHERE scan_id = ?",
                (previous_id,),
            )
            previous_rows = {(r["city_url"], r["showtime_datetime"]): dict(r) for r in c.fetchall()}

            latest_keys = set(latest_rows.keys())
            previous_keys = set(previous_rows.keys())

            added_keys = latest_keys - previous_keys
            removed_keys = previous_keys - latest_keys
            common_keys = latest_keys & previous_keys

            added = [latest_rows[k] for k in sorted(added_keys)]
            removed = [previous_rows[k] for k in sorted(removed_keys)]

            # Check for time changes (same city+venue+date but different time)
            changed = []
            for key in common_keys:
                prev = previous_rows[key]
                curr = latest_rows[key]
                if prev["showtime_datetime"] != curr["showtime_datetime"]:
                    changed.append({
                        "city": curr["city"],
                        "theater": curr["theater_name"],
                        "old_time": prev["showtime_datetime"],
                        "new_time": curr["showtime_datetime"],
                    })

            return {
                "new": False,
                "latest_scan_id": latest_id,
                "previous_scan_id": previous_id,
                "latest_scan_time": scans[0]["scan_time"],
                "previous_scan_time": scans[1]["scan_time"],
                "added": added,
                "removed": removed,
                "changed": changed,
            }
        finally:
            if close_conn:
                conn.close()

    def print_changes(self, changes):
        """Print a formatted change report."""
        if changes.get("new"):
            print(f"\n{'=' * 60}")
            print(f"FIRST SCAN — {changes.get('scan_id', 'N/A')}")
            print("No previous data to compare. Baseline established.")
            return

        print(f"\n{'=' * 60}")
        print(f"CHANGE REPORT")
        print(f"Previous scan: {changes.get('previous_scan_time', 'N/A')}")
        print(f"Latest scan:  {changes.get('latest_scan_time', 'N/A')}")
        print(f"{'=' * 60}")

        added = changes.get("added", [])
        removed = changes.get("removed", [])
        changed = changes.get("changed", [])

        if not added and not removed and not changed:
            print("No changes detected.")
            return

        if added:
            print(f"\n🟢 ADDED SHOWTIMES ({len(added)}):")
            for s in sorted(added, key=lambda x: (x["city"], x["showtime_datetime"])):
                print(f"  • {s['city']} — {s['theater_name']}")
                print(f"    {s['showtime_datetime']} ({s['showtime_display']})")
                print(f"    {s['country']}")

        if removed:
            print(f"\n🔴 REMOVED SHOWTIMES ({len(removed)}):")
            for s in sorted(removed, key=lambda x: (x["city"], x["showtime_datetime"])):
                print(f"  • {s['city']} — {s['theater_name']}")
                print(f"    {s['showtime_datetime']} ({s['showtime_display']})")
                print(f"    {s['country']}")

        if changed:
            print(f"\n🟡 TIME CHANGES ({len(changed)}):")
            for s in sorted(changed, key=lambda x: x["city"]):
                print(f"  • {s['city']} — {s['theater']}")
                print(f"    OLD: {s['old_time']}")
                print(f"    NEW: {s['new_time']}")

        print(f"\n{'=' * 60}")

    def write_update_md(self, changes):
        """Write a YYMMDD-update.md with bullet-point changes."""
        now = datetime.now(timezone.utc)
        filename = now.strftime("%y%m%d") + "-update.md"
        filepath = os.path.join(os.path.dirname(self.db_path), filename)

        if changes.get("new"):
            n = changes.get("showtimes_found", 0)
            c = changes.get("cities_scraped", 0)
            with open(filepath, "w") as f:
                f.write(f"# Shen Yun Update ({now.strftime('%Y-%m-%d %H:%M UTC')})\n\n")
                f.write(f"First scan — {n} showtimes across {c} cities.\n")
                f.write("Baseline established — see [`shenyun_showtimes.xlsx`](./shenyun_showtimes.xlsx)\n")
            print(f"Update file: {filepath}")
            return

        added = changes.get("added", [])
        removed = changes.get("removed", [])
        changed = changes.get("changed", [])

        if not added and not removed and not changed:
            with open(filepath, "w") as f:
                f.write(f"# Shen Yun Update ({now.strftime('%Y-%m-%d %H:%M UTC')})\n\n")
                f.write("No changes since last scan.\n")
            print(f"Update file: {filepath} (no changes)")
            return

        prev_time = (changes.get("previous_scan_time") or "?")[:10]
        curr_time = (changes.get("latest_scan_time") or "?")[:10]

        with open(filepath, "w") as f:
            f.write(f"# Shen Yun Update ({now.strftime('%Y-%m-%d %H:%M UTC')})\n\n")
            f.write(f"Changes from `{prev_time}` → `{curr_time}`\n")
            if added:
                f.write(f"\n## Added ({len(added)})\n\n")
                for s in sorted(added, key=lambda x: (x["city"], x["showtime_datetime"])):
                    f.write(f"- **{s['city']}** ({s['country']}) — {s['theater_name']}\n")
                    f.write(f"  {s['showtime_datetime']} — {s['showtime_display']}\n")
            if removed:
                f.write(f"\n## Removed ({len(removed)})\n\n")
                for s in sorted(removed, key=lambda x: (x["city"], x["showtime_datetime"])):
                    f.write(f"- **{s['city']}** ({s['country']}) — {s['theater_name']}\n")
                    f.write(f"  {s['showtime_datetime']} — {s['showtime_display']}\n")
            if changed:
                f.write(f"\n## Time Changes ({len(changed)})\n\n")
                for s in sorted(changed, key=lambda x: x["city"]):
                    f.write(f"- **{s['city']}** — {s['theater']}\n")
                    f.write(f"  OLD: {s['old_time']} → NEW: {s['new_time']}\n")
            f.write("\n---\nSee [`shenyun_showtimes.xlsx`](./shenyun_showtimes.xlsx) for full data.\n")

        print(f"Update file: {filepath}")

    def export_json(self, output_path=None):
        """Export latest scan data as JSON."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute(
            "SELECT id FROM scan_history WHERE status = 'completed' ORDER BY id DESC LIMIT 1"
        )
        row = c.fetchone()
        if not row:
            print("No completed scans found.")
            conn.close()
            return

        scan_id = row["id"]
        c.execute(
            "SELECT * FROM showtimes WHERE scan_id = ? ORDER BY city, showtime_datetime",
            (scan_id,),
        )
        rows = [dict(r) for r in c.fetchall()]
        conn.close()

        output = {
            "scan_id": scan_id,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "showtimes": rows,
        }

        if output_path:
            with open(output_path, "w") as f:
                json.dump(output, f, indent=2)
            print(f"Exported {len(rows)} showtimes to {output_path}")
        else:
            print(json.dumps(output, indent=2))

        return output

    def query(self, sql, params=None):
        """Direct query helper for exploring the database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        if params:
            c.execute(sql, params)
        else:
            c.execute(sql)
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows


def should_run():
    """Check if enough time has passed since last scan."""
    if not os.path.exists(DB_PATH):
        return True
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT scan_time FROM scan_history WHERE status = 'completed' ORDER BY id DESC LIMIT 1"
    )
    row = c.fetchone()
    conn.close()
    if not row:
        return True
    last_time = datetime.fromisoformat(row[0])
    delta = datetime.now(timezone.utc) - last_time
    return delta >= timedelta(days=SCAN_INTERVAL_DAYS)


def main():
    parser = argparse.ArgumentParser(description="Shen Yun Showtime Scraper")
    parser.add_argument("--no-report", action="store_true", help="Skip change report after scrape")
    parser.add_argument("--report-only", action="store_true", help="Show changes from last two scans without scraping")
    parser.add_argument("--force", action="store_true", help="Force scrape regardless of last scan time")
    parser.add_argument("--export", metavar="FILE", help="Export latest data as JSON to FILE")
    parser.add_argument("--query", metavar="SQL", help="Run a SQL query against the database")
    args = parser.parse_args()

    scraper = ShenyunScraper()

    if args.query:
        rows = scraper.query(args.query)
        for row in rows:
            print(json.dumps(row, default=str))
        return

    if args.export:
        scraper.export_json(args.export)
        return

    if args.report_only:
        changes = scraper.detect_changes()
        scraper.print_changes(changes)
        scraper.write_update_md(changes)
        return

    if not args.force and not should_run():
        print(f"Skipping scrape — last scan was less than {SCAN_INTERVAL_DAYS} days ago.")
        print(f"Use --force to override.")
        changes = scraper.detect_changes()
        scraper.print_changes(changes)
        return

    changes = scraper.scrape_all()
    # Generate xlsx after scrape
    try:
        from shenyun_export_excel import build as build_xlsx
        build_xlsx()
    except ImportError:
        print("(shenyun_export_excel not available, skipping xlsx)")


if __name__ == "__main__":
    main()
