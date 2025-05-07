import requests
from backend.config import settings
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
    Возвращает не более 15 результатов.
    """
    if not OMDB_API_KEY: print("API ключ OMDb не настроен.", file=sys.stderr); return None
    if not title: return []

    initial_results = []
    max_initial_results = 20
    total_results_api = 0

    for page in range(1, 3):
        if len(initial_results) >= max_initial_results and page > 1:
            break

        params = {'apikey': OMDB_API_KEY, 's': title, 'page': page}
        if year and year.strip().isdigit(): params['y'] = year.strip()
        if type_filter and type_filter in ['movie', 'series', 'episode']: params['type'] = type_filter

        print(f"OMDb initial search request (page {page}) params: {params}")
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
                print(
                    f"OMDb page {page} success. Found: {len(found_now)}. Total loaded: {len(initial_results)}. API total: {total_results_api}")
                if total_results_api <= page * 10:
                    break
            else:
                if page == 1 and data.get('Error') != 'Movie not found.':
                    print(f"OMDb API Error page 1: {data.get('Error')}", file=sys.stderr)
                elif page > 1:
                    print(f"OMDb API Error page {page}: {data.get('Error')}", file=sys.stderr)
                break

        except requests.exceptions.Timeout:
            print(f"Таймаут при поиске (страница {page})", file=sys.stderr)
            if page == 1:
                return None
            else:
                break
        except requests.exceptions.RequestException as e:
            print(f"Ошибка сети при поиске OMDb (страница {page}): {e}", file=sys.stderr)
            if page == 1:
                return None
            else:
                break
        except Exception as e_other:
            print(f"Неожиданная ошибка при поиске OMDb (страница {page}): {e_other}", file=sys.stderr)
            if page == 1:
                return None
            else:
                break

    if not initial_results:
        print("Первичный поиск не дал результатов.")
        return []

    final_filtered_results = []
    needs_rating_filter = not (min_rating <= 0.0 and max_rating >= 10.0)

    if not needs_rating_filter:
        print("Фильтрация по рейтингу не требуется (диапазон 0-10).")
        final_filtered_results = initial_results
    else:
        print(f"Фильтрация по рейтингу: Min={min_rating}, Max={max_rating}")
        count = 0
        for basic_result in initial_results:
            if len(final_filtered_results) >= 15:
                break

            imdb_id = basic_result.get('imdbID')
            if not imdb_id: continue

            count += 1
            print(f"({count}/{len(initial_results)}) Получение деталей для {imdb_id} ('{basic_result.get('Title')}')")
            detailed_data = get_movie_by_id(imdb_id)

            if detailed_data:
                rating_str = detailed_data.get('imdbRating', 'N/A')
                if rating_str != 'N/A':
                    try:
                        rating_float = float(rating_str)
                        if min_rating <= rating_float <= max_rating:
                            print(f"  -> Рейтинг {rating_float} в диапазоне [{min_rating}-{max_rating}]. Добавляем.")
                            final_filtered_results.append(basic_result)
                        else:
                            print(f"  -> Рейтинг {rating_float} вне диапазона.")
                    except ValueError:
                        print(f"  -> Не удалось преобразовать рейтинг '{rating_str}' в число.")
                else:
                    print("  -> Рейтинг 'N/A'.")
            else:
                print(f"  -> Не удалось получить детали для {imdb_id}.")
            time.sleep(0.05)

    return final_filtered_results[:15]
