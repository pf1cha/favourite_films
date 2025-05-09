from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QListWidget, QLabel, QListWidgetItem,
                             QFrame)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QImage, QPixmap
import requests
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

        self.bg_color = QColor(240, 240, 245)
        self.primary_color = QColor(80, 100, 220)
        self.secondary_color = QColor(108, 117, 125)
        self.error_color = QColor(220, 53, 69)
        self.text_color = QColor(50, 50, 50)
        self.card_bg_color = QColor(255, 255, 255)
        self.border_color = QColor(200, 200, 200)

        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.bg_color.name()};
                color: {self.text_color.name()};
            }}

            QLabel {{
                font-size: 14px;
            }}

            QLabel#titleLabel {{
                font-size: 18px;
                font-weight: 600;
            }}

            QLineEdit {{
                border: 1px solid {self.border_color.name()};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }}

            QLineEdit:focus {{
                border: 2px solid {self.primary_color.name()};
            }}

            QPushButton {{
                background-color: {self.primary_color.name()};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 100px;
            }}

            QPushButton:hover {{
                background-color: {self.primary_color.darker(110).name()};
            }}

            QPushButton:disabled {{
                background-color: {self.border_color.name()};
            }}

            QPushButton#clearButton {{
                background-color: {self.secondary_color.name()};
            }}

            QPushButton#clearButton:hover {{
                background-color: {self.secondary_color.darker(110).name()};
            }}

            QListWidget {{
                background-color: {self.card_bg_color.name()};
                border: 1px solid {self.border_color.name()};
                border-radius: 8px;
                padding: 5px;
            }}

            QListWidget::item {{
                border-bottom: 1px solid {self.border_color.name()};
                padding: 12px 8px;
            }}

            QListWidget::item:selected {{
                background-color: {self.primary_color.lighter(130).name()};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите название фильма или сериала...")
        self.search_input.setClearButtonEnabled(True)
        search_layout.addWidget(self.search_input)

        self.search_button = QPushButton("Поиск")
        self.search_button.setCursor(Qt.CursorShape.PointingHandCursor)
        search_layout.addWidget(self.search_button)

        self.clear_button = QPushButton("Очистить")
        self.clear_button.setObjectName("clearButton")
        self.clear_button.setCursor(Qt.CursorShape.PointingHandCursor)
        search_layout.addWidget(self.clear_button)

        layout.addLayout(search_layout)

        results_label = QLabel("Результаты поиска:")
        results_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(results_label)

        self.results_list = QListWidget()
        self.results_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.results_list.setSpacing(5)
        layout.addWidget(self.results_list)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.add_to_favorites_button = QPushButton("Добавить в избранное")
        self.add_to_favorites_button.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.add_to_favorites_button)

        self.leave_review_button = QPushButton("Оставить отзыв")
        self.leave_review_button.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.leave_review_button)

        layout.addLayout(button_layout)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

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

        self.status_label.setText("Выполняется поиск...")
        self.results_list.clear()
        self.current_search_results = []

        movies = search_movie_by_title(title)
        if movies is None:
            self.status_label.setText("Ошибка соединения с API")
            show_error_message(self, "Ошибка поиска",
                               "Не удалось выполнить поиск. Проверьте подключение к интернету.")
        elif not movies:
            self.status_label.setText("Ничего не найдено.")
        else:
            self.current_search_results = movies
            for movie in movies:
                item = QListWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole, movie)
                item.setSizeHint(QSize(0, 180))

                widget = QWidget()
                widget_layout = QHBoxLayout(widget)
                widget_layout.setContentsMargins(10, 5, 10, 5)
                widget_layout.setSpacing(10)

                poster_url = movie.get('Poster')
                if poster_url and poster_url != 'N/A':
                    try:
                        response = requests.get(poster_url, timeout=10)
                        if response.status_code == 200:
                            image = QImage()
                            image.loadFromData(response.content)

                            scaled_image = image.scaled(120, 160,
                                                        Qt.AspectRatioMode.KeepAspectRatio,
                                                        Qt.TransformationMode.SmoothTransformation)

                            poster_label = QLabel()
                            poster_label.setPixmap(QPixmap.fromImage(scaled_image))
                            poster_label.setFixedSize(120, 160)
                            poster_label.setStyleSheet("border: 1px solid #ddd;")
                            widget_layout.addWidget(poster_label)
                    except Exception as e:
                        print(f"Ошибка загрузки постера: {e}")

                info_widget = QWidget()
                info_layout = QVBoxLayout(info_widget)
                info_layout.setContentsMargins(0, 0, 0, 0)
                info_layout.setSpacing(5)

                title_layout = QHBoxLayout()

                title_label = QLabel(movie.get('Title', 'Нет названия'))
                title_font = QFont()
                title_font.setBold(True)
                title_font.setPointSize(14)
                title_label.setFont(title_font)
                title_layout.addWidget(title_label)

                if movie.get('Year'):
                    year_label = QLabel(f"({movie.get('Year')})")
                    year_label.setStyleSheet("color: #666;")
                    title_layout.addWidget(year_label)

                title_layout.addStretch()

                if movie.get('Type'):
                    type_label = QLabel(movie.get('Type'))
                    type_label.setStyleSheet("""
                        color: white;
                        background-color: #6c757d;
                        border-radius: 4px;
                        padding: 2px 6px;
                    """)
                    title_layout.addWidget(type_label)

                info_layout.addLayout(title_layout)

                if movie.get('imdbID'):
                    imdb_layout = QHBoxLayout()
                    imdb_label = QLabel(f"IMDb: {movie.get('imdbID')}")
                    imdb_label.setStyleSheet("color: #555;")
                    imdb_layout.addWidget(imdb_label)
                    imdb_layout.addStretch()
                    info_layout.addLayout(imdb_layout)

                if movie.get('imdbRating') and movie.get('imdbRating') != 'N/A':
                    rating_layout = QHBoxLayout()
                    rating_label = QLabel(f"Рейтинг: {movie.get('imdbRating')}")
                    rating_label.setStyleSheet("color: #ffc107; font-weight: bold;")
                    rating_layout.addWidget(rating_label)
                    rating_layout.addStretch()
                    info_layout.addLayout(rating_layout)

                separator = QFrame()
                separator.setFrameShape(QFrame.Shape.HLine)
                separator.setStyleSheet(f"color: {self.border_color.name()};")
                info_layout.addWidget(separator)

                widget_layout.addWidget(info_widget)
                widget_layout.setStretchFactor(info_widget, 1)

                self.results_list.addItem(item)
                self.results_list.setItemWidget(item, widget)

            self.status_label.setText(f"Найдено результатов: {len(movies)}")

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
        if success:
            show_info_message(self, "Избранное", f"Фильм '{movie_data.get('Title')}' добавлен в избранное!")
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
            show_error_message(self, "Отзыв", "Недостаточно информации о фильме (отсутствует IMDb ID или название).")
            return

        dialog = ReviewDialog(self.user_id, imdb_id, movie_title, self)
        dialog.exec()