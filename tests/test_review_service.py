import pytest
from unittest.mock import MagicMock
from sqlalchemy import exc as sqlalchemy_exc
from backend.database.review_service import (
    add_review,
    get_reviews_for_movie,
    get_reviews_by_user,
    get_review_by_user_and_movie
)
from backend.models.review import Review


def test_add_review_new_review(mock_session, sample_user):
    mock_query_result = MagicMock()
    mock_query_result.filter_by.return_value.first.return_value = None
    mock_session.query.return_value = mock_query_result

    user_id = sample_user.id
    imdb_id = "tt98765"
    title = "Awesome Movie"
    rating = 5
    comment = "Loved it!"

    success, message = add_review(user_id, imdb_id, title, rating, comment)

    assert success is True
    assert message == "Отзыв успешно добавлен."
    mock_session.query.assert_called_once_with(Review)
    mock_query_result.filter_by.assert_called_once_with(user_id=user_id, imdb_id=imdb_id)

    added_review = mock_session.add.call_args[0][0]
    assert isinstance(added_review, Review)
    assert added_review.user_id == user_id
    assert added_review.imdb_id == imdb_id
    assert added_review.movie_title == title
    assert added_review.rating == rating
    assert added_review.comment == comment

    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_not_called()
    mock_session.close.assert_called_once()


def test_add_review_update_existing_review(mock_session, sample_user, sample_review):
    existing_review_mock = sample_review

    mock_query_result = MagicMock()
    mock_query_result.filter_by.return_value.first.return_value = existing_review_mock
    mock_session.query.return_value = mock_query_result

    user_id = sample_user.id
    imdb_id = existing_review_mock.imdb_id
    new_title = "Updated Title"
    new_rating = 3
    new_comment = "It was okay."

    success, message = add_review(user_id, imdb_id, new_title, new_rating, new_comment)

    assert success is True
    assert message == "Отзыв обновлен."

    assert existing_review_mock.rating == new_rating
    assert existing_review_mock.comment == new_comment
    assert existing_review_mock.movie_title == new_title

    mock_session.add.assert_not_called()
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_not_called()
    mock_session.close.assert_called_once()


def test_add_review_sqlalchemy_error(mock_session, sample_user, capsys):
    mock_query_result = MagicMock()
    mock_query_result.filter_by.return_value.first.return_value = None
    mock_session.query.return_value = mock_query_result
    mock_session.commit.side_effect = sqlalchemy_exc.SQLAlchemyError("DB Commit Failed")

    success, message = add_review(sample_user.id, "ttError", "Error Movie", 1, "Bad")

    assert success is False
    assert message == "Ошибка базы данных при добавлении отзыва."
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()
    captured = capsys.readouterr()
    assert f"Database error adding/updating review (user: {sample_user.id}, imdb: ttError): DB Commit Failed" in captured.err


def test_add_review_unexpected_error(mock_session, sample_user, capsys):
    mock_session.query.side_effect = Exception("Very Unexpected Error")

    success, message = add_review(sample_user.id, "ttFatal", "Fatal Movie", 1, "OhNo")

    assert success is False
    assert message == "Непредвиденная ошибка при добавлении отзыва."
    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()
    captured = capsys.readouterr()
    assert f"Unexpected error adding/updating review (user: {sample_user.id}, imdb: ttFatal): Very Unexpected Error" in captured.err


# get_reviews_for_movie tests
def test_get_reviews_for_movie_success(mock_session, sample_review):
    mock_query_result = MagicMock()
    mock_query_result.filter.return_value.order_by.return_value.all.return_value = [sample_review, sample_review]
    mock_session.query.return_value = mock_query_result

    target_imdb_id = "tt0111161"
    reviews_list = get_reviews_for_movie(target_imdb_id)

    assert len(reviews_list) == 2
    assert reviews_list[0] == sample_review
    mock_session.query.assert_called_once_with(Review)
    mock_query_result.filter.assert_called_once()
    mock_query_result.filter.return_value.order_by.return_value.all.assert_called_once()
    mock_session.close.assert_called_once()


def test_get_reviews_for_movie_none_found(mock_session):
    mock_query_result = MagicMock()
    mock_query_result.filter.return_value.order_by.return_value.all.return_value = []
    mock_session.query.return_value = mock_query_result

    reviews_list = get_reviews_for_movie("tt_no_reviews_here")
    assert reviews_list == []
    mock_session.close.assert_called_once()


def test_get_reviews_for_movie_exception(mock_session, capsys):
    mock_session.query.side_effect = Exception("DB Query Failed Miserably")

    reviews_list = get_reviews_for_movie("tt_problem_child")
    assert reviews_list == []
    mock_session.close.assert_called_once()
    captured = capsys.readouterr()
    assert "Error fetching reviews for movie (imdb: tt_problem_child): DB Query Failed Miserably" in captured.err


# get_reviews_by_user tests
def test_get_reviews_by_user_success(mock_session, sample_user, sample_review):
    mock_query_result = MagicMock()
    mock_query_result.filter.return_value.order_by.return_value.all.return_value = [sample_review]
    mock_session.query.return_value = mock_query_result

    reviews_list = get_reviews_by_user(sample_user.id)

    assert len(reviews_list) == 1
    assert reviews_list[0] == sample_review
    mock_session.close.assert_called_once()


def test_get_reviews_by_user_none_found(mock_session, sample_user):
    mock_query_result = MagicMock()
    mock_query_result.filter.return_value.order_by.return_value.all.return_value = []
    mock_session.query.return_value = mock_query_result

    reviews_list = get_reviews_by_user(sample_user.id)
    assert reviews_list == []
    mock_session.close.assert_called_once()


def test_get_reviews_by_user_exception(mock_session, sample_user, capsys):
    mock_session.query.side_effect = Exception("User Reviews Query Fail")

    reviews_list = get_reviews_by_user(sample_user.id)
    assert reviews_list == []
    mock_session.close.assert_called_once()
    captured = capsys.readouterr()
    assert f"Error fetching reviews for user (user_id: {sample_user.id}): User Reviews Query Fail" in captured.err


# get_review_by_user_and_movie tests
def test_get_review_by_user_and_movie_found(mock_session, sample_user, sample_review):
    mock_query_result = MagicMock()
    mock_query_result.filter_by.return_value.first.return_value = sample_review
    mock_session.query.return_value = mock_query_result

    review_result = get_review_by_user_and_movie(sample_user.id, sample_review.imdb_id)

    assert review_result == sample_review
    mock_query_result.filter_by.assert_called_once_with(user_id=sample_user.id, imdb_id=sample_review.imdb_id)
    mock_session.close.assert_called_once()


def test_get_review_by_user_and_movie_not_found(mock_session, sample_user):
    mock_query_result = MagicMock()
    mock_query_result.filter_by.return_value.first.return_value = None
    mock_session.query.return_value = mock_query_result

    review_result = get_review_by_user_and_movie(sample_user.id, "tt_no_such_review")
    assert review_result is None
    mock_session.close.assert_called_once()


def test_get_review_by_user_and_movie_exception(mock_session, sample_user, capsys):
    mock_session.query.side_effect = Exception("Specific Review Query Fail")

    review_result = get_review_by_user_and_movie(sample_user.id, "tt_problem_again")
    assert review_result is None
    mock_session.close.assert_called_once()
    captured = capsys.readouterr()
    assert f"Error fetching specific review (user: {sample_user.id}, imdb: tt_problem_again): Specific Review Query Fail" in captured.err