from datetime import datetime

import pytest
from unittest.mock import MagicMock, patch

from sqlalchemy import DateTime
from sqlalchemy.orm import Session
from backend.database.database import get_session  # Замените `your_module` на имя вашего модуля
from backend.models.user import User
from backend.models.favourite_film import FavouriteFilm

@pytest.fixture
def mock_session():
    """Фикстура для мока сессии SQLAlchemy."""
    with patch('backend.database.database.get_session') as mock_get_session:
        mock_session = MagicMock(spec=Session)
        mock_get_session.return_value = mock_session
        yield mock_session


@pytest.fixture
def sample_favourite():
    """Фикстура для тестового объекта FavouriteFilm."""
    return FavouriteFilm(id= 1, title="breaking bad", year="2k17", user_id=1, imdb_id="tt0133093", type_="nevermind", poster_url=".", added_at=datetime(1, 1, 24))

