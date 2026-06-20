# BookScraper: Multi-Category Web Scraper for Books.toscrape.com
# This script scrapes book data from all pages across 20 categories on books.toscrape.com.
# Features include rotating user agents, retry logic, detailed logging, and CSV output.

import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
import random
import time
import pandas as pd
from datetime import datetime
import re

@dataclass
class ScraperConfig:
    delay: float = 1.0
    max_retries: int = 3
    timeout: int = 10
    user_agents: List[str] = field(default_factory=lambda: [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"
    ])

class BookScraper:
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.session = requests.Session()
        self.base_url = "http://books.toscrape.com"
        self.log_data = []
    
    def _get_random_headers(self) -> dict:
        return {"User-Agent": random.choice(self.config.user_agents)}
    
    def _fetch(self, url: str) -> Tuple[Optional[str], float, int]:
        retries = 0
        start_time = time.time()
        while retries <= self.config.max_retries:
            try:
                time.sleep(self.config.delay)
                response = self.session.get(
                    url,
                    headers=self._get_random_headers(),
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                elapsed_time = (time.time() - start_time) * 1000
                self.log_data.append({
                    "url": url,
                    "status": "success",
                    "response_time": elapsed_time,
                    "retries_needed": retries
                })
                return response.text, elapsed_time, retries
            except requests.exceptions.RequestException as e:
                retries += 1
                if retries > self.config.max_retries:
                    elapsed_time = (time.time() - start_time) * 1000
                    self.log_data.append({
                        "url": url,
                        "status": f"error: {str(e)}",
                        "response_time": elapsed_time,
                        "retries_needed": retries - 1
                    })
                    return None, elapsed_time, retries - 1
                time.sleep(self.config.delay * (2 ** retries))
    
    def scrape_categories(self) -> Dict[str, str]:
        print("── CATEGORY SCRAPING ──")
        url = f"{self.base_url}/index.html"
        html, _, _ = self._fetch(url)
        if not html:
            return {}
        soup = BeautifulSoup(html, "html.parser")
        categories = {}
        category_links = soup.select("ul.nav-list li ul li a")
        for link in category_links:
            name = link.text.strip()
            href = link["href"]
            full_url = f"{self.base_url}/{href}"
            categories[name] = full_url
        print(f"Found {len(categories)} categories")
        return categories
    
    def scrape_category(self, category_url: str) -> List[Dict[str, Any]]:
        books = []
        page_url = category_url
        while page_url:
            html, response_time, retries = self._fetch(page_url)
            if not html:
                break
            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select("div.product_pod")
            for card in cards:
                book = self._parse_book_card(card)
                detail_url = book["url"]
                detail_html, detail_time, detail_retries = self._fetch(detail_url)
                if detail_html:
                    detail_data = self._parse_book_detail(detail_html)
                    book.update(detail_data)
                    book["url"] = detail_url
                    book["scraped_at"] = datetime.now().isoformat()
                    book["response_time_ms"] = detail_time
                    books.append(book)
            next_link = soup.select_one("li.next a")
            if next_link:
                next_page = next_link["href"]
                page_url = f"{page_url.rsplit('/', 1)[0]}/{next_page}"
            else:
                page_url = None
        return books
    
    def _parse_book_card(self, card_soup: BeautifulSoup) -> Dict[str, Any]:
        title = card_soup.h3.a["title"]
        price = card_soup.select_one("p.price_color").text.strip()
        rating_class = card_soup.select_one("p.star-rating")["class"]
        rating = rating_class[1] if len(rating_class) > 1 else "Zero"
        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        rating_int = rating_map.get(rating, 0)
        book_url = card_soup.h3.a["href"]
        full_book_url = f"{self.base_url}/{book_url.replace('../../', 'catalogue/')}"
        return {
            "title": title,
            "price": float(price[1:]),
            "rating": rating_int,
            "url": full_book_url
        }
    
    def _parse_book_detail(self, detail_soup: BeautifulSoup) -> Dict[str, Any]:
        soup = BeautifulSoup(detail_soup, "html.parser")
        description = soup.select_one("div.product_description p")
        description_text = description.text.strip() if description else ""
        upc = soup.select_one("table tr:nth-child(1) td").text
        availability = soup.select_one("table tr:nth-child(6) td").text
        in_stock_match = re.search(r"(\d+)", availability)
        in_stock_count = int(in_stock_match.group(1)) if in_stock_match else 0
        num_reviews = int(soup.select_one("table tr:nth-child(7) td").text)
        return {
            "author": "",
            "description": description_text,
            "upc": upc,
            "availability": availability.strip(),
            "in_stock_count": in_stock_count,
            "num_reviews": num_reviews
        }
    
    def scrape_all(self, max_categories: int = 20) -> Dict[str, List[Dict]]:
        print("── SCRAPING ALL CATEGORIES ──")
        categories = self.scrape_categories()
        if not categories:
            print("No categories found")
            return {}
        selected_categories = dict(list(categories.items())[:max_categories])
        print(f"Processing {len(selected_categories)} categories")
        all_books = {}
        for category_name, category_url in selected_categories.items():
            print(f"Scraping category: {category_name}")
            books = self.scrape_category(category_url)
            all_books[category_name] = books
        return all_books

def main():
    config = ScraperConfig(delay=1.0, max_retries=3, timeout=10)
    scraper = BookScraper(config)
    all_books_data = scraper.scrape_all(max_categories=20)
    
    all_books = []
    category_stats = []
    for category, books in all_books_data.items():
        for book in books:
            all_books.append(book)
        if books:
            avg_price = sum(b["price"] for b in books) / len(books)
            avg_rating = sum(b["rating"] for b in books) / len(books)
            category_stats.append({
                "category": category,
                "count": len(books),
                "avg_price": avg_price,
                "avg_rating": avg_rating
            })
    
    pd.DataFrame(all_books).to_csv("books_all.csv", index=False)
    pd.DataFrame(category_stats).to_csv("books_by_category.csv", index=False)
    pd.DataFrame(scraper.log_data).to_csv("scraper_log.csv", index=False)
    
    print("── SUMMARY ──")
    print(f"Total categories scraped: {len(all_books_data)}")
    print(f"Total books scraped: {len(all_books)}")
    for stat in category_stats:
        print(f"{stat['category']}: {stat['count']} books, Avg Price: £{stat['avg_price']:.2f}, Avg Rating: {stat['avg_rating']:.2f}")
    log_df = pd.DataFrame(scraper.log_data)
    if not log_df.empty:
        slowest = log_df.loc[log_df["response_time"].idxmax()]
        fastest = log_df.loc[log_df["response_time"].idxmin()]
        print(f"Slowest page: {slowest['url']} ({slowest['response_time']:.0f}ms)")
        print(f"Fastest page: {fastest['url']} ({fastest['response_time']:.0f}ms)")

if __name__ == "__main__":
    main()