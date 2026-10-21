# FlyRank A9 — The Polite Scraper

A Python scraper that collects book information from Books to Scrape, a practice website intended for web scraping exercises.

## Target Classification

* **Target:** https://books.toscrape.com/
* **Classification:** Practice sandbox for web scraping.
* **Robots.txt:** Returned HTTP 404 Not Found when checked. A missing robots.txt file is not permission to ignore website rules.
* **Scope:** First three catalogue pages and their book detail pages.
* **Politeness:** Identifying User-Agent, request timeout, at least 0.5 seconds between uncached requests, and limited retries.

## Features

* Discovers book URLs across three catalogue pages.
* Extracts titles, URLs, prices, availability, ratings, and descriptions.
* Normalizes prices into numeric GBP values.
* Validates records using Pydantic.
* Caches fetched HTML to avoid unnecessary repeat requests.
* Records invalid records and failed pages.
* Retries timeouts, connection failures, and HTTP 5xx errors once.
* Generates a JSON run report.

## Requirements

* Python 3.10 or newer
* Internet access for uncached pages

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
python src/main.py
```

## Output Files

* `output/books.json` — validated book records.
* `output/errors.json` — invalid records and their error reasons.
* `output/run-report.json` — execution duration, fetched pages, cache hits, record counts, and failed pages.

## Data Schema

Each validated book record contains:

* `title`
* `product_url`
* `price_text`
* `price_gbp`
* `availability_text`
* `rating_text`
* `description`
* `source_page`
* `fetched_at`

## Caching and Politeness

HTML responses are stored locally in `cache/`. Subsequent runs reuse cached pages instead of requesting them again. Requests for uncached pages include a timeout and delay, and transient failures receive at most one retry.

## Limitations

The scraper processes only the first three catalogue pages. Cached HTML may become outdated. Missing descriptions are allowed, while missing required product fields are recorded as errors.

## Why No Browser Is Needed

The target exposes the relevant book information in server-returned HTML. Requests retrieves the HTML, and Beautiful Soup parses it, so browser automation is unnecessary.

## Ethics

This project is restricted to a designated practice website. It uses a limited scope, avoids unnecessary repeat requests through caching, and includes delays and bounded retries. A missing robots.txt file does not imply unrestricted permission to scrape other websites.
