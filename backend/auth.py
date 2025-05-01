# backend/auth.py
import bcrypt
import psycopg2
from backend.database import get_db_connection  # Используем общую функцию
import sys


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

    conn = get_db_connection()
    if not conn:
        return False, "Ошибка подключения к базе данных."

    try:
        hashed_pw = hash_password(password)
        hashed_pw_str = hashed_pw.decode('utf-8')

        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, hashed_pw_str)
            )
            conn.commit()
        return True, "Пользователь успешно зарегистрирован."

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False, "Пользователь с таким именем уже существует."
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Ошибка БД при регистрации пользователя {username}: {e}", file=sys.stderr)
        return False, "Произошла ошибка базы данных при регистрации."
    except Exception as e:
        print(f"Неожиданная ошибка при регистрации {username}: {e}", file=sys.stderr)
        return False, "Произошла непредвиденная ошибка."
    finally:
        if conn:
            conn.close()


# --- ИЗМЕНЕНО: login_user ---
def login_user(username: str, password: str) -> tuple[bool, str, int | None]:
    """
    Проверяет учетные данные пользователя.
    Возвращает: (Успех?, Сообщение, user_id или None)
    """
    if not username or not password:
        return False, "Введите имя пользователя и пароль.", None

    conn = get_db_connection()
    if not conn:
        return False, "Ошибка подключения к базе данных.", None

    user_id = None  # Инициализируем user_id
    try:
        with conn.cursor() as cur:
            # Получаем и user_id, и хеш пароля
            cur.execute(
                "SELECT user_id, password_hash FROM users WHERE username = %s",
                (username,)
            )
            result = cur.fetchone()

        if result is None:
            return False, "Пользователь не найден.", None

        user_id, stored_hash_str = result  # Распаковываем результат

        if verify_password(password, stored_hash_str):
            return True, "Вход выполнен успешно.", user_id  # Возвращаем user_id
        else:
            return False, "Неверный пароль.", None

    except psycopg2.Error as e:
        print(f"Ошибка БД при входе пользователя {username}: {e}", file=sys.stderr)
        return False, "Произошла ошибка базы данных при входе.", None
    except Exception as e:
        print(f"Неожиданная ошибка при входе {username}: {e}", file=sys.stderr)
        return False, "Произошла непредвиденная ошибка.", None
    finally:
        if conn:
            conn.close()
