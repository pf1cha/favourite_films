import requests
from backend.config.config import settings
import sys
import time

BASE_URL = "http://www.omdbapi.com/"
OMDB_API_KEY = settings.OMDB_API_KEY


def get_movie_by_id(imdb_id):
    if not OMDB_API_KEY: print("API ключ OMDb не настроен.", file=sys.stderr); return None
    params = {'apikey': OMDB_API_KEY, 'i': imdb_id, 'plot': 'short'}
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("Response") == "True":
            return data
        else:
            if data.get('Error') != 'Error getting data.':
                print(f"OMDb API Error (i={imdb_id}): {data.get('Error')}", file=sys.stderr)
            return None
    except requests.exceptions.Timeout:
        print(f"Таймаут при получении деталей для {imdb_id}", file=sys.stderr)
        return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка сети при получении деталей {imdb_id}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Неожиданная ошибка при получении деталей {imdb_id}: {e}", file=sys.stderr)
        return None


def search_movie_by_title(
        title: str,
        year: str | None = None,
        type_filter: str | None = None,
        min_rating: float = 0.0,
        max_rating: float = 10.0
) -> list[dict] | None:
    """
    Ищет фильмы/сериалы по названию, фильтрует по году/типу,
    затем фильтрует по диапазону рейтинга IMDb.
    Возвращает не более 15 результатов с рейтингом для каждого фильма.
    """
    if not OMDB_API_KEY:
        print("API ключ OMDb не настроен.", file=sys.stderr)
        return None
    if not title:
        return []

    initial_results = []
    max_initial_results = 20
    total_results_api = 0

    for page in range(1, 3):
        if len(initial_results) >= max_initial_results and page > 1:
            break

        params = {'apikey': OMDB_API_KEY, 's': title, 'page': page}
        if year and year.strip().isdigit():
            params['y'] = year.strip()
        if type_filter and type_filter in ['movie', 'series', 'episode']:
            params['type'] = type_filter

        try:
            response = requests.get(BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if data.get("Response") == "True":
                found_now = data.get("Search", [])
                initial_results.extend(found_now)
                if page == 1:
                    try:
                        total_results_api = int(data.get("totalResults", 0))
                    except ValueError:
                        total_results_api = 0
                if total_results_api <= page * 10:
                    break
        except Exception as e:
            print(f"Ошибка при поиске (страница {page}): {e}", file=sys.stderr)
            if page == 1:
                return None
            break

    if not initial_results:
        return []

    final_results = []
    needs_rating_filter = not (min_rating <= 0.0 and max_rating >= 10.0)

    for basic_result in initial_results:
        if len(final_results) >= 15:
            break

        imdb_id = basic_result.get('imdbID')
        if not imdb_id:
            continue

        detailed_data = get_movie_by_id(imdb_id)
        if not detailed_data:
            continue

        rating_str = detailed_data.get('imdbRating', 'N/A')
        rating = None
        if rating_str != 'N/A':
            try:
                rating = float(rating_str)
            except ValueError:
                rating = None

        if needs_rating_filter and (rating is None or not (min_rating <= rating <= max_rating)):
            continue

        full_result = {
            **basic_result,
            'imdbRating': rating_str,
            'imdbRatingValue': rating,
            'Plot': detailed_data.get('Plot'),
            'Director': detailed_data.get('Director'),
            'Actors': detailed_data.get('Actors'),
            'Genre': detailed_data.get('Genre'),
            'Runtime': detailed_data.get('Runtime'),
            'Poster': detailed_data.get('Poster')
        }

        final_results.append(full_result)
        time.sleep(0.05)

    return final_results[:15]

