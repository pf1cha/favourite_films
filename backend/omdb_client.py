import requests
from backend.config import OMDB_API_KEY
import sys

BASE_URL = "http://www.omdbapi.com/"

def search_movie_by_title(title):
    """Ищет фильмы/сериалы по названию."""
    if not OMDB_API_KEY:
        print("API ключ OMDb не настроен.", file=sys.stderr)
        return None

    params = {
        'apikey': OMDB_API_KEY,
        's': title,        # 's' для поиска по названию (возвращает список)
        'type': ''         # Искать всё (movie, series, episode)
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("Response") == "True":
            return data.get("Search", [])
        else:
            print(f"OMDb API Error: {data.get('Error')}", file=sys.stderr)
            return []

    except requests.exceptions.RequestException as e:
        print(f"Ошибка сети при обращении к OMDb API: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Неожиданная ошибка при поиске в OMDb: {e}", file=sys.stderr)
        return None

def get_movie_by_id(imdb_id):
    """Получает детальную информацию по IMDb ID."""
    if not OMDB_API_KEY:
        print("API ключ OMDb не настроен.", file=sys.stderr)
        return None

    params = {
        'apikey': OMDB_API_KEY,
        'i': imdb_id,     # 'i' для поиска по ID
        'plot': 'short'   # Можно 'full' для полного описания
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("Response") == "True":
            print(data)
            return data # Возвращает словарь с деталями
        else:
            print(f"OMDb API Error: {data.get('Error')}", file=sys.stderr)
            return None

    except requests.exceptions.RequestException as e:
        print(f"Ошибка сети при обращении к OMDb API: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Неожиданная ошибка при получении деталей из OMDb: {e}", file=sys.stderr)
        return None
