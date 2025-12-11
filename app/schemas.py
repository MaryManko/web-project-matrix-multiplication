from pydantic import BaseModel, EmailStr
from typing import Optional


class TaskCreate(BaseModel):
    matrix_size: int

class TaskResponse(BaseModel):
    id: int
    status: str
    progress: int
    description: str


    class Config:
        orm_mode = True



class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str