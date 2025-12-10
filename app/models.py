from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)


    tasks = relationship("Task", back_populates="owner")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="Pending")
    progress = Column(Integer, default=0)
    description = Column(String)
    

    owner_id = Column(Integer, ForeignKey("users.id"))


    owner = relationship("User", back_populates="tasks")