from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(100), unique=True, nullable=False)

    email = Column(String(255), unique=True, nullable=False)

    password = Column(String(255), nullable=False)

    role = Column(String(20), default="admin")

    created_at = Column(DateTime, default=datetime.utcnow)