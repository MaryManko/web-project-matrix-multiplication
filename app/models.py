from sqlalchemy import Column, Integer, String, Float, Text
from .database import Base

class Task(Base):
    # Назва таблиці в базі даних буде 'tasks'
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    
    # Статус: "Pending" (в черзі), "Processing" (рахується), "Completed" (готово), "Error"
    status = Column(String, default="Pending")
    
    # Прогрес виконання у відсотках (0 - 100)
    progress = Column(Integer, default=0)
    
    # Результат обчислень (збережемо як текст або JSON)
    result = Column(Text, nullable=True)
    
    # Вхідні дані (наприклад, розмір матриці)
    description = Column(String, nullable=True)