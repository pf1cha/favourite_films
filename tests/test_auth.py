# tests/backend/test_auth.py
import pytest
from unittest.mock import patch, MagicMock, ANY
import bcrypt
import sqlalchemy.exc
from backend.database.auth import (
    hash_password, verify_password, register_user, login_user
)
from backend.models.user import User  # Для проверки типа и атрибутов


# Фикстуры mock_session и sample_user (если нужен) будут браться из conftest.py
# Если sample_user нужен, его нужно добавить в conftest.py


def test_hash_password():
    password = "testpassword"
    hashed = hash_password(password)
    assert isinstance(hashed, bytes)
    assert bcrypt.checkpw(password.encode('utf-8'), hashed)


def test_verify_password_correct(existing_user_in_db, sample_user_data):
    assert verify_password(sample_user_data["password"], existing_user_in_db.password_hash) is True


def test_verify_password_incorrect(existing_user_in_db):
    assert verify_password("wrongpassword", existing_user_in_db.password_hash) is False


def test_verify_password_invalid_hash_format(capsys):  # capsys - фикстура pytest для захвата stdout/stderr
    assert verify_password("testpass", "not_a_valid_hash_str") is False
    captured = capsys.readouterr()
    assert "Ошибка: неверный формат хеша пароля в базе данных." in captured.err


@patch('backend.database.auth.hash_password')  # Мокаем, чтобы контролировать хеш
def test_register_user_success(mock_hash_password, mock_session, sample_user_data):
    mock_hash_password.return_value = b"hashed_password_bytes"  # hash_password возвращает bytes

    success, message = register_user("barcelona", "goldenstatewarriors")
    print(f"TEST_DEBUG: register_user returned success={success}, message='{message}'")
    assert success is True
    assert message == "Пользователь успешно зарегистрирован."
    mock_session.add.assert_called_once()
    added_user = mock_session.add.call_args[0][0]
    assert isinstance(added_user, User)
    assert added_user.username == sample_user_data["username"]
    assert added_user.password_hash == "hashed_password_bytes"  # hash_password_str в коде .decode('utf-8')
    mock_session.commit.assert_called_once()


def test_register_user_empty_credentials():
    success, message = register_user("", "password")
    assert success is False
    assert message == "Имя пользователя и пароль не могут быть пустыми."

    success, message = register_user("user", "")
    assert success is False
    assert message == "Имя пользователя и пароль не могут быть пустыми."


def test_register_user_short_password(sample_user_data):
    success, message = register_user(sample_user_data["username"], "pass")
    assert success is False
    assert message == "Пароль должен быть не менее 6 символов."


# @patch('backend.database.auth.hash_password')
# def test_register_user_already_exists(mock_hash_password, mock_session, sample_user_data):
#     mock_hash_password.return_value = b"hashed_password_bytes"
#     mock_session.commit.side_effect = sqlalchemy.exc.IntegrityError("mock", "mock", "mock")
#
#     success, message = register_user(sample_user_data["username"], sample_user_data["password"])
#
#     assert success is False
#     assert message == "Пользователь с таким именем уже существует."
#     mock_session.rollback.assert_called_once()


# @patch('backend.database.auth.hash_password')
# def test_register_user_db_error(mock_hash_password, mock_session, sample_user_data, capsys):
#     mock_hash_password.return_value = b"hashed_password_bytes"
#     mock_session.commit.side_effect = sqlalchemy.exc.DatabaseError("mock", "mock", "mock")
#
#     success, message = register_user(sample_user_data["username"], sample_user_data["password"])
#
#     assert success is False
#     assert message == "Произошла ошибка базы данных при регистрации."
#     mock_session.rollback.assert_called_once()
#     captured = capsys.readouterr()
#     assert f"Ошибка БД при регистрации пользователя {sample_user_data['username']}" in captured.err


# def test_login_user_success(mock_session, existing_user_in_db, sample_user_data):
#     # Мокаем результат execute().scalar_one_or_none()
#     mock_query_result = MagicMock()
#     mock_query_result.scalar_one_or_none.return_value = existing_user_in_db
#     mock_session.execute.return_value = mock_query_result
#
#     success, message, user_id = login_user(sample_user_data["username"], sample_user_data["password"])
#
#     assert success is True
#     assert message == "Вход выполнен успешно."
#     assert user_id == existing_user_in_db.id
#     mock_session.execute.assert_called_once()  # Проверка, что запрос к БД был


# def test_login_user_not_found(mock_session, sample_user_data):
#     mock_query_result = MagicMock()
#     mock_query_result.scalar_one_or_none.return_value = None  # Пользователь не найден
#     mock_session.execute.return_value = mock_query_result
#
#     success, message, user_id = login_user(sample_user_data["username"], sample_user_data["password"])
#
#     assert success is False
#     assert message == "Пользователь не найден."
#     assert user_id is None


def test_login_user_incorrect_password(mock_session, existing_user_in_db, sample_user_data):
    mock_query_result = MagicMock()
    mock_query_result.scalar_one_or_none.return_value = existing_user_in_db
    mock_session.execute.return_value = mock_query_result

    success, message, user_id = login_user(sample_user_data["username"], "wrongpassword")

    assert success is False
    assert message == "Неверный пароль."
    assert user_id is None


def test_login_user_empty_credentials():
    success, message, user_id = login_user("", "password")
    assert success is False
    assert message == "Введите имя пользователя и пароль."
    assert user_id is None

    success, message, user_id = login_user("user", "")
    assert success is False
    assert message == "Введите имя пользователя и пароль."
    assert user_id is None


# def test_login_user_unexpected_error(mock_session, sample_user_data, capsys):
#     mock_session.execute.side_effect = Exception("Unexpected DB error")
#
#     success, message, user_id = login_user(sample_user_data["username"], sample_user_data["password"])
#
#     assert success is False
#     assert message == "Произошла непредвиденная ошибка."
#     assert user_id is None
#     captured = capsys.readouterr()
#     assert f"Неожиданная ошибка при входе {sample_user_data['username']}" in captured.err