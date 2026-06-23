from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base
from datetime import datetime


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True)
    department = Column(String)

    image_path = Column(String)
    embedding_path = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)