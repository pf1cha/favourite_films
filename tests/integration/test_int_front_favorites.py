import pytest
from unittest.mock import patch, MagicMock
from PyQt6.QtWidgets import QApplication, QMessageBox
from frontend.tabs.favorites_tab import FavoritesTab
from backend.models.favourite_film import FavouriteFilm


@pytest.fixture(scope="module")
def qapp():
    """Фикстура для создания QApplication"""
    app = QApplication([])
    yield app
    app.quit()


@pytest.fixture
def favorites_tab(qapp):
    """Фикстура для создания вкладки избранного с моками"""
    with patch('frontend.tabs.favorites_tab.get_all_favorites_by_user_id') as mock_get_favs:
        mock_get_favs.return_value = []
        tab = FavoritesTab(1)
        yield tab
        tab.close()


def test_favorites_tab_initial_state(favorites_tab):
    """Тест начального состояния вкладки избранного"""
    assert favorites_tab.favorites_list.count() == 0
    assert favorites_tab.remove_favorite_button.isEnabled() is False
    assert favorites_tab.leave_review_button.isEnabled() is False
    assert "пока пуст" in favorites_tab.status_label.text()


def test_load_favorites_with_data(favorites_tab):
    """Тест загрузки избранных фильмов с данными"""
    test_film = FavouriteFilm(
        title="Тестовый фильм",
        year="2023",
        imdb_id="tt1234567",
        user_id=1
    )

    with patch('frontend.tabs.favorites_tab.get_all_favorites_by_user_id') as mock_get_favs:
        mock_get_favs.return_value = [test_film]
        favorites_tab.load_favorites()

        assert favorites_tab.favorites_list.count() == 1
        assert "Найдено фильмов: 1" in favorites_tab.status_label.text()


def test_remove_favorite_flow(favorites_tab):
    """Тест процесса удаления фильма из избранного"""
    test_film = FavouriteFilm(
        title="Фильм для удаления",
        imdb_id="tt9999999",
        user_id=1
    )

    with patch('frontend.tabs.favorites_tab.get_all_favorites_by_user_id') as mock_get_favs, \
            patch('frontend.tabs.favorites_tab.remove_favorite') as mock_remove_fav, \
            patch('frontend.tabs.favorites_tab.QMessageBox.question') as mock_question, \
            patch('frontend.tabs.favorites_tab.QMessageBox.information'):
        mock_get_favs.return_value = [test_film]
        mock_question.return_value = QMessageBox.StandardButton.Yes
        mock_remove_fav.return_value = True

        favorites_tab.load_favorites()
        favorites_tab.favorites_list.setCurrentRow(0)
        favorites_tab.remove_favorite_button.click()

        mock_remove_fav.assert_called_once_with(1, "tt9999999")
        assert favorites_tab.favorites_list.count() == 0


def test_leave_review_flow(favorites_tab):
    """Тест процесса добавления отзыва"""
    test_film = FavouriteFilm(
        title="Фильм для отзыва",
        imdb_id="tt1111111",
        user_id=1
    )

    with patch('frontend.tabs.favorites_tab.get_all_favorites_by_user_id') as mock_get_favs, \
            patch('frontend.tabs.favorites_tab.ReviewDialog') as mock_dialog:
        mock_get_favs.return_value = [test_film]
        mock_dialog_instance = MagicMock()
        mock_dialog.return_value = mock_dialog_instance

        favorites_tab.load_favorites()
        favorites_tab.favorites_list.setCurrentRow(0)
        favorites_tab.leave_review_button.click()

        mock_dialog.assert_called_once()
        mock_dialog_instance.exec.assert_called_once()