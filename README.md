# FavouritesMovie (Десктопное приложение)

[![License](https://img.shields.io/badge/license-MIT-blue)](https://opensource.org/licenses/MIT) <!-- Замените, если другая лицензия -->

> Десктопное приложение на Python (PyQt6) для создания списка любимых фильмов и обмена отзывами.

## Описание

**FavouritesMovie** - это приложение для рабочего стола, позволяющее пользователям:

*   Создавать и управлять локальными аккаунтами.  *(Данные пользователей хранятся локально, не на сервере)*
*   Собирать коллекцию любимых фильмов, используя данные из внешнего API (OMDb API).
*   Писать отзывы о фильмах.

## Функциональность

### 1. Аккаунт (Локальный)

*   **Создание аккаунта:** Регистрация нового пользователя с указанием имени, пароля и, возможно, других данных (email - опционально, для восстановления пароля, если реализуете).  Все данные хранятся *локально*.
*   **Вход в аккаунт:** Аутентификация пользователя по имени и паролю.


### 2. Избранное

*   **Поиск фильмов:** Интеграция с внешним API (OMDb API) для поиска фильмов по названию, году и другим параметрам.  *Взаимодействие с API происходит через HTTP-запросы (библиотека `requests` в Python).*
*   **Добавление в избранное:** Сохранение выбранных фильмов в локальную базу данных.
*   **Просмотр избранного:** Отображение списка любимых фильмов с основной информацией (название, год и т.д.).  
*   **Удаление из избранного:** Возможность удалить фильм из списка.

### 3. Отзывы

*   **Написание отзывов:** Возможность оставить текстовый отзыв к любому фильму.  *Отзывы хранятся локально.*
*   **Просмотр отзывов:** Чтение отзывов, оставленных *текущим* пользователем (так как аккаунты локальные).
*   **(Опционально)** Оценка фильмов (например, звездочки).
*   **(Опционально)** Редактирование и удаление своих отзывов.

## Установка

**Требования:**

*   Python 3.7+
*   pip (менеджер пакетов Python)
*   Аккаунт и API-ключ на TMDb (или аналогичном сервисе)

**Шаги:**

1.  **Клонирование репозитория (или скачивание архива):**

    ```bash
    git clone https://github.com/<your-username>/kinoizbrannoe-desktop.git  # Замените на ваш репозиторий
    cd kinoizbrannoe-desktop
    ```

2.  **Создание виртуального окружения (рекомендуется):**

    ```bash
    python3 -m venv venv  # Создание виртуального окружения
    source venv/bin/activate  # Активация (Linux/macOS)
    # venv\Scripts\activate  # Активация (Windows)
    ```

3.  **Установка зависимостей:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Настройка:**
    *   Создайте файл `config.py` (или используйте другой способ хранения конфигурации).
    *   Добавьте в `config.py` ваш API-ключ TMDb (или другого сервиса) и, при необходимости, другие настройки (например, путь к файлу БД):

        ```python
        # config.py
        TMDB_API_KEY = "your_tmdb_api_key"
        DATABASE_PATH = "kinoizbrannoe.db"  # Путь к файлу SQLite (например)
        # ... другие настройки
        ```

5. **Запуск приложения:**

    ```bash
    python main.py
    ```
    (Где `main.py` - главный файл вашего приложения).
