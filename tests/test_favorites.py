import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError
from backend.database.database import (
    add_favorite,
    remove_favorite
)
from backend.models.favourite_film import FavouriteFilm
from datetime import datetime


@pytest.fixture
def mock_db_session():
    """Фикстура для мокирования сессии БД"""
    with patch('backend.database.database.get_session') as mock_get_session:
        session = MagicMock()
        mock_get_session.return_value = session
        yield session


@pytest.fixture
def sample_favorite():
    return FavouriteFilm(
        id=1,
        title="Inception",
        year="2010",
        imdb_id="tt1375666",
        type_="movie",
        poster_url="http://example.com/poster.jpg",
        user_id=1,
        added_at=datetime(2023, 1, 1)
    )


def test_scenario_successful_favorite_addition(mock_db_session, sample_favorite):
    """Сценарий 1: Успешное добавление фильма в избранное"""
    mock_db_session.commit.return_value = None

    success, message = add_favorite(sample_favorite)

    assert success is True
    assert message == "Успешно добавлено в избранное"
    mock_db_session.add.assert_called_once_with(sample_favorite)
    mock_db_session.commit.assert_called_once()


def test_scenario_duplicate_favorite_addition(mock_db_session, sample_favorite):
    """Сценарий 2: Попытка добавить дубликат фильма"""

    mock_db_session.commit.side_effect = IntegrityError("Duplicate entry", params=None, orig=None)

    success, message = add_favorite(sample_favorite)

    assert success is False
    assert "Ошибка при добавлении в избранное" in message
    mock_db_session.rollback.assert_called_once()



def test_scenario_successful_favorite_removal(mock_db_session):
    """Сценарий 4: Успешное удаление фильма из избранного"""
    mock_db_session.commit.return_value = None

    mock_db_session.execute.return_value.rowcount = 1

    success = remove_favorite(user_id=1, imdb_id="tt1375666")

    assert success is True
    mock_db_session.commit.assert_called_once()


    delete_query = str(mock_db_session.execute.call_args[0][0])
    assert "DELETE FROM public.favourites" in delete_query
    assert "public.favourites.user_id = :user_id_1" in delete_query
    assert "public.favourites.imdb_id = :imdb_id_1" in delete_query

def test_scenario_remove_nonexistent_favorite(mock_db_session):
    """Сценарий 5: Удаление несуществующего фильма"""
    mock_db_session.execute.return_value.rowcount = 0

    success = remove_favorite(user_id=1, imdb_id="tt9999999")

    assert success is True
    mock_db_session.commit.assert_called_once()


def test_scenario_database_error_during_removal(mock_db_session):
    """Сценарий 6: Ошибка БД при удалении фильма"""
    mock_db_session.commit.side_effect = Exception("Database error")

    success = remove_favorite(user_id=1, imdb_id="tt1375666")

    assert success is False
    mock_db_session.rollback.assert_called_once()