from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QListWidget, QLabel, QListWidgetItem)
from PyQt6.QtCore import Qt
from backend.api.omdb_client import search_movie_by_title
from backend.database.database import add_favorite
from frontend.review_dialog import ReviewDialog
from frontend.ui_utils import show_error_message, show_info_message, show_warning_message
from backend.models.favourite_film import FavouriteFilm


class SearchTab(QWidget):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.current_search_results = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите название фильма/сериала...")
        self.search_button = QPushButton("Поиск")
        self.clear_button = QPushButton("Очистить")

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.clear_button)
        layout.addLayout(search_layout)

        self.results_list = QListWidget()
        layout.addWidget(QLabel("Результаты поиска:"))
        layout.addWidget(self.results_list)

        action_layout = QHBoxLayout()
        self.add_to_favorites_button = QPushButton("Добавить в избранное")
        self.leave_review_button = QPushButton("Оставить отзыв")

        action_layout.addWidget(self.add_to_favorites_button)
        action_layout.addWidget(self.leave_review_button)
        action_layout.addStretch()
        layout.addLayout(action_layout)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # Connections
        self.search_button.clicked.connect(self.perform_search)
        self.search_input.returnPressed.connect(self.perform_search)
        self.clear_button.clicked.connect(self.clear_search)
        self.add_to_favorites_button.clicked.connect(self.add_selected_to_favorites)
        self.leave_review_button.clicked.connect(self.leave_review_for_selected)
        self.results_list.itemSelectionChanged.connect(self.update_action_buttons_state)

        self.update_action_buttons_state()

    def perform_search(self):
        title = self.search_input.text().strip()
        if not title:
            show_warning_message(self, "Поиск", "Введите название для поиска.")
            return

        self.status_label.setText("Поиск...")
        self.results_list.clear()
        self.current_search_results = []

        movies = search_movie_by_title(title)
        if movies is None:
            self.status_label.setText("Ошибка API или сети. Проверьте консоль.")
            show_error_message(self, "Ошибка поиска",
                               "Не удалось выполнить поиск. Проверьте API ключ и сетевое соединение.")
        elif not movies:
            self.status_label.setText("Ничего не найдено.")
        else:
            self.current_search_results = movies
            for movie in movies:
                item_text = f"{movie.get('Title', 'N/A')} ({movie.get('Year', 'N/A')}) - {movie.get('Type', 'N/A')}"
                list_item = QListWidgetItem(item_text)
                list_item.setData(Qt.ItemDataRole.UserRole, movie)
                self.results_list.addItem(list_item)
            self.status_label.setText(f"Найдено: {len(movies)} результатов.")
        self.update_action_buttons_state()

    def clear_search(self):
        self.search_input.clear()
        self.results_list.clear()
        self.current_search_results = []
        self.status_label.setText("")
        self.update_action_buttons_state()

    def update_action_buttons_state(self):
        selected = bool(self.results_list.selectedItems())
        self.add_to_favorites_button.setEnabled(selected)
        self.leave_review_button.setEnabled(selected)

    def get_selected_movie_data(self):
        selected_items = self.results_list.selectedItems()
        if not selected_items:
            return None
        return selected_items[0].data(Qt.ItemDataRole.UserRole)

    def add_selected_to_favorites(self):
        movie_data = self.get_selected_movie_data()
        print(f"Selected movie data: {movie_data}")
        if not movie_data:
            show_warning_message(self, "Избранное", "Фильм не выбран.")
            return
        new_favorite_movie = FavouriteFilm(
            title=movie_data.get('Title'),
            year=movie_data.get('Year'),
            type_=movie_data.get('Type'),
            imdb_id=movie_data.get('imdbID'),
            poster_url=movie_data.get('Poster'),
            user_id=self.user_id
        )
        success, message = add_favorite(new_favorite_movie)
        print(f"Adding to favorites: {success}, {message}")
        if success:
            show_info_message(self, "Избранное", message)
        else:
            show_warning_message(self, "Избранное", message)

    def leave_review_for_selected(self):
        movie_data = self.get_selected_movie_data()
        if not movie_data:
            show_warning_message(self, "Отзыв", "Фильм не выбран.")
            return

        imdb_id = movie_data.get('imdbID')
        movie_title = movie_data.get('Title')

        if not imdb_id or not movie_title:
            show_error_message(self, "Отзыв", "Информация о фильме неполная (нет IMDb ID или названия).")
            return

        dialog = ReviewDialog(self.user_id, imdb_id, movie_title, self)
        dialog.exec()