import time
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "cache"
CACHE_FILE = CACHE_DIR / "catalogue-page-1.html"

PAGE_URL = "https://books.toscrape.com/"
TIMEOUT_SECONDS = 10

HEADERS = {
    "User-Agent": (
        "FlyRankInternship-A9/1.0 "
        "(https://github.com/25A31A42J5)"
    )
}


def fetch_catalogue_page():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if CACHE_FILE.exists():
        html = CACHE_FILE.read_text(encoding="utf-8")
        print("CACHE HIT")
        print(f"Response size: {len(html.encode('utf-8'))} bytes")
        return html

    time.sleep(0.5)

    response = requests.get(
        PAGE_URL,
        headers=HEADERS,
        timeout=TIMEOUT_SECONDS,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Fetch failed with HTTP {response.status_code}"
        )

    html = response.text
    CACHE_FILE.write_text(html, encoding="utf-8")

    print(f"FETCH: HTTP {response.status_code}")
    print(f"Response size: {len(response.content)} bytes")

    return html


if __name__ == "__main__":
    fetch_catalogue_page()
