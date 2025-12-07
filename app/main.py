import socket
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from . import models, database, schemas
from .worker import calculate_matrix_task

# Створюємо таблиці в базі даних
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Підключаємо статику (Frontend)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Функція для отримання сесії бази даних
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Головна сторінка
@app.get("/")
def read_root():
    return FileResponse("app/static/index.html")

# Створення задачі
@app.post("/tasks", response_model=schemas.TaskResponse)
def create_task(task_data: schemas.TaskCreate, db: Session = Depends(get_db)):

    # Створюємо задачу в БД
    new_task = models.Task(
        status="Pending",
        progress=0,
        description=f"Матриця {task_data.matrix_size}x{task_data.matrix_size}"
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    # Відправляємо в чергу
    calculate_matrix_task.delay(new_task.id, task_data.matrix_size)
    
    return new_task

# Отримання списку задач (З СОРТУВАННЯМ)
@app.get("/tasks", response_model=list[schemas.TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    # Сортуємо: нові зверху (desc - descending, спадання)
    tasks = db.query(models.Task).order_by(models.Task.id.desc()).all()
    return tasks

# Скасування задачі
@app.post("/tasks/{task_id}/cancel")
def cancel_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Задачу не знайдено")
    
    if task.status in ["Completed", "Error"]:
        return {"message": "Пізно скасовувати"}

    task.status = "Cancelled"
    task.description += " [СКАСОВАНО]"
    db.commit()
    
    return {"message": "Задачу скасовано"}