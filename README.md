# web-scraper-advanced-bs4

> BeautifulSoup — Advanced Multi-Category Scraper with Retry

`BeautifulSoup4` `Web Scraping` `Requests` `Pagination`

---

## Overview

Create a production-grade multi-category web scraper with advanced features.

Target: http://books.toscrape.com (all categories, all pages)

Requirements:
- ScraperConfig dataclass: delay, max_retries, timeout, user_agents (rotate)
- BookScraper class:
  * __init__(config)
  * _get_random_headers() — rotate through 5 user agents
  * _fetch(url) → (html, response_time_ms) with retry and exponential backoff
  * scrape_categories() → {category_name: category_url}
  * scrape_category(category_url) → all books in category (all pages)
  * scrape_book_detail(book_url) → full book info including descr

## Features

- ScraperConfig dataclass: delay, max_retries, timeout, user_agents (rotate)
- BookScraper class:
- __init__(config)
- _get_random_headers() — rotate through 5 user agents
- _fetch(url) → (html, response_time_ms) with retry and exponential backoff
- scrape_categories() → {category_name: category_url}
- scrape_category(category_url) → all books in category (all pages)
- scrape_book_detail(book_url) → full book info including description, UPC, reviews
- scrape_all(max_categories=20) — scrape 20 categories, all pages
- _parse_book_card(card_soup) → book dict from listing page
- _parse_book_detail(detail_soup) → extended book dict from detail page
- Data model per book:
- Save: books_all.csv (all books from 20 categories),
- Print: categories scraped, total books, avg price by category, slowest/fastest pages

---

## Tech Stack

| Library | Purpose |
|---|---|
| `bs4` | Data processing |
| `pandas` | Data processing |
| `requests` | Data processing |

---

## Quick Start

```bash
git clone https://github.com/makino-p/web-scraper-advanced-bs4.git
cd web-scraper-advanced-bs4
pip install bs4 pandas requests
python solution.py
```

## Dependencies

```bash
pip install bs4 pandas requests
```

## Key Functions

- `main()`
- `scrape_categories()`
- `scrape_category()`
- `scrape_all()`

## Output Files

| File | Description |
|---|---|
| `.git` | Generated output |
| `books_all.csv` | Generated output |
| `books_by_category.csv` | Generated output |
| `scraper_log.csv` | Generated output |

---

## Project Stats

- **Lines of code**: 202
- **Functions**: 9
- **Output files**: 4

---

## Skills Demonstrated

`BeautifulSoup4` `Web Scraping` `Requests` `Pagination`

---

## License

MIT
