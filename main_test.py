from pipeline.extract import extract

from pipeline.load import load_books

from pipeline.transform import extract_shelves, build_relationships
from database.connection import engine, Base

Base.metadata.create_all(engine)

extract()
load_books()
extract_shelves()
build_relationships()
