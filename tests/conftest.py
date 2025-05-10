# conftest.py
from datetime import datetime
import pytest
import bcrypt
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
# backend.models.* импортируются для создания sample объектов, если фикстуры выносятся сюда
from backend.models.favourite_film import FavouriteFilm
from backend.models.user import User
from backend.models.review import Review


@pytest.fixture
def mock_session():
    with patch('backend.database.database.get_session') as mock_get_session_db:
        mock_session_instance = MagicMock(spec=Session)
        mock_get_session_db.return_value = mock_session_instance
        yield mock_session_instance


@pytest.fixture
def sample_favourite():
    """Фикстура для тестового объекта FavouriteFilm."""
    return FavouriteFilm(id=1, title="breaking bad", year="2k17", user_id=1, imdb_id="tt0133093",
                         type_="nevermind", poster_url=".", added_at=datetime(2024, 1, 1))  # Используем корректную дату


@pytest.fixture
def sample_user_data():
    return {"username": "testuser", "password": "password123"}


@pytest.fixture
def existing_user_in_db(sample_user_data):
    """Мок существующего пользователя в БД."""
    hashed_pw = bcrypt.hashpw(sample_user_data["password"].encode('utf-8'), bcrypt.gensalt())
    user = User(id=1, username=sample_user_data["username"], password_hash=hashed_pw.decode('utf-8'))
    return user


@pytest.fixture
def sample_review_data():
    return {
        "user_id": 1,
        "imdb_id": "tt1234567",
        "movie_title": "Test Movie",
        "rating": 5,
        "comment": "Excellent film!"
    }


@pytest.fixture
def existing_review_in_db(sample_review_data):
    """Мок существующего отзыва в БД."""
    return Review(
        id=1,
        user_id=sample_review_data["user_id"],
        imdb_id=sample_review_data["imdb_id"],
        movie_title=sample_review_data["movie_title"],  # Изначальное название
        rating=sample_review_data["rating"] - 1,  # Изначальный рейтинг
        comment="Old comment",  # Изначальный комментарий
        created_at=datetime.now()
    )
