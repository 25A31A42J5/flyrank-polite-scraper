import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, HttpUrl, ValidationError, field_validator

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "cache"
OUTPUT_DIR = BASE_DIR / "output"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

START_URL = "https://books.toscrape.com/"
TIMEOUT_SECONDS = 10
REQUEST_DELAY = 0.5

HEADERS = {
    "User-Agent": (
        "FlyRankInternship-A9/1.0 "
        "(https://github.com/25A31A42J5)"
    )
}


class BookRecord(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: str | None
    source_page: HttpUrl
    fetched_at: datetime

    @field_validator("price_gbp")
    @classmethod
    def validate_price(cls, value):
        if value < 0:
            raise ValueError("Price cannot be negative")
        return value


def fetch_page(url, cache_file):
    cache_path = CACHE_DIR / cache_file

    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")

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

    cache_path.write_text(response.text, encoding="utf-8")
    return response.text


def discover_books():
    catalogue_url = START_URL
    book_urls = []
    source_pages = {}
    catalogue_pages = 0

    while catalogue_url and catalogue_pages < 3:
        catalogue_pages += 1
        html = fetch_page(
            catalogue_url,
            f"catalogue-page-{catalogue_pages}.html",
        )
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
    html = fetch_page(url, f"book-{index:03d}.html")
    soup = BeautifulSoup(html, "html.parser")
    product = soup.select_one(".product_main")

    if product is None:
        raise ValueError("Product details not found")

    title = product.select_one("h1")
    price = product.select_one(".price_color")
    availability = product.select_one(".availability")
    rating = product.select_one("p.star-rating")

    if not all([title, price, availability, rating]):
        raise ValueError("Required book fields are missing")

    description_element = soup.select_one("#product_description + p")
    description = (
        description_element.get_text(strip=True)
        if description_element
        else None
    )

    price_text = price.get_text(strip=True)
    price_value = "".join(
        char for char in price_text
        if char.isdigit() or char == "."
    )

    if not price_value:
        raise ValueError("Price could not be converted to a number")

    return {
        "title": title.get_text(strip=True),
        "product_url": url,
        "price_text": price_text,
        "price_gbp": float(price_value),
        "availability_text": availability.get_text(" ", strip=True),
        "rating_text": rating.get("class", ["", "Unknown"])[-1],
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def main():
    book_urls, source_pages = discover_books()
    valid_records = []
    invalid_records = []
    seen_urls = set()

    for index, url in enumerate(book_urls, start=1):
        if url in seen_urls:
            continue
        seen_urls.add(url)

        try:
            raw_record = extract_book(url, source_pages[url], index)
            record = BookRecord.model_validate(raw_record)
            valid_records.append(record.model_dump(mode="json"))
        except (
            requests.RequestException,
            RuntimeError,
            ValueError,
            ValidationError,
        ) as error:
            invalid_records.append({
                "product_url": url,
                "reason": str(error),
            })

    (OUTPUT_DIR / "books.json").write_text(
        json.dumps(valid_records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (OUTPUT_DIR / "errors.json").write_text(
        json.dumps(invalid_records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"valid_records={len(valid_records)}")
    print(f"invalid_records={len(invalid_records)}")
    print(f"saved_to={OUTPUT_DIR}")


if __name__ == "__main__":
    main()
