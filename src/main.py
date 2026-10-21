import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

START_URL = "https://books.toscrape.com/"
TIMEOUT_SECONDS = 10
REQUEST_DELAY = 0.5

HEADERS = {
    "User-Agent": (
        "FlyRankInternship-A9/1.0 "
        "(https://github.com/25A31A42J5)"
    )
}


def fetch_page(url, cache_file):
    cache_path = CACHE_DIR / cache_file

    if cache_path.exists():
        html = cache_path.read_text(encoding="utf-8")
        print(f"CACHE HIT: {cache_file} ({len(html.encode('utf-8'))} bytes)")
        return html

    time.sleep(REQUEST_DELAY)

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=TIMEOUT_SECONDS,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Fetch failed: HTTP {response.status_code} for {url}"
        )

    html = response.text
    cache_path.write_text(html, encoding="utf-8")

    print(f"FETCH: {url} ({len(response.content)} bytes)")
    return html


def discover_books():
    catalogue_url = START_URL
    book_urls = []
    catalogue_pages = 0

    while catalogue_url and catalogue_pages < 3:
        catalogue_pages += 1
        cache_file = f"catalogue-page-{catalogue_pages}.html"

        html = fetch_page(catalogue_url, cache_file)
        soup = BeautifulSoup(html, "html.parser")

        for link in soup.select("article.product_pod h3 a"):
            book_url = urljoin(catalogue_url, link.get("href", ""))
            book_urls.append(book_url)

        next_link = soup.select_one("li.next a")

        if next_link and catalogue_pages < 3:
            catalogue_url = urljoin(catalogue_url, next_link["href"])
        else:
            catalogue_url = None

    unique_urls = list(dict.fromkeys(book_urls))

    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(book_urls)}")
    print(f"unique_urls={len(unique_urls)}")

    return unique_urls


if __name__ == "__main__":
    discover_books()
