from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import declarative_base,sessionmaker
import time
from .config import settings

SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL
if not database_exists(SQLALCHEMY_DATABASE_URL):
    create_database(SQLALCHEMY_DATABASE_URL)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base=declarative_base()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()