from datetime import datetime
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from backend.models.favourite_film import FavouriteFilm
from backend.models.user import User
from backend.models.review import Review


@pytest.fixture
def mock_session():
    with patch('backend.database.database.get_session') as mock_get_session_db_database, \
            patch('backend.database.auth.get_session') as mock_get_session_auth, \
            patch('backend.database.review_service.get_session') as mock_get_session_review:
        mock_session_instance = MagicMock(spec=Session)

        mock_get_session_db_database.return_value = mock_session_instance
        mock_get_session_auth.return_value = mock_session_instance
        mock_get_session_review.return_value = mock_session_instance

        mock_session_instance.add = MagicMock()
        mock_session_instance.commit = MagicMock()
        mock_session_instance.rollback = MagicMock()
        mock_session_instance.close = MagicMock()
        mock_session_instance.execute = MagicMock()
        mock_session_instance.query = MagicMock()

        yield mock_session_instance


@pytest.fixture
def sample_favourite():
    """Фикстура для тестового объекта FavouriteFilm."""
    return FavouriteFilm(id=1, title="breaking bad", year="2k17", user_id=1, imdb_id="tt0133093",
                         type_="nevermind", poster_url=".", added_at=datetime(2024, 1, 1))


@pytest.fixture
def sample_user():
    """Фикстура для тестового объекта User."""
    return User(id=1, username="testuser",
                password_hash="hashed_password_str_from_db", created_at=datetime(2024, 1, 1), )


@pytest.fixture
def sample_review(sample_user):
    """Фикстура для тестового объекта Review."""
    return Review(
        id=1,
        user_id=sample_user.id,
        imdb_id="tt0111161",
        movie_title="The Shawshank Redemption",
        rating=5,
        comment="Great movie!",
        created_at=datetime(2024, 1, 1),
        user=sample_user
    )
