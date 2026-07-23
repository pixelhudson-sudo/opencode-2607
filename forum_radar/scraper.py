import re
import time
import logging
from urllib.parse import urljoin, urlparse
from datetime import datetime

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ForumScraper:
    def __init__(self, config):
        self.config = config
        self.client = httpx.Client(
            follow_redirects=True,
            timeout=30.0,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                ),
            },
        )

    def close(self):
        self.client.close()

    def _get(self, url: str) -> str:
        time.sleep(self.config.REQUEST_DELAY)
        resp = self.client.get(url)
        resp.raise_for_status()
        return resp.text

    @staticmethod
    def extract_creator(title: str, content: str = "", homepage_url: str = "") -> str:
        text = title.strip()
        for sep in [" - ", " – ", " — ", " | ", " :: "]:
            if sep in text:
                candidate = text.split(sep)[0].strip()
                if candidate and len(candidate) < 60:
                    return candidate
        for prefix in ["the ", "how to ", "introduction to ", "complete ", "advanced ", "master "]:
            if text.lower().startswith(prefix):
                return ""
        return ""

    def parse_listing_page(self, html: str, base_url: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        threads = []

        for row in soup.select("tr.inline_row"):
            tds = row.find_all("td")
            if len(tds) < 6:
                continue

            title_el = row.select_one("span.subject_new a, span.subject_old a")
            if not title_el:
                continue

            title = title_el.get_text(strip=True)
            href = title_el.get("href", "")
            thread_url = urljoin(base_url, href)

            tid_from_url = re.search(r'--(\d+)(?:\?|$|")', href)
            thread_id = int(tid_from_url.group(1)) if tid_from_url else 0

            author_el = row.select_one("div.author a")
            if author_el:
                author = author_el.get_text(strip=True)
                author_url = urljoin(base_url, author_el.get("href", ""))
            else:
                author = ""
                author_url = ""

            replies_str = tds[3].get_text(strip=True) if len(tds) > 3 else "0"
            views_str = tds[4].get_text(strip=True) if len(tds) > 4 else "0"
            replies = int(replies_str) if replies_str.isdigit() else 0
            views = int(views_str) if views_str.isdigit() else 0

            rating = 0.0
            rating_votes = 0
            rating_el = row.select_one("ul.star_rating li.current_rating")
            if rating_el:
                rt = rating_el.get("title", "")
                m = re.search(r"(\d+)\s*Vote", rt)
                if m:
                    rating_votes = int(m.group(1))
                m2 = re.search(r"(\d+(?:\.\d+)?)\s*out\s*of\s*5", rt)
                if m2:
                    rating = float(m2.group(1))

            lastpost_el = row.select_one("td#lastpost span.lastpost")
            last_post_date = ""
            if lastpost_el:
                date_el = lastpost_el.find("span", title=True) or lastpost_el
                last_post_date = date_el.get("title", date_el.get_text(strip=True))

            is_sticky = "forumdisplay_sticky" in row.get("class", [])

            threads.append({
                "thread_id": thread_id,
                "title": title,
                "url": thread_url,
                "uploader": author,
                "uploader_url": author_url,
                "replies": replies,
                "views": views,
                "rating": rating,
                "rating_votes": rating_votes,
                "last_post_date": last_post_date,
                "is_sticky": is_sticky,
            })

        return threads

    def scrape_listing(self, url: str, max_pages: int = 2) -> list[dict]:
        all_threads = []
        base_url = self.config.BASE_URL

        html = self._get(url)
        page_threads = self.parse_listing_page(html, base_url)
        all_threads.extend(page_threads)
        logger.info(f"Page 1: {len(page_threads)} threads")

        for page_num in range(2, max_pages + 1):
            page_url = f"{url}?page={page_num}"
            try:
                html = self._get(page_url)
                page_threads = self.parse_listing_page(html, base_url)
                if not page_threads:
                    break
                all_threads.extend(page_threads)
                logger.info(f"Page {page_num}: {len(page_threads)} threads")
            except Exception as e:
                logger.warning(f"Failed page {page_num}: {e}")
                break

        return all_threads

    def parse_thread_page(self, html: str) -> dict:
        soup = BeautifulSoup(html, "html.parser")
        data = {}

        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            data["description"] = meta_desc["content"].strip()

        first_post_date = ""
        first_post_el = soup.select_one("div.post_head span.post_date span[title]")
        if first_post_el:
            first_post_date = first_post_el.get("title", "")
        if not first_post_el:
            first_post_el = soup.select_one("div.post_head span.post_date")
            if first_post_el:
                first_post_date = first_post_el.get_text(strip=True)

        post_body = soup.select_one("div.post_body")
        if post_body:
            data["post_content"] = post_body.get_text("\n", strip=True)

            size_match = re.search(
                r'[\|]\s*([\d,.MGKTB\s]+(?:GB|MB|KB|TB))',
                post_body.get_text(),
            )
            if not size_match:
                size_match = re.search(
                    r'([\d,.]+)\s*(GB|MB|TB)',
                    post_body.get_text(),
                )
            if size_match:
                data["size"] = size_match.group(0).strip()

            advertised_price = 0.0
            value_matches = re.findall(
                r'Value\s*(?:\$|USD)?\s*([\d,]+(?:\.\d{2})?)',
                post_body.get_text(),
                re.IGNORECASE,
            )
            for v in value_matches:
                try:
                    advertised_price += float(v.replace(",", ""))
                except ValueError:
                    pass
            if advertised_price > 0:
                data["advertised_price"] = advertised_price

            codeblocks = post_body.select("div.codeblock div.body code")
            download_links = []
            homepage_url = ""
            for cb in codeblocks:
                text = cb.get_text(strip=True)
                if "rapidgator" in text.lower() or "uploadgig" in text.lower() or "nitroflare" in text.lower():
                    download_links.append(text)
                elif text.startswith("http") and not homepage_url:
                    homepage_url = text

            if download_links:
                data["download_links"] = "\n\n".join(download_links)
            if homepage_url:
                data["homepage_url"] = homepage_url

        if first_post_date:
            data["first_seen_date"] = first_post_date

        return data

    def lookup_online_price(self, title: str, homepage_url: str = "") -> dict:
        result = {"online_price": "NA", "online_price_url": ""}
        urls_to_try = []

        if homepage_url and homepage_url.startswith("http"):
            urls_to_try.append(homepage_url)

        if not urls_to_try:
            return result

        for url in urls_to_try:
            try:
                resp = self.client.get(url, timeout=15.0, follow_redirects=True)
                html = resp.text
                result["online_price_url"] = str(resp.url)

                price_patterns = [
                    r'\$\s*(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)\s*(?:\.\d{2})?',
                    r'price[:\s]*\$?\s*(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)',
                    r'(?:only|just|now)\s*\$?\s*(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)',
                    r'\$(\d{1,4})\s*(?:\.\d{2})?\s*(?:/mo|/month|one-time|one time)',
                    r'(?:one-time|one time)\s*(?:fee|payment|price)?[:\s]*\$?\s*(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)',
                    r'(?:monthly|per month|/month)\s*(?:fee|price)?[:\s]*\$?\s*(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)',
                ]

                prices_found = []
                for pat in price_patterns:
                    for m in re.finditer(pat, html, re.IGNORECASE):
                        try:
                            val = float(m.group(1).replace(",", ""))
                            if 5 <= val <= 50000:
                                prices_found.append(val)
                        except ValueError:
                            pass

                if prices_found:
                    result["online_price"] = f"${max(prices_found):,.0f}"
                    return result

            except Exception as e:
                logger.debug(f"Price lookup failed for {url}: {e}")

        return result

    def scrape_author_profile(self, author_url: str) -> dict:
        info = {}
        try:
            html = self._get(author_url)
            soup = BeautifulSoup(html, "html.parser")

            page_text = soup.get_text()

            m = re.search(r'Registration Date:\s*([\d\-]+)', page_text)
            if m:
                info["uploader_joined"] = m.group(1)

            m = re.search(r'Total Posts:\s*([\d,]+)', page_text)
            if m:
                info["uploader_posts"] = int(m.group(1).replace(",", ""))

            m = re.search(r'Reputation[:\]]\s*([-\d]+)', page_text)
            if m:
                info["uploader_reputation"] = int(m.group(1))

            group_el = soup.find("span", class_="largetext")
            if group_el:
                next_sib = group_el.find_next("span", class_="smalltext")
                if next_sib:
                    group_text = next_sib.get_text(strip=True).strip("()")
                    info["uploader_group"] = group_text

        except Exception as e:
            logger.debug(f"  Uploader scrape failed for {author_url}: {e}")

        return info

    def scrape_thread(self, url: str) -> dict:
        html = self._get(url)
        return self.parse_thread_page(html)

    def scan(self, max_pages: int = None) -> list[dict]:
        max_p = max_pages or self.config.MAX_PAGES_PER_SCAN
        threads = self.scrape_listing(self.config.FORUM_URL, max_pages=max_p)
        return threads
