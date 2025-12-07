import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Читаємо адресу з налаштувань (або беремо стандартну для Windows)
# Ми будемо передавати DB_HOST=db через docker-compose
db_host = os.getenv("DB_HOST", "127.0.0.1")
# Порт всередині мережі докера завжди 5432
db_port = os.getenv("DB_PORT", "5433") 

URL_DATABASE = f"postgresql://user:password@{db_host}:{db_port}/math_db"

engine = create_engine(URL_DATABASE)

# SessionLocal - це "фабрика", яка створюватиме сесії роботи з БД
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base - це клас, від якого ми будемо створювати наші моделі (таблиці)
Base = declarative_base()

# Функція, щоб отримувати доступ до БД і закривати його після використання
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()