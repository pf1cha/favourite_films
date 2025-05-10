import pytest
import requests_mock  # Импортируем библиотеку
from backend.api.omdb_client import get_movie_by_id, search_movie_by_title, BASE_URL
from backend.config.config import settings  # Для OMDB_API_KEY


# Убедимся, что API ключ установлен для этих тестов,
# даже если он None в реальных настройках, т.к. мы мокаем запросы
@pytest.fixture(autouse=True)
def _ensure_omdb_key(monkeypatch):
    if not settings.OMDB_API_KEY:
        monkeypatch.setattr(settings, 'OMDB_API_KEY', 'test_integration_key')
    # Также нужно подменить ключ в самом модуле, если он читается при импорте
    monkeypatch.setattr('backend.api.omdb_client.OMDB_API_KEY', settings.OMDB_API_KEY or 'test_integration_key')


@pytest.mark.integration
def test_get_movie_by_id_integration(requests_mock):
    imdb_id = "tt0372784"  # Batman Begins
    expected_api_url = f"{BASE_URL}?apikey={settings.OMDB_API_KEY or 'test_integration_key'}&i={imdb_id}&plot=short"
    mock_response_data = {
        "Title": "Batman Begins",
        "Year": "2005",
        "imdbID": imdb_id,
        "Response": "True"
    }
    requests_mock.get(expected_api_url, json=mock_response_data, status_code=200)

    movie_data = get_movie_by_id(imdb_id)

    assert movie_data is not None
    assert movie_data["Title"] == "Batman Begins"
    assert movie_data["imdbID"] == imdb_id
    assert requests_mock.called_once  # Убедимся, что запрос был сделан
    assert requests_mock.last_request.url == expected_api_url


@pytest.mark.integration
def test_search_movie_by_title_integration(requests_mock):
    title_search = "Batman"
    # Ожидаемый URL для первой страницы поиска
    expected_search_url_page1 = f"{BASE_URL}?apikey={settings.OMDB_API_KEY or 'test_integration_key'}&s={title_search}&page=1"
    mock_search_response_page1 = {
        "Search": [
            {"Title": "Batman Begins", "Year": "2005", "imdbID": "tt0372784", "Type": "movie"},
            {"Title": "Batman v Superman", "Year": "2016", "imdbID": "tt2975590", "Type": "movie"}
        ],
        "totalResults": "2",
        "Response": "True"
    }
    requests_mock.get(expected_search_url_page1, json=mock_search_response_page1, status_code=200)

    # Мокаем ответы для get_movie_by_id, которые будут вызваны внутри search_movie_by_title
    mock_details_tt0372784 = {"Title": "Batman Begins", "imdbRating": "8.2", "imdbID": "tt0372784", "Response": "True",
                              "Plot": "Short plot 1"}
    mock_details_tt2975590 = {"Title": "Batman v Superman", "imdbRating": "6.4", "imdbID": "tt2975590",
                              "Response": "True", "Plot": "Short plot 2"}

    requests_mock.get(f"{BASE_URL}?apikey={settings.OMDB_API_KEY or 'test_integration_key'}&i=tt0372784&plot=short",
                      json=mock_details_tt0372784)
    requests_mock.get(f"{BASE_URL}?apikey={settings.OMDB_API_KEY or 'test_integration_key'}&i=tt2975590&plot=short",
                      json=mock_details_tt2975590)

    results = search_movie_by_title(title_search)

    assert results is not None
    assert len(results) == 2
    assert results[0]["Title"] == "Batman Begins"
    assert results[0]["imdbRating"] == "8.2"
    assert results[1]["Title"] == "Batman v Superman"
    assert results[1]["imdbRating"] == "6.4"

    # Проверим, что было 3 вызова: 1 на поиск, 2 на детали
    assert requests_mock.call_count == 3
