from backend.models.favourite_film import FavouriteFilm
from backend.config.config import settings
import sys
from sqlalchemy import create_engine, Engine, select, delete
from sqlalchemy.orm import Session, sessionmaker

sqlalchemy_uri = f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

engine: Engine = create_engine(
    sqlalchemy_uri,
    echo=False
)

session_maker = sessionmaker(bind=engine)


def get_session() -> Session:
    """Возвращает сессию для работы с базой данных"""
    return session_maker()


def add_favorite(favourite: FavouriteFilm) -> tuple[bool, str]:
    session = get_session()
    try:
        session.add(favourite)
        session.commit()
        return True, "Успешно добавлено в избранное"
    except Exception as e:
        print(f"Ошибка при добавлении в избранное (user: {favourite.user_id}, imdb: {favourite.imdb_id}): {e}",
              file=sys.stderr)
        session.rollback()
        return False, "Ошибка при добавлении в избранное"


def get_all_favorites_by_user_id(user_id: int) -> list[FavouriteFilm]:
    session = get_session()
    request = session.execute(
        select(FavouriteFilm)
        .filter(FavouriteFilm.user_id == user_id)
    ).all()
    favorites_list = [film[0] for film in request]
    return favorites_list


def remove_favorite(user_id: int, imdb_id: str) -> bool:
    session = get_session()
    try:
        session.execute(delete(FavouriteFilm)
                        .where(FavouriteFilm.user_id == user_id, FavouriteFilm.imdb_id == imdb_id))
        session.commit()
        return True
    except Exception as e:
        print(f"Ошибка при удалении из избранного (user: {user_id}, imdb: {imdb_id}): {e}", file=sys.stderr)
        session.rollback()
        return False
