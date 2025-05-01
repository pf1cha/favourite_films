# backend/database.py
import psycopg2
from backend.config import DATABASE_CONFIG
import sys # Для вывода ошибок

def get_db_connection():
    """Устанавливает соединение с базой данных."""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Ошибка подключения к базе данных: {e}", file=sys.stderr)
        return None

def create_table_if_not_exists():
    """Создает таблицу favorites, если она не существует."""
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS favorites (
                    imdb_id VARCHAR(20) PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    year VARCHAR(20),
                    type VARCHAR(50),
                    poster_url TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()
        print("Таблица 'favorites' проверена/создана.")
    except psycopg2.Error as e:
        print(f"Ошибка при создании таблицы: {e}", file=sys.stderr)
    finally:
        if conn:
            conn.close()

def add_favorite(imdb_id, title, year, type, poster_url):
    """Добавляет фильм/сериал в избранное."""
    conn = get_db_connection()
    if not conn: return False
    sql = """
        INSERT INTO favorites (imdb_id, title, year, type, poster_url)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (imdb_id) DO NOTHING;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (imdb_id, title, year, type, poster_url))
            conn.commit()
            # Проверяем, была ли действительно добавлена строка (ON CONFLICT мог сработать)
            return cur.rowcount > 0
    except psycopg2.Error as e:
        print(f"Ошибка при добавлении в избранное ({imdb_id}): {e}", file=sys.stderr)
        conn.rollback() # Откатываем транзакцию при ошибке
        return False
    finally:
        if conn:
            conn.close()

def get_all_favorites():
    """Возвращает список всех избранных фильмов/сериалов."""
    conn = get_db_connection()
    if not conn: return []
    favorites_list = []
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT imdb_id, title, year, type, poster_url FROM favorites ORDER BY added_at DESC;")
            rows = cur.fetchall()
            for row in rows:
                favorites_list.append({
                    'imdb_id': row[0],
                    'title': row[1],
                    'year': row[2],
                    'type': row[3],
                    'poster_url': row[4]
                })
    except psycopg2.Error as e:
        print(f"Ошибка при получении списка избранного: {e}", file=sys.stderr)
    finally:
        if conn:
            conn.close()
    return favorites_list

def remove_favorite(imdb_id):
    """Удаляет фильм/сериал из избранного по imdb_id."""
    conn = get_db_connection()
    if not conn: return False
    sql = "DELETE FROM favorites WHERE imdb_id = %s;"
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (imdb_id,))
            conn.commit()
            return cur.rowcount > 0 # Возвращает True, если что-то было удалено
    except psycopg2.Error as e:
        print(f"Ошибка при удалении из избранного ({imdb_id}): {e}", file=sys.stderr)
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

# Создаем таблицу при первом импорте модуля
# create_table_if_not_exists() # Лучше вызвать это один раз при старте приложения