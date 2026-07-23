from curl_cffi import requests
from bs4 import BeautifulSoup
import urllib.parse

def search_mhhauto(query: str, max_results: int = 20):
    """Search mhhauto.com via DuckDuckGo HTML proxy (bypasses Cloudflare)."""
    url = "https://html.duckduckgo.com/html/"
    params = {"q": f"site:mhhauto.com {query}"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    resp = requests.get(url, params=params, headers=headers, impersonate="chrome124")
    if resp.status_code != 200:
        print(f"DuckDuckGo returned {resp.status_code}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []

    for link in soup.find_all("a", class_="result__a"):
        href = link.get("href", "")
        if "mhhauto" not in href.lower():
            continue
        title = link.get_text(strip=True)
        snippet_el = link.find_next("a", class_="result__snippet")
        snippet = snippet_el.get_text(strip=True) if snippet_el else ""

        decoded = urllib.parse.unquote(href)
        if "uddg=" in decoded:
            actual = decoded.split("uddg=")[1].split("&")[0]
            actual = urllib.parse.unquote(actual)

        results.append({"title": title, "url": actual, "snippet": snippet})
        if len(results) >= max_results:
            break

    return results


if __name__ == "__main__":
    results = search_mhhauto("cx-9")
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['title']}")
        print(f"   {r['url']}")
        if r["snippet"]:
            print(f"   {r['snippet'][:120]}...")
        print()
