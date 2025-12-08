from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

# --- НОВА ТАБЛИЦЯ: КОРИСТУВАЧІ ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # Зв'язок: Один користувач має багато задач
    tasks = relationship("Task", back_populates="owner")

# --- ОНОВЛЕНА ТАБЛИЦЯ: ЗАДАЧІ ---
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="Pending")
    progress = Column(Integer, default=0)
    description = Column(String)
    
    # НОВЕ ПОЛЕ: Власник задачі
    # Ми кажемо, що це поле посилається на id з таблиці users
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Зв'язок: Багато задач належать одному власнику
    owner = relationship("User", back_populates="tasks")