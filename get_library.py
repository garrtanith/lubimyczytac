from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import requests



def get_library(url, num_pages, driver_path):

    # --- Chrome setup ---
    options = Options()
    options.add_argument("--headless=new")

    service = Service(driver_path)
    driver = webdriver.Chrome()

    # --- open page ---
    driver.get(url)
    time.sleep(5)

    # --- cookies ---
    try:
        accept_btn = driver.find_element(
            By.CSS_SELECTOR,
            "#onetrust-accept-btn-handler"
        )
        accept_btn.click()
        time.sleep(2)
    except:
        pass

    # --- results ---
    titles, authors, isbns = [], [], []
    shelves_list, my_ratings, my_dates_read = [], [], []

    for page in range(num_pages):
        print(f"Processing page {page+1}...")

        book_elements = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".book-card"))
        )

        book_html_list = [
            el.get_attribute("outerHTML") for el in book_elements
        ]

        for html in book_html_list:
            soup = BeautifulSoup(html, "html.parser")

            # --- title ---
            title_el = soup.select_one(".book-card__title")
            title = title_el.get_text(strip=True) if title_el else None

            # --- author ---
            author_el = soup.select_one(".book-card__author a")
            author = author_el.get_text(strip=True) if author_el else None

            # --- shelves (FIXED) ---
            shelf_els = soup.select(".book-card__shelf")
            shelves = ", ".join(
                s.get_text(strip=True) for s in shelf_els
            ) if shelf_els else None

            # --- append correct variable ---
            titles.append(title)
            authors.append(author)
            shelves_list.append(shelves)

            # --- ISBN ---
            isbn = None
            if title_el and title_el.get("href"):
                subpage_url = "https://lubimyczytac.pl" + title_el["href"]
                try:
                    resp = requests.get(subpage_url, timeout=10)
                    sub_soup = BeautifulSoup(resp.text, "html.parser")
                    isbn_el = sub_soup.select_one("dt:-soup-contains('ISBN:') + dd")
                    isbn = isbn_el.get_text(strip=True) if isbn_el else None
                except:
                    isbn = None

            isbns.append(isbn)

            # --- USER RATING (FIXED + SAFE) ---
            user_rating_el = soup.select_one(
                ".book-card__detail--user-rating .rating__avarage"
            )
            my_ratings.append(
                user_rating_el.get_text(strip=True) if user_rating_el else None
            )


            # --- DATE READ ---
            date_el = soup.select_one("div.book-card__read-dates")
            if date_el:
                lines = date_el.get_text(separator="\n").split("\n")
                date_text = lines[-1].strip() if len(lines) > 1 else None
            else:
                date_text = None

            my_dates_read.append(date_text)

            print(f"\tAdded: {title}")

        # --- next page ---
        try:
            next_btn = driver.find_element(
                By.CSS_SELECTOR,
                "li.page-item.next-page a.page-link"
            )
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(5)
        except:
            print("No more pages.")
            break

    driver.quit()

    # --- dataframe ---
    df = pd.DataFrame({
        "Title": titles,
        "Author": authors,
        "ISBN": isbns,
        "My Rating": my_ratings,
        "Date Read": my_dates_read,
        "Exclusive Shelf": shelves_list
    }).drop_duplicates()

    return df