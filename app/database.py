import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


db_host = os.getenv("DB_HOST", "127.0.0.1")

db_port = os.getenv("DB_PORT", "5433") 

URL_DATABASE = f"postgresql://user:password@{db_host}:{db_port}/math_db"

engine = create_engine(URL_DATABASE)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()