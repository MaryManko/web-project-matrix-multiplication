from pydantic import BaseModel, EmailStr
from typing import Optional

# --- СХЕМИ ДЛЯ ЗАДАЧ ---
class TaskCreate(BaseModel):
    matrix_size: int

class TaskResponse(BaseModel):
    id: int
    status: str
    progress: int
    description: str
    # owner_id ми не показуємо, це внутрішня кухня

    class Config:
        orm_mode = True

# --- НОВІ СХЕМИ ДЛЯ КОРИСТУВАЧА ---

# Що ми отримуємо при реєстрації
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Що ми віддаємо (пароль показувати не можна!)
class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True

# Схема для Токена (цифрової перепустки)
class Token(BaseModel):
    access_token: str
    token_type: str