import csv
from pathlib import Path
from database.connection import Session
from models.models import BookStaging, Book, Shelf, BookShelf

session = Session()

def get_latest_csv(folder="."):
    files = list(Path(folder).glob("library_*.csv"))

    if not files:
        raise FileNotFoundError(
            f"File not found library_*.csv in {folder}"
        )

    return max(files, key=lambda f: f.name)

def load_csv_to_staging(path):
    print("🚀 START LOAD CSV")
    session.query(BookStaging).delete()  # 🔥 FULL REFRESH STAGING
    rows = []

    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for r in reader:
        
    # staging row (1 row = 1 book)
            rows.append(BookStaging(
            title=r.get("Title"),
            author=r.get("Author"),
            isbn=r.get("ISBN"),
            my_rating=r.get("My Rating"),
            date_read=r.get("Date Read"),
            shelves=r.get("Exclusive Shelf")
            ))
    
    print(f"📦 Parsed rows: {len(rows)}")
    session.bulk_save_objects(rows)
    session.commit()

def extract():
    load_csv_to_staging(get_latest_csv())
