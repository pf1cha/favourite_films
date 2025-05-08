from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QListWidget,
                             QLabel, QListWidgetItem, QHBoxLayout)
from PyQt6.QtCore import Qt
from backend.database.review_service import get_reviews_by_user
from backend.models.review import Review  # For type hinting
from frontend.review_dialog import ReviewDialog  # To potentially edit a review
from frontend.ui_utils import show_warning_message


class MyReviewsTab(QWidget):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.init_ui()
        self.load_my_reviews()

    def init_ui(self):
        layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Ваши отзывы:"))
        top_layout.addStretch()
        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.load_my_reviews)
        top_layout.addWidget(self.refresh_button)
        layout.addLayout(top_layout)

        self.reviews_list = QListWidget()
        layout.addWidget(self.reviews_list)

        action_layout = QHBoxLayout()
        self.edit_review_button = QPushButton("Редактировать отзыв")
        # self.delete_review_button = QPushButton("Удалить отзыв")
        action_layout.addWidget(self.edit_review_button)
        # action_layout.addWidget(self.delete_review_button)
        action_layout.addStretch()
        layout.addLayout(action_layout)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.edit_review_button.clicked.connect(self.edit_selected_review)
        self.reviews_list.itemSelectionChanged.connect(self.update_action_buttons_state)
        self.reviews_list.itemDoubleClicked.connect(self.edit_selected_review_on_double_click)

        self.update_action_buttons_state()

    def load_my_reviews(self):
        self.reviews_list.clear()
        self.status_label.setText("Загрузка ваших отзывов...")
        reviews = get_reviews_by_user(self.user_id)

        if not reviews:
            self.status_label.setText("Вы еще не оставили ни одного отзыва.")
        else:
            for review in reviews:
                comment_preview = (review.comment[:50] + '...') if review.comment and len(review.comment) > 50 else (
                            review.comment or "Без комментария")
                item_text = f"'{review.movie_title}' - Рейтинг: {review.rating}/5\nКомментарий: {comment_preview}"
                list_item = QListWidgetItem(item_text)
                list_item.setData(Qt.ItemDataRole.UserRole, review)
                self.reviews_list.addItem(list_item)
            self.status_label.setText(f"Загружено: {len(reviews)} отзывов.")
        self.update_action_buttons_state()

    def update_action_buttons_state(self):
        selected = bool(self.reviews_list.selectedItems())
        self.edit_review_button.setEnabled(selected)
        # self.delete_review_button.setEnabled(selected)

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