from services.matching import find_existing_book
from models.models import BookStaging, Book
from database.connection import Session

def load_books():

    session = Session()

    try:    

        staging_rows = session.query(BookStaging).all()

        for r in staging_rows:

            existing = find_existing_book(session, r)

            if existing:

                existing.title = r.title
                existing.author = r.author
                existing.isbn = r.isbn

                if r.my_rating and r.my_rating.strip():
                    existing.my_rating = float(
                        r.my_rating.replace(",", ".")
                    )
                else:
                    existing.my_rating = None

                existing.date_read = r.date_read

                continue

            rating = None

            if r.my_rating:
                try:
                    rating = float(
                        r.my_rating.replace(",", ".")
                    )
                except ValueError:
                    rating = None

            book = Book(
                title=r.title,
                author=r.author,
                isbn=r.isbn,
                my_rating=rating,
                date_read=r.date_read
            )

            session.add(book)

        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()