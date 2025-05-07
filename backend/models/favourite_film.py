from datetime import datetime

from sqlalchemy import Column, Integer, DATETIME, ForeignKey, DateTime
from sqlalchemy.orm import Relationship, relationship
from sqlalchemy.types import Text, Boolean
from .base import Base

class FavouriteFilm(Base):
    __tablename__ = "favourites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text)
    year = Column(Integer)
    type_ = Column(Text)
    poster_url = Column(Text)
    added_at = Column(DateTime, default=datetime.now())

    user_id = Column(ForeignKey("public.users.id"))
    user = relationship("User")
    imdb_id = Column(Integer)
