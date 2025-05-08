import sys
from sqlalchemy import select, exc
from backend.database.database import get_session
from backend.models.review import Review
from backend.models.user import User


def add_review(user_id: int, imdb_id: str, movie_title: str, rating: int, comment: str) -> tuple[bool, str]:
    """Adds a new review to the database."""
    session = get_session()
    try:
        existing_review = session.query(Review).filter_by(user_id=user_id, imdb_id=imdb_id).first()
        if existing_review:
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.movie_title = movie_title
            message = "Отзыв обновлен."
        else:
            print(user_id, imdb_id, movie_title, rating, comment)
            new_review = Review(
                user_id=user_id,
                imdb_id=imdb_id,
                movie_title=movie_title,
                rating=rating,
                comment=comment
            )
            session.add(new_review)
            message = "Отзыв успешно добавлен."

        session.commit()
        return True, message
    except exc.SQLAlchemyError as e:
        session.rollback()
        print(f"Database error adding/updating review (user: {user_id}, imdb: {imdb_id}): {e}", file=sys.stderr)
        return False, "Ошибка базы данных при добавлении отзыва."
    except Exception as e:
        session.rollback()
        print(f"Unexpected error adding/updating review (user: {user_id}, imdb: {imdb_id}): {e}", file=sys.stderr)
        return False, "Непредвиденная ошибка при добавлении отзыва."
    finally:
        session.close()


def get_reviews_for_movie(imdb_id: str) -> list[Review]:
    """Fetches all reviews for a specific movie, optionally joining with user info."""
    session = get_session()
    try:
        reviews = session.query(Review).filter(Review.imdb_id == imdb_id).order_by(Review.created_at.desc()).all()
        return reviews
    except Exception as e:
        print(f"Error fetching reviews for movie (imdb: {imdb_id}): {e}", file=sys.stderr)
        return []
    finally:
        session.close()


def get_reviews_by_user(user_id: int) -> list[Review]:
    """Fetches all reviews made by a specific user."""
    session = get_session()
    try:
        reviews = session.query(Review).filter(Review.user_id == user_id).order_by(Review.created_at.desc()).all()
        return reviews
    except Exception as e:
        print(f"Error fetching reviews for user (user_id: {user_id}): {e}", file=sys.stderr)
        return []
    finally:
        session.close()


def get_review_by_user_and_movie(user_id: int, imdb_id: str) -> Review | None:
    """Fetches a specific review by a user for a movie, if it exists."""
    session = get_session()
    try:
        review = session.query(Review).filter_by(user_id=user_id, imdb_id=imdb_id).first()
        return review
    except Exception as e:
        print(f"Error fetching specific review (user: {user_id}, imdb: {imdb_id}): {e}", file=sys.stderr)
        return None
    finally:
        session.close()