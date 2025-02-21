from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import os

load_dotenv()
db_name = os.getenv("DATABASE_NAME")
db_user = os.getenv("DATABASE_USER")
db_password = os.getenv("DATABASE_PASSWORD")
db_host = os.getenv("DATABASE_HOST")

DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()