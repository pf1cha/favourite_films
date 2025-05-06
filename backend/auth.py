# backend/auth.py
import bcrypt
import psycopg2
# from backend.database import get_db_connection  # Используем общую функцию
import sys

import sqlalchemy.exc
from sqlalchemy import select

from backend.database import get_session
from backend.models.user import User


# hash_password и verify_password остаются без изменений

def hash_password(password: str) -> bytes:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password


def verify_password(plain_password: str, hashed_password_str: str) -> bool:
    try:
        plain_password_bytes = plain_password.encode('utf-8')
        hashed_password_bytes = hashed_password_str.encode('utf-8')
        return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)
    except ValueError:
        print("Ошибка: неверный формат хеша пароля в базе данных.", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Ошибка при проверке пароля: {e}", file=sys.stderr)
        return False


# register_user остается без изменений

def register_user(username: str, password: str) -> tuple[bool, str]:
    if not username or not password:
        return False, "Имя пользователя и пароль не могут быть пустыми."
    if len(password) < 6:
        return False, "Пароль должен быть не менее 6 символов."

    session = get_session()
    hashed_pw = hash_password(password)
    hashed_pw_str = hashed_pw.decode('utf-8')

    try:
        session.add(User(username=username, password_hash=hashed_pw_str))
        return True, "Пользователь успешно зарегистрирован."
    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        return False, "Пользователь с таким именем уже существует."
    except sqlalchemy.exc.DatabaseError as e:
        session.rollback()
        print(f"Ошибка БД при регистрации пользователя {username}: {e}", file=sys.stderr)
        return False, "Произошла ошибка базы данных при регистрации."
    except Exception as e:
        print(f"Неожиданная ошибка при регистрации {username}: {e}", file=sys.stderr)
        return False, "Произошла непредвиденная ошибка."


# --- ИЗМЕНЕНО: login_user ---
def login_user(username: str, password: str) -> tuple[bool, str, int | None]:
    """
    Проверяет учетные данные пользователя.
    Возвращает: (Успех?, Сообщение, user_id или None)
    """
    if not username or not password:
        return False, "Введите имя пользователя и пароль.", None

    session = get_session()

    user_id = None  # Инициализируем user_id
    try:
        user = session.execute(select(User).where(User.username == username)).scalar_one_or_none()

        if user is None:
            return False, "Пользователь не найден.", None


        if verify_password(password, user.password_hash):
            return True, "Вход выполнен успешно.", user_id  # Возвращаем user_id
        else:
            return False, "Неверный пароль.", None

    except Exception as e:
        print(f"Неожиданная ошибка при входе {username}: {e}", file=sys.stderr)
        return False, "Произошла непредвиденная ошибка.", None
