
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, declarative_base

from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH, override=True)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if not all([DB_NAME, DB_USER, DB_PASSWORD]):
    raise ValueError("Database configuration is missing. Check your .env file.")

DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def test_database_connection():
    from sqlalchemy import text

    with engine.connect() as connection:
        result = connection.execute(text("SELECT DATABASE()"))
        return result.scalar()
