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
        conn.rollback()
        return False
    finally:
        if conn: conn.close()


VALID_SORT_ORDERS = {
    'date_desc': 'added_at DESC',
    'date_asc': 'added_at ASC',
    'title_asc': 'title ASC',
    'title_desc': 'title DESC',
}
DEFAULT_SORT_ORDER = 'date_desc'


def get_all_favorites(user_id: int, sort_by: str = DEFAULT_SORT_ORDER) -> list[dict]:
    conn = get_db_connection()
    if not conn:
        print("Ошибка: Не удалось получить соединение с БД для get_all_favorites.", file=sys.stderr)
        return []

    order_clause = VALID_SORT_ORDERS.get(sort_by, VALID_SORT_ORDERS[DEFAULT_SORT_ORDER])

    favorites_list = []
    sql = f"""
        SELECT imdb_id, title, year, type, poster_url
        FROM favorites
        WHERE user_id = %s
        ORDER BY {order_clause};
    """

    try:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id,))
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
        print(f"Ошибка при получении списка избранного (user: {user_id}, sort: {sort_by}): {e}", file=sys.stderr)
        return []
    finally:
        if conn:
            conn.close()

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
        conn.rollback()
        return False
    finally:
        if conn: conn.close()


def create_reviews_table_if_not_exists():
    """Создает таблицу reviews и связанные объекты, если они не существуют."""
    conn = get_db_connection()
    if not conn: return False
    # SQL взят из Шага 2.1
    sql = """
    CREATE TABLE IF NOT EXISTS reviews (
        review_id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        imdb_id VARCHAR(20) NOT NULL,
        rating INT CHECK (rating IS NULL OR (rating >= 1 AND rating <= 5)),
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_review_user
            FOREIGN KEY(user_id)
            REFERENCES users(user_id)
            ON DELETE CASCADE,
        CONSTRAINT uq_user_movie_review UNIQUE (user_id, imdb_id)
    );
    CREATE INDEX IF NOT EXISTS idx_reviews_user_id ON reviews (user_id);
    CREATE INDEX IF NOT EXISTS idx_reviews_imdb_id ON reviews (imdb_id);

    -- Создание или замена функции для триггера
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
       NEW.updated_at = NOW();
       RETURN NEW;
    END;
    $$ language 'plpgsql';

    -- Удаляем старый триггер перед созданием нового
    DROP TRIGGER IF EXISTS update_reviews_updated_at ON reviews;
    -- Создание триггера
    CREATE TRIGGER update_reviews_updated_at
    BEFORE UPDATE ON reviews
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        print("Таблица 'reviews' и связанные объекты проверены/созданы.")
        return True
    except psycopg2.Error as e:
        print(f"Ошибка при создании таблицы 'reviews' или связанных объектов: {e}", file=sys.stderr)
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def add_or_update_review(user_id: int, imdb_id: str, rating: int | None, comment: str | None) -> bool:
    """Добавляет или обновляет отзыв пользователя на фильм."""
    conn = get_db_connection()
    if not conn: return False

    comment_to_save = comment if comment and comment.strip() else None
    rating_to_save = rating if rating is not None and rating > 0 else None

    sql = """
    INSERT INTO reviews (user_id, imdb_id, rating, comment)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (user_id, imdb_id) DO UPDATE SET
        rating = EXCLUDED.rating,
        comment = EXCLUDED.comment,
        updated_at = NOW();
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id, imdb_id, rating_to_save, comment_to_save))
        conn.commit()
        return True
    except psycopg2.Error as e:
        print(f"Ошибка при добавлении/обновлении отзыва (user: {user_id}, imdb: {imdb_id}): {e}", file=sys.stderr)
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def get_review(user_id: int, imdb_id: str) -> tuple[int | None, str | None]:
    """Получает существующий отзыв пользователя на фильм. Возвращает (rating, comment)."""
    conn = get_db_connection()
    if not conn: return (None, None)

    sql = "SELECT rating, comment FROM reviews WHERE user_id = %s AND imdb_id = %s;"
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id, imdb_id))
            result = cur.fetchone()
            if result:
                return result[0], result[1]  # rating, comment
            else:
                return None, None
    except psycopg2.Error as e:
        print(f"Ошибка при получении отзыва (user: {user_id}, imdb: {imdb_id}): {e}", file=sys.stderr)
        return None, None
    finally:
        if conn:
            conn.close()


def get_user_reviews(user_id: int) -> list[dict]:
    """Получает все отзывы, оставленные пользователем."""
    conn = get_db_connection()
    if not conn: return []
    reviews = []
    sql = """
        SELECT r.review_id, r.imdb_id, r.rating, r.comment, r.updated_at, f.title
        FROM reviews r
        LEFT JOIN favorites f ON r.user_id = f.user_id AND r.imdb_id = f.imdb_id
        WHERE r.user_id = %s
        ORDER BY r.updated_at DESC;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            rows = cur.fetchall()
            for row in rows:
                reviews.append({
                    'review_id': row[0],
                    'imdb_id': row[1],
                    'rating': row[2],
                    'comment': row[3],
                    'updated_at': row[4],
                    'title': row[5] if len(row) > 5 and row[5] else "Название не найдено"
                })
    except psycopg2.Error as e:
        print(f"Ошибка при получении отзывов пользователя {user_id}: {e}", file=sys.stderr)
    finally:
        if conn: conn.close()
    return reviews


def delete_review(review_id: int) -> bool:
    """Удаляет отзыв по его ID."""
    conn = get_db_connection()
    if not conn: return False
    sql = "DELETE FROM reviews WHERE review_id = %s;"
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (review_id,))
            conn.commit()
            return cur.rowcount > 0  # True если удалено
    except psycopg2.Error as e:
        print(f"Ошибка при удалении отзыва ID {review_id}: {e}", file=sys.stderr)
        conn.rollback()
        return False
    finally:
        if conn: conn.close()
