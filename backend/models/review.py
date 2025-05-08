from datetime import datetime

from pydantic.v1.schema import schema
from sqlalchemy import Column, Integer, Text, ForeignKey, String, TIMESTAMP
from sqlalchemy.orm import relationship
from backend.models.base import Base
from sqlalchemy import UniqueConstraint

class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint('user_id', 'imdb_id', name='_user_movie_review_uc'),
        {'schema': 'public'}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("public.users.id"), nullable=False)
    imdb_id = Column(String(20), nullable=False)
    movie_title = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.now)

    user = relationship("User")
