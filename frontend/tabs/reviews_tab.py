from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QListWidget,
                             QLabel, QListWidgetItem, QHBoxLayout, QFrame)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor
from backend.database.review_service import get_reviews_by_user
from backend.models.review import Review
from frontend.review_dialog import ReviewDialog
from frontend.ui_utils import show_warning_message


class MyReviewsTab(QWidget):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id

        self.bg_color = QColor(240, 240, 245)
        self.primary_color = QColor(80, 100, 220)
        self.text_color = QColor(50, 50, 50)
        self.card_bg_color = QColor(255, 255, 255)
        self.border_color = QColor(200, 200, 200)

        self.init_ui()
        self.load_my_reviews()

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
                min-width: 100px;
            }}

            QPushButton:hover {{
                background-color: {self.primary_color.darker(110).name()};
            }}

            QPushButton:disabled {{
                background-color: {self.border_color.name()};
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
        title_label = QLabel("Ваши отзывы")
        title_label.setObjectName("titleLabel")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_button.clicked.connect(self.load_my_reviews)
        title_layout.addWidget(self.refresh_button)
        layout.addLayout(title_layout)

        self.reviews_list = QListWidget()
        self.reviews_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.reviews_list.setSpacing(5)
        layout.addWidget(self.reviews_list)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.edit_review_button = QPushButton("Редактировать отзыв")
        self.edit_review_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_review_button.clicked.connect(self.edit_selected_review)
        button_layout.addWidget(self.edit_review_button)

        layout.addLayout(button_layout)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.reviews_list.itemSelectionChanged.connect(self.update_action_buttons_state)
        self.reviews_list.itemDoubleClicked.connect(self.edit_selected_review_on_double_click)

        self.update_action_buttons_state()

    def load_my_reviews(self):
        self.reviews_list.clear()
        self.status_label.setText("Загрузка ваших отзывов...")

        reviews = get_reviews_by_user(self.user_id)

        if not reviews:
            self.status_label.setText("Вы еще не оставили ни одного отзыва.")
            return

        for review in reviews:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, review)
            item.setSizeHint(QSize(0, 100))

            widget = QWidget()
            widget_layout = QVBoxLayout(widget)
            widget_layout.setContentsMargins(10, 5, 10, 5)
            widget_layout.setSpacing(5)


            title_layout = QHBoxLayout()

            title_label = QLabel(review.movie_title)
            title_font = QFont()
            title_font.setBold(True)
            title_font.setPointSize(14)
            title_label.setFont(title_font)
            title_layout.addWidget(title_label)

            rating_label = QLabel(f"★ {review.rating}/5")
            rating_label.setStyleSheet(f"color: {self.primary_color.name()}; font-weight: bold;")
            title_layout.addStretch()
            title_layout.addWidget(rating_label)

            widget_layout.addLayout(title_layout)

            if review.comment:
                comment_label = QLabel(review.comment)
                comment_label.setWordWrap(True)
                comment_label.setStyleSheet("color: #555;")
                widget_layout.addWidget(comment_label)
            else:
                no_comment_label = QLabel("Без комментария")
                no_comment_label.setStyleSheet("color: #999; font-style: italic;")
                widget_layout.addWidget(no_comment_label)

            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setStyleSheet(f"color: {self.border_color.name()};")
            widget_layout.addWidget(separator)

            self.reviews_list.addItem(item)
            self.reviews_list.setItemWidget(item, widget)

        self.status_label.setText(f"Найдено отзывов: {len(reviews)}")
        self.update_action_buttons_state()

    def update_action_buttons_state(self):
        selected = bool(self.reviews_list.selectedItems())
        self.edit_review_button.setEnabled(selected)

    def get_selected_review(self) -> Review | None:
        selected_items = self.reviews_list.selectedItems()
        if not selected_items:
            return None
        return selected_items[0].data(Qt.ItemDataRole.UserRole)

    def edit_selected_review_on_double_click(self, item: QListWidgetItem):
        self.edit_selected_review()

    def edit_selected_review(self):
        selected_review = self.get_selected_review()
        if not selected_review:
            show_warning_message(self, "Редактирование", "Отзыв не выбран.")
            return

        dialog = ReviewDialog(self.user_id, selected_review.imdb_id, selected_review.movie_title, self)
        dialog.review_submitted.connect(self.load_my_reviews)
        dialog.exec()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_my_reviews()