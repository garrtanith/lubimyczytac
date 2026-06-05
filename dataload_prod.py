from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

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