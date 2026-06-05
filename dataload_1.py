from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
import csv

Base = declarative_base()

class BookStaging(Base):
    __tablename__ = "books_staging"

    id = Column(Integer, primary_key=True, autoincrement=True)

    title = Column(String)
    author = Column(String)
    isbn = Column(String)

    my_rating = Column(String)
    date_read = Column(String)
    shelves = Column(String)

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    
    
    title = Column(String)
    author = Column(String)
    isbn = Column(String, unique=True)
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


engine = create_engine("sqlite:///library.db")
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def load_csv_to_staging(path):
    print("🚀 START LOAD CSV")
    
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        rows = []

        for r in reader:

    # 🔥 PRO FIX: normalizacja półek BEFORE staging
            raw_shelves = r.get("Exclusive Shelf")

            if raw_shelves:
                shelves_list = [s.strip() for s in raw_shelves.split(",")]
            else:
                shelves_list = []

    # staging row (1 row = 1 book)
            rows.append(BookStaging(
            title=r.get("Title"),
            author=r.get("Author"),
            isbn=r.get("ISBN"),
            my_rating=r.get("My Rating"),
            date_read=r.get("Date Read"),

        # ⚠️ tu możesz:
        # A) trzymać listę (lepsze ETL)
        # B) albo zostawić string (gorsze SQL)
            shelves=",".join(shelves_list)
            ))
    
    print(f"📦 Parsed rows: {len(rows)}")
    session.bulk_save_objects(rows)
    session.commit()

def build_relationships():
    staging_rows = session.query(BookStaging).all()

    for r in staging_rows:

        book = session.query(Book).filter_by(
                title=r.title,
                author=r.author
        ).first()
        if not book or not r.shelves:
            continue

        seen_shelves = set()  # dodatkowa ochrona

        for shelf_name in r.shelves.split(","):
            name = shelf_name.strip()

            if name in seen_shelves:
                continue
            seen_shelves.add(name)

            shelf = session.query(Shelf).filter_by(name=name).first()
            if not shelf:
                continue

            # 🔥 ANTI-DUPLICATE CHECK
            exists = session.query(BookShelf).filter_by(
                book_id=book.id,
                shelf_id=shelf.id
            ).first()

            if exists:
                continue

            session.add(BookShelf(
                book_id=book.id,
                shelf_id=shelf.id
            ))

    session.commit()

def extract_shelves():
    rows = session.query(BookStaging.shelves).all()

    unique = set()

    for r in rows:
        if r.shelves:
            for s in r.shelves.split(","):
                unique.add(s.strip())

    for s in unique:
        session.add(Shelf(name=s))

    session.commit()

def load_books():
    staging_rows = session.query(BookStaging).all()

    for r in staging_rows:

        # optional: dedupe po ISBN
        existing = session.query(Book).filter_by(isbn=r.isbn).first()
        if existing:
            continue

        book = Book(
            title=r.title,
            author=r.author,
            isbn=r.isbn,
            my_rating=float(r.my_rating) if r.my_rating else None,
            date_read=r.date_read
        )

        session.add(book)

    session.commit()

load_csv_to_staging("library.csv")
extract_shelves()
load_books()
build_relationships()
