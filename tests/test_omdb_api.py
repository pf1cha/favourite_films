import pytest
from unittest.mock import patch, MagicMock, call
import requests
from backend.api.omdb_client import get_movie_by_id, search_movie_by_title

OMDB_BASE_URL = "http://www.omdbapi.com/"



@patch('backend.api.omdb_client.requests.get')
@patch('backend.api.omdb_client.OMDB_API_KEY', 'test_key')
def test_get_movie_by_id_success(mock_requests_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"Response": "True", "Title": "Test Movie"}
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response

    movie = get_movie_by_id("tt12345")

    assert movie == {"Response": "True", "Title": "Test Movie"}
    mock_requests_get.assert_called_once_with(
        OMDB_BASE_URL,
        params={'apikey': 'test_key', 'i': "tt12345", 'plot': 'short'},
        timeout=10
    )
    mock_response.raise_for_status.assert_called_once()


@patch('backend.api.omdb_client.OMDB_API_KEY', None)
def test_get_movie_by_id_no_api_key(capsys):
    result = get_movie_by_id("tt12345")
    assert result is None
    captured = capsys.readouterr()
    assert "API ключ OMDb не настроен." in captured.err


@patch('backend.api.omdb_client.requests.get')
@patch('backend.api.omdb_client.OMDB_API_KEY', 'test_key')
def test_get_movie_by_id_api_response_false(mock_requests_get, capsys):
    mock_response = MagicMock()
    mock_response.json.return_value = {"Response": "False", "Error": "Movie not found!"}
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response

    movie = get_movie_by_id("tt12345")

    assert movie is None
    captured = capsys.readouterr()
    assert "OMDb API Error (i=tt12345): Movie not found!" in captured.err


@patch('backend.api.omdb_client.requests.get')
@patch('backend.api.omdb_client.OMDB_API_KEY', 'test_key')
def test_get_movie_by_id_api_response_false_generic_omdb_error(mock_requests_get, capsys):
    mock_response = MagicMock()
    mock_response.json.return_value = {"Response": "False", "Error": "Error getting data."}
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response

    movie = get_movie_by_id("tt12345")

    assert movie is None
    captured = capsys.readouterr()
    assert "OMDb API Error (i=tt12345): Error getting data." not in captured.err


@patch('backend.api.omdb_client.requests.get')
@patch('backend.api.omdb_client.OMDB_API_KEY', 'test_key')
def test_get_movie_by_id_timeout(mock_requests_get, capsys):
    mock_requests_get.side_effect = requests.exceptions.Timeout("Timeout error")
    movie = get_movie_by_id("tt12345")
    assert movie is None
    captured = capsys.readouterr()
    assert "Таймаут при получении деталей для tt12345" in captured.err


@patch('backend.api.omdb_client.requests.get')
@patch('backend.api.omdb_client.OMDB_API_KEY', 'test_key')
def test_get_movie_by_id_request_exception(mock_requests_get, capsys):
    mock_requests_get.side_effect = requests.exceptions.RequestException("Network error")
    movie = get_movie_by_id("tt12345")
    assert movie is None
    captured = capsys.readouterr()
    assert "Ошибка сети при получении деталей tt12345: Network error" in captured.err


@patch('backend.api.omdb_client.requests.get')
@patch('backend.api.omdb_client.OMDB_API_KEY', 'test_key')
def test_get_movie_by_id_unexpected_exception(mock_requests_get, capsys):
    mock_requests_get.side_effect = Exception("Unexpected error")
    movie = get_movie_by_id("tt12345")
    assert movie is None
    captured = capsys.readouterr()
    assert "Неожиданная ошибка при получении деталей tt12345: Unexpected error" in captured.err



@patch('backend.api.omdb_client.time.sleep')
@patch('backend.api.omdb_client.get_movie_by_id')
@patch('backend.api.omdb_client.requests.get')
@patch('backend.api.omdb_client.OMDB_API_KEY', 'test_key')
def test_search_movie_by_title_success_one_page(mock_requests_get, mock_internal_get_movie_by_id, mock_sleep):
    mock_search_response = MagicMock()
    mock_search_response.json.return_value = {
        "Response": "True",
        "Search": [{"Title": "Test Movie 1", "imdbID": "tt00001", "Poster": "poster1.jpg"}],
        "totalResults": "1"
    }
    mock_search_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_search_response

    mock_internal_get_movie_by_id.return_value = {
        "imdbID": "tt00001", "Title": "Test Movie 1", "imdbRating": "8.0",
        "Plot": "A great plot.", "Director": "Dir", "Actors": "Act", "Genre": "Gen", "Runtime": "120 min",
        "Poster": "detail_poster1.jpg"
    }

    results = search_movie_by_title("Test Movie")

    assert len(results) == 1
    assert results[0]['Title'] == "Test Movie 1"
    assert results[0]['imdbRating'] == "8.0"
    assert results[0]['imdbRatingValue'] == 8.0
    assert results[0]['Plot'] == "A great plot."
    assert results[0]['Poster'] == "detail_poster1.jpg"

    mock_requests_get.assert_called_once_with(
        OMDB_BASE_URL,
        params={'apikey': 'test_key', 's': "Test Movie", 'page': 1},
        timeout=15
    )
    mock_internal_get_movie_by_id.assert_called_once_with("tt00001")
    mock_sleep.assert_called_once()


@patch('backend.api.omdb_client.OMDB_API_KEY', None)
def test_search_movie_no_api_key(capsys):
    result = search_movie_by_title("Test")
    assert result is None
    captured = capsys.readouterr()
    assert "API ключ OMDb не настроен." in captured.err


def test_search_movie_empty_title():
    result = search_movie_by_title("")
    assert result == []


@patch('backend.api.omdb_client.requests.get')
@patch('backend.api.omdb_client.OMDB_API_KEY', 'test_key')
def test_search_movie_by_title_api_error_first_page(mock_requests_get, capsys):
    mock_requests_get.side_effect = requests.exceptions.RequestException("API Search Error")
    results = search_movie_by_title("Test Movie")
    assert results is None
    captured = capsys.readouterr()
    assert "Ошибка при поиске (страница 1): API Search Error" in captured.err


@patch('backend.api.omdb_client.requests.get')
@patch('backend.api.omdb_client.OMDB_API_KEY', 'test_key')
def test_search_movie_by_title_no_initial_results_api_false(mock_requests_get):
    mock_search_response = MagicMock()
    mock_search_response.json.return_value = {"Response": "False", "Error": "Movie not found."}
    mock_requests_get.return_value = mock_search_response
    results = search_movie_by_title("NonExistent")
    assert results == []


@patch('backend.api.omdb_client.time.sleep')
@patch('backend.api.omdb_client.get_movie_by_id')
@patch('backend.api.omdb_client.requests.get')
@patch('backend.api.omdb_client.OMDB_API_KEY', 'test_key')
def test_search_movie_by_title_with_year_and_type(mock_requests_get, mock_internal_get_movie_by_id, mock_sleep):
    mock_search_response = MagicMock()
    mock_search_response.json.return_value = {
        "Response": "True", "Search": [{"Title": "Test Movie", "imdbID": "tt00001"}], "totalResults": "1"
    }
    mock_requests_get.return_value = mock_search_response
    mock_internal_get_movie_by_id.return_value = {"imdbID": "tt00001", "imdbRating": "N/A"}

    search_movie_by_title("Test Movie", year=" 2020 ", type_filter="movie")

    mock_requests_get.assert_called_once_with(
        OMDB_BASE_URL,
        params={'apikey': 'test_key', 's': "Test Movie", 'page': 1, 'y': "2020", 'type': "movie"},
        timeout=15
    )


@patch('backend.api.omdb_client.time.sleep')
@patch('backend.api.omdb_client.get_movie_by_id')
@patch('backend.api.omdb_client.requests.get')
@patch('backend.api.omdb_client.OMDB_API_KEY', 'test_key')
def test_search_movie_by_title_rating_filter(mock_requests_get, mock_internal_get_movie_by_id, mock_sleep):
    mock_search_response = MagicMock()
    mock_search_response.json.return_value = {
        "Response": "True",
        "Search": [
            {"Title": "High Rating", "imdbID": "tt001"}, {"Title": "Mid Rating", "imdbID": "tt002"},
            {"Title": "Low Rating", "imdbID": "tt003"}, {"Title": "No Rating", "imdbID": "tt004"},
            {"Title": "Bad Rating Str", "imdbID": "tt005"}
        ], "totalResults": "5"
    }
    mock_requests_get.return_value = mock_search_response

    def get_movie_details_side_effect(imdb_id):
        if imdb_id == "tt001": return {"imdbID": "tt001", "imdbRating": "9.0"}
        if imdb_id == "tt002": return {"imdbID": "tt002", "imdbRating": "7.5"}
        if imdb_id == "tt003": return {"imdbID": "tt003", "imdbRating": "5.0"}
        if imdb_id == "tt004": return {"imdbID": "tt004", "imdbRating": "N/A"}
        if imdb_id == "tt005": return {"imdbID": "tt005", "imdbRating": "bad_str"}
        return None

    mock_internal_get_movie_by_id.side_effect = get_movie_details_side_effect

    results = search_movie_by_title("Test", min_rating=7.0, max_rating=9.5)

    assert len(results) == 2
    assert results[0]['imdbID'] == "tt001"
    assert results[1]['imdbID'] == "tt002"
    assert mock_internal_get_movie_by_id.call_count == 5
    assert mock_sleep.call_count == 2


@patch('backend.api.omdb_client.time.sleep')
@patch('backend.api.omdb_client.get_movie_by_id')
@patch('backend.api.omdb_client.requests.get')
@patch('backend.api.omdb_client.OMDB_API_KEY', 'test_key')
def test_search_movie_by_title_max_15_final_results(mock_requests_get, mock_internal_get_movie_by_id, mock_sleep):
    search_items = [{"Title": f"Movie {i}", "imdbID": f"tt{i:05}"} for i in range(1, 25)]  # 24 items

    mock_search_response_p1 = MagicMock()
    mock_search_response_p1.json.return_value = {"Response": "True", "Search": search_items[:10], "totalResults": "24"}
    mock_search_response_p2 = MagicMock()
    mock_search_response_p2.json.return_value = {"Response": "True", "Search": search_items[10:20],
                                                 "totalResults": "24"}
    mock_requests_get.side_effect = [mock_search_response_p1, mock_search_response_p2]

    mock_internal_get_movie_by_id.side_effect = lambda imdb_id: {"imdbID": imdb_id, "imdbRating": "7.5", "Plot": "Plot"}

    results = search_movie_by_title("Test")

    assert len(results) == 15
    assert mock_internal_get_movie_by_id.call_count == 15
    assert mock_sleep.call_count == 15
    mock_requests_get.assert_has_calls([
        call(OMDB_BASE_URL, params={'apikey': 'test_key', 's': 'Test', 'page': 1}, timeout=15),
        call(OMDB_BASE_URL, params={'apikey': 'test_key', 's': 'Test', 'page': 2}, timeout=15)
    ])


@patch('backend.api.omdb_client.time.sleep')
@patch('backend.api.omdb_client.get_movie_by_id')
@patch('backend.api.omdb_client.requests.get')
@patch('backend.api.omdb_client.OMDB_API_KEY', 'test_key')
def test_search_movie_internal_get_movie_by_id_returns_none(mock_requests_get, mock_internal_get_movie_by_id,
                                                            mock_sleep):
    mock_search_response = MagicMock()
    mock_search_response.json.return_value = {
        "Response": "True",
        "Search": [{"imdbID": "tt001"}, {"imdbID": "tt002"}], "totalResults": "2"
    }
    mock_requests_get.return_value = mock_search_response
    mock_internal_get_movie_by_id.side_effect = [
        {"imdbID": "tt001", "imdbRating": "8.0"}, None
    ]

    results = search_movie_by_title("Test")
    assert len(results) == 1
    assert results[0]['imdbID'] == "tt001"
    assert mock_internal_get_movie_by_id.call_count == 2
    assert mock_sleep.call_count == 1


@patch('backend.api.omdb_client.time.sleep')
@patch('backend.api.omdb_client.get_movie_by_id')
@patch('backend.api.omdb_client.requests.get')
@patch('backend.api.omdb_client.OMDB_API_KEY', 'test_key')
def test_search_movie_stops_paging_if_total_results_met(mock_requests_get, mock_internal_get_movie_by_id, mock_sleep):
    mock_search_response = MagicMock()
    mock_search_response.json.return_value = {
        "Response": "True", "Search": [{"imdbID": f"tt{i}"} for i in range(5)], "totalResults": "5"
    }
    mock_requests_get.return_value = mock_search_response
    mock_internal_get_movie_by_id.side_effect = lambda imdb_id: {"imdbID": imdb_id, "imdbRating": "7.0"}

    results = search_movie_by_title("Test")
    assert len(results) == 5
    mock_requests_get.assert_called_once()
    assert mock_internal_get_movie_by_id.call_count == 5
    assert mock_sleep.call_count == 5


@patch('backend.api.omdb_client.time.sleep')
@patch('backend.api.omdb_client.get_movie_by_id')
@patch('backend.api.omdb_client.requests.get')
@patch('backend.api.omdb_client.OMDB_API_KEY', 'test_key')
def test_search_movie_stops_paging_if_max_initial_results_met(mock_requests_get, mock_internal_get_movie_by_id,
                                                              mock_sleep):
    items_p1 = [{"imdbID": f"tt{i:02}"} for i in range(10)]
    items_p2 = [{"imdbID": f"tt{i:02}"} for i in range(10, 20)]

    mock_resp_p1 = MagicMock()
    mock_resp_p1.json.return_value = {"Response": "True", "Search": items_p1, "totalResults": "30"}
    mock_resp_p2 = MagicMock()
    mock_resp_p2.json.return_value = {"Response": "True", "Search": items_p2, "totalResults": "30"}
    mock_resp_p3 = MagicMock()
    mock_resp_p3.json.return_value = {"Response": "True", "Search": [], "totalResults": "30"}

    mock_requests_get.side_effect = [mock_resp_p1, mock_resp_p2, mock_resp_p3]
    mock_internal_get_movie_by_id.side_effect = lambda imdb_id: {"imdbID": imdb_id, "imdbRating": "7.0"}

    results = search_movie_by_title("Test")

    assert mock_requests_get.call_count == 2
    assert len(results) == 15
    assert mock_internal_get_movie_by_id.call_count == 15
    assert mock_sleep.call_count == 15


@patch('backend.api.omdb_client.time.sleep')
@patch('backend.api.omdb_client.get_movie_by_id')
@patch('backend.api.omdb_client.requests.get')
@patch('backend.api.omdb_client.OMDB_API_KEY', 'test_key')
def test_search_movie_api_error_on_second_page(mock_requests_get, mock_internal_get_movie_by_id, mock_sleep, capsys):
    items_p1 = [{"imdbID": f"tt{i:02}"} for i in range(5)]
    mock_resp_p1 = MagicMock()
    mock_resp_p1.json.return_value = {"Response": "True", "Search": items_p1, "totalResults": "25"}

    mock_requests_get.side_effect = [
        mock_resp_p1,
        requests.exceptions.RequestException("API Error page 2")
    ]
    mock_internal_get_movie_by_id.side_effect = lambda imdb_id: {"imdbID": imdb_id, "imdbRating": "7.0"}

    results = search_movie_by_title("Test")

    assert len(results) == 5
    assert mock_requests_get.call_count == 2
    assert mock_internal_get_movie_by_id.call_count == 5
    assert mock_sleep.call_count == 5
    captured = capsys.readouterr()
    assert "Ошибка при поиске (страница 2): API Error page 2" in captured.err
