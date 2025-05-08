from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QWidget, QTextEdit,
                             QDialogButtonBox, QFormLayout, QMessageBox, QFrame,
                             QHBoxLayout, QPushButton)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QPalette
from backend.database.review_service import add_review, get_review_by_user_and_movie


class ReviewDialog(QDialog):
    review_submitted = pyqtSignal()

    def __init__(self, user_id, imdb_id, movie_title, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.imdb_id = imdb_id
        self.movie_title_str = movie_title
        self.current_rating = 5


        self.bg_color = QColor(240, 240, 245)
        self.primary_color = QColor(80, 100, 220)
        self.error_color = QColor(220, 53, 69)
        self.text_color = QColor(50, 50, 50)
        self.border_color = QColor(200, 200, 200)
        self.star_active_color = QColor(255, 193, 7)
        self.star_inactive_color = QColor(200, 200, 200)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, self.bg_color)
        palette.setColor(QPalette.ColorRole.WindowText, self.text_color)
        self.setPalette(palette)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.bg_color.name()};
            }}

            QLabel {{
                color: {self.text_color.name()};
                font-size: 14px;
            }}

            QLabel#titleLabel {{
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 15px;
            }}

            QLabel#ratingLabel {{
                font-size: 15px;
                margin-right: 10px;
            }}

            QPushButton#starButton {{
                border: none;
                background: transparent;
                font-size: 24px;
                color: {self.star_inactive_color.name()};
                padding: 0 2px;
            }}

            QPushButton#starButton:hover {{
                color: {self.star_active_color.lighter(120).name()};
            }}

            QTextEdit {{
                border: 1px solid {self.border_color.name()};
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                min-height: 100px;
            }}

            QTextEdit:focus {{
                border: 2px solid {self.primary_color.name()};
            }}

            QDialogButtonBox QPushButton {{
                min-width: 80px;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 14px;
            }}

            QDialogButtonBox QPushButton:first-child {{
                background-color: {self.primary_color.name()};
                color: white;
            }}

            QDialogButtonBox QPushButton:first-child:hover {{
                background-color: {self.primary_color.darker(110).name()};
            }}

            QDialogButtonBox QPushButton:last-child {{
                background-color: {self.border_color.name()};
            }}

            QDialogButtonBox QPushButton:last-child:hover {{
                background-color: {self.border_color.darker(110).name()};
            }}
        """)

        self.setWindowTitle(f"Отзыв на: {self.movie_title_str}")
        self.setMinimumWidth(500)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.title_label = QLabel(self.movie_title_str)
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"color: {self.border_color.name()};")
        separator.setFixedHeight(1)

        form_layout = QFormLayout()
        form_layout.setContentsMargins(10, 0, 10, 10)
        form_layout.setVerticalSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        rating_widget = QWidget()
        rating_layout = QHBoxLayout(rating_widget)
        rating_layout.setContentsMargins(0, 0, 0, 0)

        rating_label = QLabel("Рейтинг:")
        rating_label.setObjectName("ratingLabel")
        rating_layout.addWidget(rating_label)

        self.star_buttons = []
        for i in range(1, 6):
            star_btn = QPushButton("★")
            star_btn.setObjectName("starButton")
            star_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            star_btn.clicked.connect(lambda _, r=i: self.set_rating(r))
            self.star_buttons.append(star_btn)
            rating_layout.addWidget(star_btn)

        rating_layout.addStretch()
        self.update_stars()

        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText("Напишите ваш отзыв о фильме...")
        self.comment_edit.setAcceptRichText(False)

        form_layout.addRow(rating_widget)
        form_layout.addRow("Комментарий:", self.comment_edit)

        self.button_box = QDialogButtonBox()
        self.ok_button = self.button_box.addButton("Сохранить", QDialogButtonBox.ButtonRole.AcceptRole)
        self.cancel_button = self.button_box.addButton("Назад", QDialogButtonBox.ButtonRole.RejectRole)
        self.button_box.setCenterButtons(True)

        main_layout.addWidget(self.title_label)
        main_layout.addWidget(separator)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.submit_review)
        self.button_box.rejected.connect(self.reject)

        self.load_existing_review()

    def set_rating(self, rating):
        """Устанавливает рейтинг и обновляет отображение звезд"""
        self.current_rating = rating
        self.update_stars()

    def update_stars(self):
        """Обновляет цвет звезд в соответствии с текущим рейтингом"""
        for i, star_btn in enumerate(self.star_buttons, 1):
            if i <= self.current_rating:
                star_btn.setStyleSheet(f"color: {self.star_active_color.name()};")
            else:
                star_btn.setStyleSheet(f"color: {self.star_inactive_color.name()};")

    def load_existing_review(self):
        review = get_review_by_user_and_movie(self.user_id, self.imdb_id)
        if review:
            self.current_rating = review.rating
            self.update_stars()
            self.comment_edit.setPlainText(review.comment or "")
            self.ok_button.setText("Обновить")

    def submit_review(self):
        comment = self.comment_edit.toPlainText().strip()

        success, message = add_review(
            self.user_id,
            self.imdb_id,
            self.movie_title_str,
            self.current_rating,
            comment
        )

        if success:
            QMessageBox.information(
                self,
                "Сохранено",
                "Ваш отзыв успешно сохранен!",
                buttons=QMessageBox.StandardButton.Ok,
                defaultButton=QMessageBox.StandardButton.Ok
            )
            self.review_submitted.emit()
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Ошибка",
                message,
                buttons=QMessageBox.StandardButton.Ok,
                defaultButton=QMessageBox.StandardButton.Ok
            )