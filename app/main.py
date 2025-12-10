from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from jose import JWTError, jwt

# Імпорт моделей та схем
from . import models, database, schemas, security
from .worker import calculate_matrix_task

# Створення таблиць
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# --- CORS (ГОЛОВНЕ ВИПРАВЛЕННЯ!) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Можеш замінити на конкретний домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Авторизація
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ---- DB SESSION ----
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---- GET CURRENT USER ----
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


# ---- ROUTES ----

@app.get("/")
def read_root():
    return FileResponse("app/static/index.html")


# 1. РЕЄСТРАЦІЯ
@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Перевіряємо, чи email вже зайнятий
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = security.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# 2. ЛОГІН
@app.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# 3. СТВОРЕННЯ ЗАДАЧІ
@app.post("/tasks", response_model=schemas.TaskResponse)
def create_task(
    task_data: schemas.TaskCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if task_data.matrix_size > 2000:
        raise HTTPException(status_code=400, detail="Занадто велика матриця! Максимум 2000.")
    if task_data.matrix_size < 2:
        raise HTTPException(status_code=400, detail="Занадто мала матриця!")

    new_task = models.Task(
        status="Pending",
        progress=0,
        description=f"Матриця {task_data.matrix_size}x{task_data.matrix_size}",
        owner_id=current_user.id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    calculate_matrix_task.delay(new_task.id, task_data.matrix_size)
    return new_task


# 4. ОТРИМАННЯ ЗАДАЧ ПОТОЧНОГО КОРИСТУВАЧА
@app.get("/tasks", response_model=list[schemas.TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    tasks = db.query(models.Task).filter(models.Task.owner_id == current_user.id).order_by(models.Task.id.desc()).all()
    return tasks


# 5. СКАСУВАННЯ ЗАДАЧІ
@app.post("/tasks/{task_id}/cancel")
def cancel_task(
    task_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.owner_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Задачу не знайдено (або вона не ваша)")

    if task.status in ["Completed", "Error"]:
        return {"message": "Пізно скасовувати"}

    task.status = "Cancelled"
    task.description += " [СКАСОВАНО]"
    db.commit()
    return {"message": "Задачу скасовано"}
