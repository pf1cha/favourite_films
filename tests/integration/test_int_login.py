import pytest
from unittest.mock import patch
from PyQt6.QtCore import Qt
from frontend.login_window import LoginWindow


@pytest.fixture
def app(qapp):
    """Фикстура для создания QApplication"""
    return qapp


@pytest.fixture
def window(app):
    """Фикстура для создания и очистки окна логина"""
    win = LoginWindow()
    yield win
    win.close()


def test_successful_login_flow(window, qtbot):
    """Сценарий 1: Успешный вход в систему"""
    qtbot.keyClicks(window.username_login_input, "test_user")
    qtbot.keyClicks(window.password_login_input, "securePass123")

    with patch('frontend.login_window.login_user') as mock_login:
        mock_login.return_value = (True, "Вход выполнен успешно.", 123)

        with patch.object(window, 'accept') as mock_accept:
            qtbot.mouseClick(window.login_button, Qt.MouseButton.LeftButton)

            mock_login.assert_called_once_with("test_user", "securePass123")
            assert window.login_status_label.text() == "Вход выполнен успешно."
            mock_accept.assert_called_once()


def test_empty_fields_validation(window, qtbot):
    """Сценарий 2: Валидация пустых полей"""
    test_cases = [
        ("", "password", "Введите имя пользователя и пароль."),
        ("username", "", "Введите имя пользователя и пароль."),
        ("", "", "Введите имя пользователя и пароль.")
    ]

    for username, password, expected_msg in test_cases:
        window.username_login_input.clear()
        window.password_login_input.clear()

        if username:
            qtbot.keyClicks(window.username_login_input, username)
        if password:
            qtbot.keyClicks(window.password_login_input, password)

        with patch('backend.database.auth.login_user') as mock_login:
            qtbot.mouseClick(window.login_button, Qt.MouseButton.LeftButton)

            assert window.login_status_label.text() == expected_msg
            mock_login.assert_not_called()


def test_tab_switching(window, qtbot):
    """Сценарий 3: Переключение между вкладками входа и регистрации"""
    assert window.tab_widget.currentIndex() == 0
    assert window.login_tab_btn.isChecked()
    assert not window.register_tab_btn.isChecked()

    qtbot.mouseClick(window.register_tab_btn, Qt.MouseButton.LeftButton)
    assert window.tab_widget.currentIndex() == 1
    assert window.register_tab_btn.isChecked()
    assert not window.login_tab_btn.isChecked()

    assert window.username_reg_input.text() == ""
    assert window.password_reg_input.text() == ""
    assert window.password_reg_confirm_input.text() == ""

    qtbot.mouseClick(window.login_tab_btn, Qt.MouseButton.LeftButton)
    assert window.tab_widget.currentIndex() == 0


def test_enter_key_submission(window, qtbot):
    """Сценарий 4: Отправка формы по нажатию Enter"""
    qtbot.keyClicks(window.username_login_input, "test_user")
    qtbot.keyClicks(window.password_login_input, "testPass")

    with patch('frontend.login_window.login_user') as mock_login:
        mock_login.return_value = (True, "Вход выполнен успешно.", 123)

        qtbot.keyPress(window.password_login_input, Qt.Key.Key_Return)

        mock_login.assert_called_once_with("test_user", "testPass")
