import time
from datetime import datetime, timezone
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
        print(f"CACHE HIT: {cache_file}")
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
    print(f"FETCH: {cache_file}")

    return html


def discover_books():
    catalogue_url = START_URL
    book_urls = []
    source_pages = {}
    catalogue_pages = 0

    while catalogue_url and catalogue_pages < 3:
        catalogue_pages += 1
        cache_file = f"catalogue-page-{catalogue_pages}.html"

        html = fetch_page(catalogue_url, cache_file)
        soup = BeautifulSoup(html, "html.parser")

        for link in soup.select("article.product_pod h3 a"):
            book_url = urljoin(catalogue_url, link.get("href", ""))
            book_urls.append(book_url)
            source_pages[book_url] = catalogue_url

        next_link = soup.select_one("li.next a")

        if next_link and catalogue_pages < 3:
            catalogue_url = urljoin(catalogue_url, next_link["href"])
        else:
            catalogue_url = None

    unique_urls = list(dict.fromkeys(book_urls))

    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(book_urls)}")
    print(f"unique_urls={len(unique_urls)}")

    return unique_urls, source_pages


def extract_book(url, source_page, index):
    cache_file = f"book-{index:03d}.html"
    html = fetch_page(url, cache_file)
    soup = BeautifulSoup(html, "html.parser")

    product = soup.select_one(".product_main")

    if product is None:
        raise ValueError(f"Product details not found: {url}")

    title = product.select_one("h1")
    price = product.select_one(".price_color")
    availability = product.select_one(".availability")
    rating_element = product.select_one("p.star-rating")

    if not all([title, price, availability, rating_element]):
        raise ValueError(f"Required book fields missing: {url}")

    description_element = soup.select_one("#product_description + p")
    description = (
        description_element.get_text(strip=True)
        if description_element
        else None
    )

    price_text = price.get_text(strip=True)
    price_value = "".join(
        character
        for character in price_text
        if character.isdigit() or character == "."
    )

    if not price_value:
        raise ValueError(f"Invalid price: {url}")

    return {
        "title": title.get_text(strip=True),
        "product_url": url,
        "price_text": price_text,
        "availability_text": availability.get_text(" ", strip=True),
        "rating_text": rating_element.get("class", ["", "Unknown"])[-1],
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "price_gbp": float(price_value),
    }


def main():
    book_urls, source_pages = discover_books()
    records = []

    for index, url in enumerate(book_urls, start=1):
        try:
            record = extract_book(url, source_pages[url], index)
            records.append(record)
        except (requests.RequestException, RuntimeError, ValueError) as error:
            print(f"ERROR: {url} — {error}")

    print(f"detail_pages={len(records)}")

    if records:
        print("Sample record:")
        print(records[0])


if __name__ == "__main__":
    main()
