import os
from dotenv import load_dotenv
import sys

load_dotenv()

OMDB_API_KEY = os.getenv("OMDB_API_KEY")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

if not OMDB_API_KEY:
    print("Ошибка: Ключ OMDb API не найден в .env")
    sys.exit(1)
if not DB_NAME or not DB_USER or not DB_PASSWORD:
    print("Ошибка: Данные для подключения к БД не найдены в .env")
    sys.exit(1)

DATABASE_CONFIG = {
    'dbname': DB_NAME,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'host': DB_HOST,
    'port': DB_PORT,
}
