import os
import random  
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Task


redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
db_host = os.getenv("DB_HOST", "127.0.0.1")
db_port = os.getenv("DB_PORT", "5433")


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

    db = SessionLocal()
    
    try:
        task = db.query(Task).filter(Task.id == task_db_id).first()
        if not task:
            return "Task not found"


        task.status = "Processing"
        task.description += f" [Генеруємо матриці...]"
        db.commit()

        
        matrix_a = [[random.randint(1, 10) for _ in range(matrix_size)] for _ in range(matrix_size)]
        matrix_b = [[random.randint(1, 10) for _ in range(matrix_size)] for _ in range(matrix_size)]
        
        result = [[0] * matrix_size for _ in range(matrix_size)]

        task.description = task.description.replace(" [Генеруємо матриці...]", "")
        db.commit()

       
        for i in range(matrix_size):
            
            
            if i % 10 == 0:
                db.refresh(task)
                if task.status == "Cancelled":
                    return "Cancelled"
                
                
                percent = int((i / matrix_size) * 100)
                task.progress = percent
                db.commit()

            for j in range(matrix_size):
                for k in range(matrix_size):
                    result[i][j] += matrix_a[i][k] * matrix_b[k][j]

        db.refresh(task)
        task.progress = 100
        task.status = "Completed"
        task.description += " [ОБЧИСЛЕНО]"
        db.commit()
        
    except Exception as e:
        print(f"ПОМИЛКА ВОКЕРА: {e}")

        try:
            task.status = "Error"
            task.description += f" Error: {str(e)}"
            db.commit()
        except:
            pass
    finally:
        db.close()
    
    return "Done"