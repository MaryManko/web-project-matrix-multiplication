import os
import time
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Task

# --- НАЛАШТУВАННЯ ---
redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
db_host = os.getenv("DB_HOST", "127.0.0.1")
db_port = os.getenv("DB_PORT", "5433") 

# Створюємо власне підключення до БД для воркера (щоб не залежати від інших файлів)
DATABASE_URL = f"postgresql://user:password@{db_host}:{db_port}/math_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

celery_app = Celery(
    "worker",
    broker=redis_url,
    backend=redis_url
)

@celery_app.task(name="calculate_matrix")
def calculate_matrix_task(task_db_id: int, matrix_size: int):
    # Кожного разу створюємо НОВУ сесію
    db = SessionLocal()
    
    try:
        task = db.query(Task).filter(Task.id == task_db_id).first()
        if not task:
            return "Task not found"

        # Початок роботи
        task.status = "Processing"
        db.commit()

        # Імітація роботи
        for i in range(1, 11):
            # Перевірка на скасування (ОБОВ'ЯЗКОВО оновлюємо дані з БД)
            db.refresh(task) 
            if task.status == "Cancelled":
                return "Cancelled"
            
            time.sleep(1) # Трохи швидше (10 сек сумарно)
            task.progress = i * 10
            db.commit() # Зберігаємо прогрес (10%, 20%...)
        
        # --- ФІНАЛ ---
        # Оновлюємо об'єкт перед фінальним записом
        db.refresh(task)
        task.progress = 100
        task.status = "Completed"
        task.description += " [ГОТОВО]"
        db.commit()
        
    except Exception as e:
        print(f"ПОМИЛКА ВОКЕРА: {e}")
        # Спробуємо записати помилку в БД
        try:
            task.status = "Error"
            db.commit()
        except:
            pass
    finally:
        db.close()
    
    return "Done"