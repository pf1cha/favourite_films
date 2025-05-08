
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QListWidget,
                             QLabel, QMessageBox, QListWidgetItem, QHBoxLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from backend.database.database import get_all_favorites_by_user_id, remove_favorite
from backend.models.favourite_film import FavouriteFilm  # For type hinting
from frontend.review_dialog import ReviewDialog
from frontend.ui_utils import show_error_message, show_info_message, show_warning_message


class FavoritesTab(QWidget):
    favorite_removed_signal = pyqtSignal(str)

    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.init_ui()
        self.load_favorites()

    def init_ui(self):
        layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Ваши избранные фильмы:"))
        top_layout.addStretch()
        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.load_favorites)
        top_layout.addWidget(self.refresh_button)
        layout.addLayout(top_layout)

        self.favorites_list = QListWidget()
        layout.addWidget(self.favorites_list)

        action_layout = QHBoxLayout()
        self.remove_favorite_button = QPushButton("Удалить из избранного")
        self.leave_review_button = QPushButton("Оставить/Изменить отзыв")
        action_layout.addWidget(self.remove_favorite_button)
        action_layout.addWidget(self.leave_review_button)
        action_layout.addStretch()
        layout.addLayout(action_layout)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.remove_favorite_button.clicked.connect(self.remove_selected_favorite)
        self.leave_review_button.clicked.connect(self.leave_review_for_selected_favorite)
        self.favorites_list.itemSelectionChanged.connect(self.update_action_buttons_state)

        self.update_action_buttons_state()

    def load_favorites(self):
        self.favorites_list.clear()
        self.status_label.setText("Загрузка избранного...")
        favorites = get_all_favorites_by_user_id(self.user_id)

        if not favorites:
            self.status_label.setText("Список избранного пуст.")
        else:
            for fav_film in favorites:
                item_text = f"{fav_film.title} ({fav_film.year or 'N/A'}) - {fav_film.type_ or 'N/A'}"
                list_item = QListWidgetItem(item_text)
                list_item.setData(Qt.ItemDataRole.UserRole, fav_film)
                self.favorites_list.addItem(list_item)
            self.status_label.setText(f"Загружено: {len(favorites)} фильмов.")
        self.update_action_buttons_state()

    def update_action_buttons_state(self):
        selected = bool(self.favorites_list.selectedItems())
        self.remove_favorite_button.setEnabled(selected)
        self.leave_review_button.setEnabled(selected)

    def get_selected_favorite_film(self) -> FavouriteFilm | None:
        selected_items = self.favorites_list.selectedItems()
        if not selected_items:
            return None
        return selected_items[0].data(Qt.ItemDataRole.UserRole)

    def remove_selected_favorite(self):
        selected_film = self.get_selected_favorite_film()
        if not selected_film:
            show_warning_message(self, "Удаление", "Фильм не выбран.")
            return

        confirm = QMessageBox.question(self, "Подтверждение",
                                       f"Удалить '{selected_film.title}' из избранного?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            success = remove_favorite(self.user_id, selected_film.imdb_id)
            if success:
                show_info_message(self, "Удаление", f"'{selected_film.title}' удален из избранного.")
                self.favorite_removed_signal.emit(selected_film.imdb_id)
                self.load_favorites()
            else:
                show_error_message(self, "Ошибка удаления", "Не удалось удалить фильм из избранного.")

    def leave_review_for_selected_favorite(self):
        selected_film = self.get_selected_favorite_film()
        if not selected_film:
            show_warning_message(self, "Отзыв", "Фильм не выбран.")
            return
        dialog = ReviewDialog(self.user_id, selected_film.imdb_id, selected_film.title, self)
        # dialog.review_submitted.connect(self.handle_review_submission)
        dialog.exec()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_favorites()