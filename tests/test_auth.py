import pytest
from unittest.mock import patch, MagicMock
import bcrypt
import sqlalchemy.exc
from backend.database.auth import hash_password, verify_password, register_user, login_user
from backend.models.user import User


# hash_password tests
@patch('backend.database.auth.bcrypt.gensalt')
@patch('backend.database.auth.bcrypt.hashpw')
def test_hash_password(mock_hashpw, mock_gensalt):
    mock_salt = b'$2b$12$saltiestsltevermakeit'
    mock_hashed_pw = b'$2b$12$saltiestsltevermakeithashed'
    mock_gensalt.return_value = mock_salt
    mock_hashpw.return_value = mock_hashed_pw

    password_to_hash = "securepassword123"
    hashed_result = hash_password(password_to_hash)

    assert hashed_result == mock_hashed_pw
    mock_gensalt.assert_called_once()
    mock_hashpw.assert_called_once_with(password_to_hash.encode('utf-8'), mock_salt)


# verify_password tests
@patch('backend.database.auth.bcrypt.checkpw')
def test_verify_password_correct(mock_checkpw):
    mock_checkpw.return_value = True
    is_valid = verify_password("plainpass", "hashedpass_str")
    assert is_valid is True
    mock_checkpw.assert_called_once_with(b"plainpass", b"hashedpass_str")


@patch('backend.database.auth.bcrypt.checkpw')
def test_verify_password_incorrect(mock_checkpw):
    mock_checkpw.return_value = False
    is_valid = verify_password("plainpass", "hashedpass_str")
    assert is_valid is False


@patch('backend.database.auth.bcrypt.checkpw', side_effect=ValueError("Invalid salt in hash"))
def test_verify_password_value_error_in_bcrypt(mock_checkpw, capsys):
    is_valid = verify_password("plainpass",
                               "badhashform")
    assert is_valid is False
    captured = capsys.readouterr()
    assert "Ошибка: неверный формат хеша пароля в базе данных." in captured.err


@patch('backend.database.auth.bcrypt.checkpw', side_effect=Exception("Some bcrypt error"))
def test_verify_password_generic_exception(mock_checkpw, capsys):
    is_valid = verify_password("plainpass", "hashedpass_str")
    assert is_valid is False
    captured = capsys.readouterr()
    assert "Ошибка при проверке пароля: Some bcrypt error" in captured.err


# register_user tests (mock_session fixture is used implicitly)

@patch('backend.database.auth.hash_password', return_value=b'hashed_pw_bytes_utf8')
def test_register_user_success(mock_hash_password_func, mock_session):
    mock_session.execute.return_value.scalar_one_or_none.return_value = None

    success, message = register_user("new_test_user", "ValidPass123")

    assert success is True
    assert message == "Пользователь успешно зарегистрирован."
    mock_hash_password_func.assert_called_once_with("ValidPass123")
    mock_session.execute.assert_called_once()
    added_user = mock_session.add.call_args[0][0]
    assert isinstance(added_user, User)
    assert added_user.username == "new_test_user"
    assert added_user.password_hash == 'hashed_pw_bytes_utf8'

    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_not_called()


@pytest.mark.parametrize("username, password, expected_msg", [
    ("", "pass123", "Имя пользователя и пароль не могут быть пустыми."),
    ("user1", "", "Имя пользователя и пароль не могут быть пустыми."),
    ("user2", "short", "Пароль должен быть не менее 6 символов."),
])
def test_register_user_invalid_input(mock_session, username, password, expected_msg):
    success, message = register_user(username, password)
    assert success is False
    assert message == expected_msg
    mock_session.add.assert_not_called()


@patch('backend.database.auth.hash_password', return_value=b'hashed_pw_bytes_utf8')
def test_register_user_already_exists(mock_hash_password_func, mock_session, sample_user):
    mock_session.execute.return_value.scalar_one_or_none.return_value = sample_user

    success, message = register_user(sample_user.username, "AnotherPass123")

    assert success is False
    assert message == "Пользователь с таким именем уже существует."
    mock_session.add.assert_not_called()


@patch('backend.database.auth.hash_password', return_value=b'hashed_pw_bytes_utf8')
def test_register_user_database_error_on_commit(mock_hash_password_func, mock_session, capsys):
    mock_session.execute.return_value.scalar_one_or_none.return_value = None
    mock_session.commit.side_effect = sqlalchemy.exc.DatabaseError("mock", "mock", "mock")

    success, message = register_user("db_error_user", "Pass123456")

    assert success is False
    assert message == "Произошла ошибка базы данных при регистрации."
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_called_once()
    captured = capsys.readouterr()
    assert "Ошибка БД при регистрации пользователя db_error_user" in captured.err


@patch('backend.database.auth.hash_password', return_value=b'hashed_pw_bytes_utf8')
def test_register_user_unexpected_error(mock_hash_password_func, mock_session, capsys):
    mock_session.execute.return_value.scalar_one_or_none.return_value = None
    mock_session.add.side_effect = Exception("Completely unexpected error")

    success, message = register_user("unexpected_user", "Pass123456")

    assert success is False
    assert message == "Произошла непредвиденная ошибка."
    mock_session.add.assert_called_once()
    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_not_called()
    captured = capsys.readouterr()
    assert "Неожиданная ошибка при регистрации unexpected_user" in captured.err


# login_user tests

def test_login_user_success(mock_session, sample_user):
    mock_session.execute.return_value.scalar_one_or_none.return_value = sample_user

    with patch('backend.database.auth.verify_password', return_value=True) as mock_verify_pw:
        success, message, user_id_result = login_user(sample_user.username, "correct_password")

        assert success is True
        assert message == "Вход выполнен успешно."
        assert user_id_result == sample_user.id
        mock_verify_pw.assert_called_once_with("correct_password", sample_user.password_hash)


@pytest.mark.parametrize("username, password, expected_msg", [
    ("", "pass", "Введите имя пользователя и пароль."),
    ("user", "", "Введите имя пользователя и пароль."),
])
def test_login_user_empty_credentials(mock_session, username, password, expected_msg):
    success, message, user_id_result = login_user(username, password)
    assert success is False
    assert message == expected_msg
    assert user_id_result is None
    mock_session.execute.assert_not_called()


def test_login_user_not_found(mock_session):
    mock_session.execute.return_value.scalar_one_or_none.return_value = None

    with patch('backend.database.auth.verify_password') as mock_verify_pw:
        success, message, user_id_result = login_user("ghost_user", "any_password")

        assert success is False
        assert message == "Пользователь не найден."
        assert user_id_result is None
        mock_verify_pw.assert_not_called()


def test_login_user_incorrect_password(mock_session, sample_user):
    mock_session.execute.return_value.scalar_one_or_none.return_value = sample_user

    with patch('backend.database.auth.verify_password', return_value=False) as mock_verify_pw:
        success, message, user_id_result = login_user(sample_user.username, "wrong_password")

        assert success is False
        assert message == "Неверный пароль."
        assert user_id_result is None
        mock_verify_pw.assert_called_once_with("wrong_password", sample_user.password_hash)


def test_login_user_unexpected_error(mock_session, capsys):
    mock_session.execute.side_effect = Exception("Sudden DB explosion")

    with patch('backend.database.auth.verify_password') as mock_verify_pw:
        success, message, user_id_result = login_user("some_user", "some_password")

        assert success is False
        assert message == "Произошла непредвиденная ошибка."
        assert user_id_result is None
        mock_verify_pw.assert_not_called()
        captured = capsys.readouterr()
        assert "Неожиданная ошибка при входе some_user" in captured.err
