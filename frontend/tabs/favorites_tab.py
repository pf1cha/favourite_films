from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QListWidget,
                             QLabel, QMessageBox, QListWidgetItem, QHBoxLayout,
                             QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor
from backend.database.database import get_all_favorites_by_user_id, remove_favorite
from backend.models.favourite_film import FavouriteFilm
from frontend.review_dialog import ReviewDialog
from frontend.ui_utils import show_error_message, show_info_message, show_warning_message


class FavoritesTab(QWidget):
    favorite_removed_signal = pyqtSignal(str)

    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id

        self.bg_color = QColor(240, 240, 245)
        self.primary_color = QColor(80, 100, 220)
        self.error_color = QColor(220, 53, 69)
        self.text_color = QColor(50, 50, 50)
        self.card_bg_color = QColor(255, 255, 255)
        self.border_color = QColor(200, 200, 200)

        self.init_ui()
        self.load_favorites()

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

            QPushButton {{
                background-color: {self.primary_color.name()};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 120px;
            }}

            QPushButton:hover {{
                background-color: {self.primary_color.darker(110).name()};
            }}

            QPushButton:disabled {{
                background-color: {self.border_color.name()};
            }}

            QPushButton#removeButton {{
                background-color: {self.error_color.name()};
            }}

            QPushButton#removeButton:hover {{
                background-color: {self.error_color.darker(110).name()};
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

        title_layout = QHBoxLayout()
        title_label = QLabel("Избранные фильмы")
        title_label.setObjectName("titleLabel")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_button.clicked.connect(self.load_favorites)
        title_layout.addWidget(self.refresh_button)
        layout.addLayout(title_layout)

        self.favorites_list = QListWidget()
        self.favorites_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.favorites_list.setSpacing(5)
        layout.addWidget(self.favorites_list)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.remove_favorite_button = QPushButton("Удалить из избранного")
        self.remove_favorite_button.setObjectName("removeButton")
        self.remove_favorite_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.remove_favorite_button.clicked.connect(self.remove_selected_favorite)
        button_layout.addWidget(self.remove_favorite_button)

        self.leave_review_button = QPushButton("Оставить отзыв")
        self.leave_review_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.leave_review_button.clicked.connect(self.leave_review_for_selected_favorite)
        button_layout.addWidget(self.leave_review_button)

        layout.addLayout(button_layout)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.favorites_list.itemSelectionChanged.connect(self.update_action_buttons_state)
        self.update_action_buttons_state()

    def load_favorites(self):
        self.favorites_list.clear()
        self.status_label.setText("Загрузка избранных фильмов...")

        favorites = get_all_favorites_by_user_id(self.user_id)

        if not favorites:
            self.status_label.setText("Ваш список избранного пока пуст.")
            return

        for fav_film in favorites:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, fav_film)
            item.setSizeHint(QSize(0, 100))

            widget = QWidget()
            widget_layout = QVBoxLayout(widget)
            widget_layout.setContentsMargins(10, 5, 10, 5)
            widget_layout.setSpacing(5)

            title_layout = QHBoxLayout()

            title_label = QLabel(fav_film.title)
            title_font = QFont()
            title_font.setBold(True)
            title_font.setPointSize(14)
            title_label.setFont(title_font)
            title_layout.addWidget(title_label)

            if fav_film.year:
                year_label = QLabel(f"({fav_film.year})")
                year_label.setStyleSheet("color: #666;")
                title_layout.addWidget(year_label)

            title_layout.addStretch()

            if fav_film.type_:
                type_label = QLabel(fav_film.type_)
                type_label.setStyleSheet("""
                    color: white;
                    background-color: #6c757d;
                    border-radius: 4px;
                    padding: 2px 6px;
                """)
                title_layout.addWidget(type_label)

            widget_layout.addLayout(title_layout)


            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setStyleSheet(f"color: {self.border_color.name()};")
            widget_layout.addWidget(separator)

            self.favorites_list.addItem(item)
            self.favorites_list.setItemWidget(item, widget)

        self.status_label.setText(f"Найдено фильмов: {len(favorites)}")
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

        confirm = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить '{selected_film.title}' из избранного?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            success = remove_favorite(self.user_id, selected_film.imdb_id)
            if success:
                for i in range(self.favorites_list.count()):
                    item = self.favorites_list.item(i)
                    if item.data(Qt.ItemDataRole.UserRole).imdb_id == selected_film.imdb_id:
                        self.favorites_list.takeItem(i)
                        break

                show_info_message(self, "Успешно", f"Фильм '{selected_film.title}' удален из избранного.")
                self.favorite_removed_signal.emit(selected_film.imdb_id)
                self.update_action_buttons_state()
            else:
                show_error_message(self, "Ошибка", "Не удалось удалить фильм из избранного.")

    def leave_review_for_selected_favorite(self):
        selected_film = self.get_selected_favorite_film()
        if not selected_film:
            show_warning_message(self, "Отзыв", "Фильм не выбран.")
            return

        dialog = ReviewDialog(self.user_id, selected_film.imdb_id, selected_film.title, self)
        dialog.review_submitted.connect(self.load_favorites)
        dialog.exec()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_favorites()