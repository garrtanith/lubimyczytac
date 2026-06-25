from models.models import BookStaging, Shelf, BookShelf
from services.matching import find_existing_book
from database.connection import Session

STATUS_SHELVES = {
    "przeczytane",
    "chcę przeczytać",
    "teraz czytam"
}


def normalize_shelf_name(name):
    return name.strip().lower()

def build_relationships(batch_id):

    session = Session()

    try:

        seen_relationships = set()

        staging_rows = session.query(BookStaging).filter_by(
            load_batch=batch_id
        ).all()

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

                if shelf_name in STATUS_SHELVES:

                    current_status_relationships = (
                        session.query(BookShelf)
                        .join(Shelf)
                        .filter(
                            BookShelf.book_id == book.id,
                            Shelf.name.in_(STATUS_SHELVES)
                        )
                        .all()
                    )

                    for rel in current_status_relationships:
                        session.delete(rel)

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

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()

def extract_shelves(batch_id):

    session = Session()

    try:

        rows = session.query(BookStaging).filter_by(
            load_batch=batch_id
        ).all()
        seen = set()

        for row in rows:

            if not row.shelves:
                continue

            for s in row.shelves.split(","):

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


