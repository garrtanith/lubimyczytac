from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from database.connection import Base


class BookStaging(Base):
    __tablename__ = "books_staging"

    id = Column(Integer, primary_key=True)

    title = Column(String)
    author = Column(String)
    isbn = Column(String)
    my_rating = Column(String)
    date_read = Column(String)
    shelves = Column(String)
    load_batch = Column(String)

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

