# # tests/backend/database/test_review_service.py
# import pytest
# from unittest.mock import patch, MagicMock, ANY
# import sqlalchemy.exc
# from datetime import datetime
#
# from backend.database.review_service import (
#     add_review, get_reviews_for_movie, get_reviews_by_user, get_review_by_user_and_movie
# )
# from backend.models.review import Review
#
#
# # Фикстура mock_session будет браться из conftest.py
#
#
# def test_add_review_new_success(mock_session, sample_review_data):
#     # Мокаем mock_session.query().filter_by().first() -> None (нет существующего)
#     mock_query = MagicMock()
#     mock_query.filter_by.return_value.first.return_value = None
#     mock_session.query.return_value = mock_query
#
#     success, message = add_review(
#         sample_review_data["user_id"],
#         sample_review_data["imdb_id"],
#         sample_review_data["movie_title"],
#         sample_review_data["rating"],
#         sample_review_data["comment"]
#     )
#
#     assert success is True
#     assert message == "Отзыв успешно добавлен."
#     mock_session.add.assert_called_once()
#     added_review = mock_session.add.call_args[0][0]
#     assert isinstance(added_review, Review)
#     assert added_review.user_id == sample_review_data["user_id"]
#     assert added_review.imdb_id == sample_review_data["imdb_id"]
#     assert added_review.movie_title == sample_review_data["movie_title"]
#     assert added_review.rating == sample_review_data["rating"]
#     assert added_review.comment == sample_review_data["comment"]
#     mock_session.commit.assert_called_once()
#     mock_session.close.assert_called_once()
#
#
# def test_add_review_update_existing_success(mock_session, existing_review_in_db, sample_review_data):
#     # Мокаем mock_session.query().filter_by().first() -> existing_review_in_db
#     mock_query = MagicMock()
#     mock_query.filter_by.return_value.first.return_value = existing_review_in_db
#     mock_session.query.return_value = mock_query
#
#     success, message = add_review(
#         sample_review_data["user_id"],  # тот же user_id
#         sample_review_data["imdb_id"],  # тот же imdb_id
#         "Updated Movie Title",  # новое название
#         sample_review_data["rating"],  # новый рейтинг
#         "Updated comment"  # новый комментарий
#     )
#
#     assert success is True
#     assert message == "Отзыв обновлен."
#     assert existing_review_in_db.movie_title == "Updated Movie Title"
#     assert existing_review_in_db.rating == sample_review_data["rating"]
#     assert existing_review_in_db.comment == "Updated comment"
#     mock_session.add.assert_not_called()  # Не должно быть нового добавления
#     mock_session.commit.assert_called_once()
#     mock_session.close.assert_called_once()
#
#
# def test_add_review_db_error(mock_session, sample_review_data, capsys):
#     mock_query = MagicMock()
#     mock_query.filter_by.return_value.first.return_value = None  # Пытаемся добавить новый
#     mock_session.query.return_value = mock_query
#     mock_session.commit.side_effect = sqlalchemy.exc.SQLAlchemyError("DB write error")
#
#     success, message = add_review(
#         sample_review_data["user_id"],
#         sample_review_data["imdb_id"],
#         sample_review_data["movie_title"],
#         sample_review_data["rating"],
#         sample_review_data["comment"]
#     )
#
#     assert success is False
#     assert message == "Ошибка базы данных при добавлении отзыва."
#     mock_session.rollback.assert_called_once()
#     mock_session.close.assert_called_once()
#     captured = capsys.readouterr()
#     assert f"Database error adding/updating review (user: {sample_review_data['user_id']}, imdb: {sample_review_data['imdb_id']})" in captured.err
#
#
# def test_get_reviews_for_movie_success(mock_session, existing_review_in_db):
#     # Мокаем mock_session.query().filter().order_by().all()
#     mock_query = MagicMock()
#     # all() возвращает список объектов Review
#     mock_query.filter.return_value.order_by.return_value.all.return_value = [existing_review_in_db, Review(id=2,
#                                                                                                            imdb_id=existing_review_in_db.imdb_id)]
#     mock_session.query.return_value = mock_query
#
#     reviews = get_reviews_for_movie(existing_review_in_db.imdb_id)
#
#     assert len(reviews) == 2
#     assert reviews[0] == existing_review_in_db
#     # Проверяем, что был вызван filter с правильным imdb_id
#     mock_session.query(Review).filter.assert_called_once_with(Review.imdb_id == existing_review_in_db.imdb_id)
#     mock_session.close.assert_called_once()
#
#
# def test_get_reviews_for_movie_empty(mock_session):
#     mock_query = MagicMock()
#     mock_query.filter.return_value.order_by.return_value.all.return_value = []
#     mock_session.query.return_value = mock_query
#
#     reviews = get_reviews_for_movie("tt_non_existent")
#     assert reviews == []
#     mock_session.close.assert_called_once()
#
#
# def test_get_reviews_by_user_success(mock_session, existing_review_in_db):
#     mock_query = MagicMock()
#     mock_query.filter.return_value.order_by.return_value.all.return_value = [existing_review_in_db]
#     mock_session.query.return_value = mock_query
#
#     reviews = get_reviews_by_user(existing_review_in_db.user_id)
#
#     assert reviews == [existing_review_in_db]
#     mock_session.query(Review).filter.assert_called_once_with(Review.user_id == existing_review_in_db.user_id)
#     mock_session.close.assert_called_once()
#
#
# def test_get_review_by_user_and_movie_found(mock_session, existing_review_in_db):
#     mock_query = MagicMock()
#     mock_query.filter_by.return_value.first.return_value = existing_review_in_db
#     mock_session.query.return_value = mock_query
#
#     review = get_review_by_user_and_movie(existing_review_in_db.user_id, existing_review_in_db.imdb_id)
#
#     assert review == existing_review_in_db
#     mock_session.query(Review).filter_by.assert_called_once_with(user_id=existing_review_in_db.user_id,
#                                                                  imdb_id=existing_review_in_db.imdb_id)
#     mock_session.close.assert_called_once()
#
#
# def test_get_review_by_user_and_movie_not_found(mock_session):
#     mock_query = MagicMock()
#     mock_query.filter_by.return_value.first.return_value = None
#     mock_session.query.return_value = mock_query
#
#     review = get_review_by_user_and_movie(99, "tt_non_existent")
#     assert review is None
#     mock_session.close.assert_called_once()