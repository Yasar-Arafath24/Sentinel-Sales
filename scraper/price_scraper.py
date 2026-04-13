import requests
from playwright.sync_api import sync_playwright

API_URL = "http://127.0.0.1:8000/products"

def scrape_price():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html")

        price_text = page.locator(".price_color").inner_text()
        price = float(price_text.replace("£", ""))

        data = {
            "name": "Book A",
            "price": price,
            "competitor": "BooksToScrape"
        }

        response = requests.post(API_URL, json=data)

        print("Status:", response.status_code)
        print("Response:", response.json())

        browser.close()

if __name__ == "__main__":
    scrape_price()