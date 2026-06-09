from pipeline.extract import extract, load_csv_to_staging, get_latest_csv
from pipeline.load import load_books
from pipeline.transform import extract_shelves, build_relationships
from database.connection import engine, Base

Base.metadata.create_all(engine)

#extract()
batch_id = load_csv_to_staging(get_latest_csv())
load_books(batch_id)
extract_shelves(batch_id)
build_relationships(batch_id)
