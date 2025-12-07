from pydantic import BaseModel

# Це те, що клієнт надсилає нам (тільки розмір матриці)
class TaskCreate(BaseModel):
    matrix_size: int

# Це те, що ми відповідаємо клієнту (ID задачі і статус)
class TaskResponse(BaseModel):
    id: int
    status: str
    progress: int
    description: str

    class Config:
        from_attributes = True