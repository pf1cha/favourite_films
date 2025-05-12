from unittest.mock import MagicMock
from backend.database.database import add_favorite, get_all_favorites_by_user_id, remove_favorite
from backend.models.favourite_film import FavouriteFilm


def test_add_favorite_success(mock_session, sample_favourite):
    mock_session.commit.return_value = None
    success, message = add_favorite(sample_favourite)

    assert success is True
    assert message == "Успешно добавлено в избранное"
    mock_session.add.assert_called_once_with(sample_favourite)
    mock_session.commit.assert_called_once()


def test_add_favorite_failure(mock_session, sample_favourite):
    mock_session.commit.side_effect = Exception("DB error")
    success, message = add_favorite(sample_favourite)

    assert success is False
    assert message == "Ошибка при добавлении в избранное"
    mock_session.rollback.assert_called_once()


def test_get_all_favorites_by_user_id(mock_session, sample_favourite):
    mock_result = MagicMock()
    mock_result.all.return_value = [(sample_favourite,)]
    mock_session.execute.return_value = mock_result

    favorites = get_all_favorites_by_user_id(1)

    assert favorites == [sample_favourite]

    called_args = mock_session.execute.call_args[0][0]

    assert str(called_args).startswith("SELECT")
    assert "favourites.user_id" in str(called_args)
    assert "1" in str(called_args)


def test_remove_favorite_success(mock_session):
    mock_session.commit.return_value = None
    success = remove_favorite(1, "tt0133093")

    assert success is True

    called_delete = mock_session.execute.call_args[0][0]
    assert str(called_delete).startswith("DELETE")
    assert called_delete.whereclause.compare(
        (FavouriteFilm.user_id == 1) &
        (FavouriteFilm.imdb_id == "tt0133093")
    )

    mock_session.commit.assert_called_once()


def test_remove_favorite_failure(mock_session):
    mock_session.commit.side_effect = Exception("DB error")
    success = remove_favorite(1, "tt0133093")

    assert success is False
    mock_session.rollback.assert_called_once()
