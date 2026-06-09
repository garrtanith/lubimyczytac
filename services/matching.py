from models.models import Book


def find_existing_book(session,r):

    if r.isbn and r.isbn.strip():
        return session.query(Book).filter_by(
            isbn=r.isbn
        ).first()

    return session.query(Book).filter_by(
        title=r.title,
        author=r.author
    ).first()
