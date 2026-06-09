from models.models import BookStaging, Shelf, BookShelf
from services.matching import find_existing_book
from database.connection import Session

def normalize_shelf_name(name):
    return name.strip().lower()

def build_relationships():

    session = Session()

    try:

        session.query(BookShelf).delete(
            synchronize_session=False
        )

        session.commit()

        seen_relationships = set()

        staging_rows = session.query(BookStaging).all()

        for r in staging_rows:

            book = find_existing_book(session, r)

            if not book or not r.shelves:
                continue

            normalized_shelves = {
                normalize_shelf_name(s)
                for s in r.shelves.split(",")
                if s.strip()
            }

            for shelf_name in normalized_shelves:

                shelf = session.query(Shelf).filter_by(
                    name=shelf_name
                ).first()

                if not shelf:
                    continue

                key = (book.id, shelf.id)

                if key not in seen_relationships:

                    seen_relationships.add(key)

                    session.add(BookShelf(
                        book_id=book.id,
                        shelf_id=shelf.id
                    ))

        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()

def extract_shelves():

    session = Session()

    try:

        rows = session.query(BookStaging.shelves).all()

        seen = set()

        for (shelves,) in rows:

            if not shelves:
                continue

            for s in shelves.split(","):

                name = normalize_shelf_name(s)

                if name and name not in seen:

                    seen.add(name)

                    exists = session.query(Shelf).filter_by(
                        name=name
                    ).first()

                    if not exists:
                        session.add(Shelf(name=name))

        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


