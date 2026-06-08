from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
import csv
from pathlib import Path

Base = declarative_base()

class BookStaging(Base):
    __tablename__ = "books_staging"

    id = Column(Integer, primary_key=True)

    title = Column(String)
    author = Column(String)
    isbn = Column(String)

    my_rating = Column(String)
    date_read = Column(String)
    shelves = Column(String)

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
  #  staging_id = Column(Integer, unique=True)  # 🔥 KLUCZ IDEMPOTENCYJNY
    title = Column(String)
    author = Column(String)
    isbn = Column(String)
    my_rating = Column(Float)
    date_read = Column(String)



class Shelf(Base):
    __tablename__ = "shelves"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)


class BookShelf(Base):
    __tablename__ = "book_shelves"

    book_id = Column(Integer, ForeignKey("books.id"), primary_key=True)
    shelf_id = Column(Integer, ForeignKey("shelves.id"), primary_key=True)


engine = create_engine(
    "postgresql+psycopg2://librarian:librarian123@localhost:5432/library"
)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
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

def build_relationships():
    session.query(BookShelf).delete(
        synchronize_session=False
    )
    session.commit()

    staging_rows = session.query(BookStaging).all()

    for r in staging_rows:

        book = find_existing_book(r)
        if not book or not r.shelves:
            continue

        normalized_shelves = {
            s.strip().lower()
            for s in r.shelves.split(",")
            if s.strip()
        }

        for shelf_name in normalized_shelves: # dedupe inline
            shelf = session.query(Shelf).filter_by(name=shelf_name).first()

            if shelf:

                exists = session.query(BookShelf).filter_by(
                    book_id=book.id,
                    shelf_id=shelf.id
                ).first()

                if not exists:
                    session.add(BookShelf(
                        book_id=book.id,
                        shelf_id=shelf.id
                    ))

    session.commit()

def extract_shelves():
    rows = session.query(BookStaging.shelves).all()

    seen = set()

    for (shelves,) in rows:
        if not shelves:
            continue

        for s in shelves.split(","):
            name = s.strip().lower()

            if name and name not in seen:
                seen.add(name)

                exists = session.query(Shelf).filter_by(name=name).first()
                if not exists:
                    session.add(Shelf(name=name))

    session.commit()

def load_books():
    staging_rows = session.query(BookStaging).all()

    for r in staging_rows:

        # optional: dedupe po ISBN
        existing = find_existing_book(r)
        if existing:
                 # 🔥 update (idempotency)
            existing.title = r.title
            existing.author = r.author
            existing.isbn = r.isbn
            if r.my_rating and r.my_rating.strip():
                existing.my_rating = float(r.my_rating.replace(",", "."))
            else:
                existing.my_rating = None
            existing.date_read = r.date_read
            continue
        rating = None
        if r.my_rating:
            try:
                rating = float(r.my_rating.replace(",", "."))
            except ValueError:
                rating = None   
        book = Book(
            #staging_id=r.id,
            title=r.title,
            author=r.author,
            isbn=r.isbn,
            #my_rating=float(r.my_rating) if r.my_rating else None,
            my_rating=rating,
            date_read=r.date_read
        )

        session.add(book)

    session.commit()

def find_existing_book(r):

    if r.isbn and r.isbn.strip():
        return session.query(Book).filter_by(
            isbn=r.isbn
        ).first()

    return session.query(Book).filter_by(
        title=r.title,
        author=r.author
    ).first()

def run_pipeline():
    load_csv_to_staging(get_latest_csv())
    load_books()
    extract_shelves()
    build_relationships()

if __name__ == "__main__":
    run_pipeline()