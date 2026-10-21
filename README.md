# FlyRank Polite Scraper

A Python web-scraping pipeline built for FlyRank Internship Assignment A9.

## Target Classification

- Target: Books to Scrape
- Website: https://books.toscrape.com/
- Purpose: Practice web scraping using a designated practice website.
- Scope: The first three catalogue pages and their 60 unique book pages.
- Data: Book titles, prices, availability, ratings, descriptions, URLs,
  source catalogue pages, and fetch timestamps.
- Robots.txt result: HTTP 404 Not Found when checked.

I will not reuse this code on another site without checking its rules
and terms first.

## Technology

- Python
- Requests
- Beautiful Soup
- Pydantic

## Installation

Create and activate a virtual environment, then install dependencies:

    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt

## Usage

The scraper implementation will be added in subsequent stages.

## Data Validation

Book records will be validated before being written to the output JSON.

## Politeness

The scraper will identify itself with a User-Agent, use request timeouts,
wait between network requests, and cache downloaded HTML.

## Limitations

The scraper is designed only for the first three catalogue pages.
Changes to the website's HTML structure may require selector updates.

## Ethics

Prefer official APIs when available. Never bypass logins, paywalls,
or access restrictions. Collect only the data needed.