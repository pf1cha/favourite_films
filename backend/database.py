import psycopg2
from backend.config import DATABASE_CONFIG
import sys


def get_db_connection():
    """Устанавливает соединение с базой данных."""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Ошибка подключения к базе данных: {e}", file=sys.stderr)
        return None


def create_users_table_if_not_exists():
    """Создает таблицу users, если она не существует."""
    conn = get_db_connection()
    if not conn: return False
    sql = """
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        print("Таблица 'users' проверена/создана.")
        return True
    except psycopg2.Error as e:
        print(f"Ошибка при создании таблицы 'users': {e}", file=sys.stderr)
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def create_favorites_table_if_not_exists():
    """Создает таблицу favorites, если она не существует."""
    conn = get_db_connection()
    if not conn: return False
    sql = """
    CREATE TABLE IF NOT EXISTS favorites (
        favorite_id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        imdb_id VARCHAR(20) NOT NULL,
        title VARCHAR(255) NOT NULL,
        year VARCHAR(20),
        type VARCHAR(50),
        poster_url TEXT,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_user
            FOREIGN KEY(user_id)
            REFERENCES users(user_id)
            ON DELETE CASCADE,
        CONSTRAINT uq_user_movie UNIQUE (user_id, imdb_id)
    );
    CREATE INDEX IF NOT EXISTS idx_favorites_user_id ON favorites (user_id);
    CREATE INDEX IF NOT EXISTS idx_favorites_imdb_id ON favorites (imdb_id);
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        print("Таблица 'favorites' проверена/создана.")
        return True
    except psycopg2.Error as e:
        print(f"Ошибка при создании таблицы 'favorites' или индексов: {e}", file=sys.stderr)
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def add_favorite(user_id: int, imdb_id: str, title: str, year: str, type: str, poster_url: str) -> bool:
    conn = get_db_connection()
    if not conn: return False
    sql = """
        INSERT INTO favorites (user_id, imdb_id, title, year, type, poster_url)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id, imdb_id) DO NOTHING;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id, imdb_id, title, year, type, poster_url))
            conn.commit()
            return cur.rowcount > 0
    except psycopg2.Error as e:
        print(f"Ошибка при добавлении в избранное (user: {user_id}, imdb: {imdb_id}): {e}", file=sys.stderr)
        conn.rollback();
        return False
    finally:
        if conn: conn.close()


def get_all_favorites(user_id: int) -> list[dict]:
    conn = get_db_connection()
    if not conn: return []
    favorites_list = []
    sql = "SELECT imdb_id, title, year, type, poster_url FROM favorites WHERE user_id = %s ORDER BY added_at DESC;"
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            rows = cur.fetchall()
            for row in rows:
                favorites_list.append(
                    {'imdb_id': row[0], 'title': row[1], 'year': row[2], 'type': row[3], 'poster_url': row[4]})
    except psycopg2.Error as e:
        print(f"Ошибка при получении списка избранного (user: {user_id}): {e}", file=sys.stderr)
    finally:
        if conn: conn.close()
    return favorites_list


def remove_favorite(user_id: int, imdb_id: str) -> bool:
    conn = get_db_connection()
    if not conn: return False
    sql = "DELETE FROM favorites WHERE user_id = %s AND imdb_id = %s;"
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id, imdb_id))
            conn.commit()
            return cur.rowcount > 0
    except psycopg2.Error as e:
        print(f"Ошибка при удалении из избранного (user: {user_id}, imdb: {imdb_id}): {e}", file=sys.stderr)
        conn.rollback();
        return False
    finally:
        if conn: conn.close()
