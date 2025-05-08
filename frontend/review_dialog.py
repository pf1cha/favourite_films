from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QComboBox, QTextEdit,
                             QDialogButtonBox, QFormLayout, QMessageBox)
from PyQt6.QtCore import pyqtSignal
from backend.database.review_service import add_review, get_review_by_user_and_movie


class ReviewDialog(QDialog):
    review_submitted = pyqtSignal()

    def __init__(self, user_id, imdb_id, movie_title, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.imdb_id = imdb_id
        self.movie_title_str = movie_title

        self.setWindowTitle(f"Отзыв на фильм: {self.movie_title_str}")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.title_label = QLabel(f"Фильм: {self.movie_title_str}")
        self.rating_combo = QComboBox()
        self.rating_combo.addItems([str(i) for i in range(1, 6)])  # 1-5 stars
        self.rating_combo.setCurrentText("5")

        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText("Ваш комментарий (необязательно)")

        form_layout.addRow("Рейтинг (1-5):", self.rating_combo)
        form_layout.addRow("Комментарий:", self.comment_edit)

        layout.addWidget(self.title_label)
        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.submit_review)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.load_existing_review()

    def load_existing_review(self):
        review = get_review_by_user_and_movie(self.user_id, self.imdb_id)
        if review:
            self.rating_combo.setCurrentText(str(review.rating))
            self.comment_edit.setText(review.comment or "")
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setText("Обновить отзыв")

    def submit_review(self):
        rating_str = self.rating_combo.currentText()
        if not rating_str:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите рейтинг.")
            return

        rating = int(rating_str)
        comment = self.comment_edit.toPlainText().strip()

        success, message = add_review(self.user_id, self.imdb_id, self.movie_title_str, rating, comment)

        if success:
            QMessageBox.information(self, "Успех", message)
            self.review_submitted.emit()
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", message)