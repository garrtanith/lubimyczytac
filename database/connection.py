from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine


DATABASE_URL = "postgresql+psycopg2://librarian:librarian123@localhost:5432/library"

engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)

Base = declarative_base()