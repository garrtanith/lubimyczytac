from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import pandas as pd


def scrape_library(url: str, driver_path: str):
    # --- Selenium setup ---
    service = Service(driver_path)
    driver = webdriver.Chrome()

    try:
        driver.get(url)

        # czekamy aż pojawią się książki
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".book-card"))
        )

        html = driver.page_source

    finally:
        driver.quit()

    # --- BeautifulSoup parsing ---
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select(".book-card")

    books = []

    for card in cards:
        # title
        title_el = card.select_one(".book-card__title")
        title = title_el.get_text(strip=True) if title_el else None

        # author
        author_el = card.select_one(".book-card__author a")
        author = author_el.get_text(strip=True) if author_el else None

        # global rating
        rating_el = card.select_one(".book-card__detail--rating .rating__avarage")
        rating = rating_el.get_text(strip=True) if rating_el else None

        # user rating
        user_rating_el = card.select_one(
            ".book-card__detail--user-rating .rating__avarage"
        )
        user_rating = user_rating_el.get_text(strip=True) if user_rating_el else None

        # shelves (multi-value)
        shelf_els = card.select(".book-card__shelf")
        shelves = ", ".join(
            s.get_text(strip=True) for s in shelf_els
        ) if shelf_els else None

        books.append({
            "title": title,
            "author": author,
            "rating": rating,
            "user_rating": user_rating,
            "shelves": shelves
        })

    return books

df = pd.DataFrame(books)
df.to_csv("library.csv", index=False, encoding="utf-8")

print(df.head())