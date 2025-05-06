from datetime import datetime

from sqlalchemy import Column, Integer, DATETIME
from sqlalchemy.types import Text, Boolean
from .base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(Text, unique=True)
    password_hash = Column(Text)
    created_at = Column(DATETIME, default=datetime.now())
