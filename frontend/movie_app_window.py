from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                             QPushButton, QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from frontend.tabs.search_tab import SearchTab
from frontend.tabs.favorites_tab import FavoritesTab
from frontend.tabs.reviews_tab import MyReviewsTab


class MovieAppWindow(QMainWindow):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Основное окно")
        self.setMinimumSize(900, 650)

        self.bg_color = QColor(240, 240, 245)
        self.tab_active_color = QColor(80, 100, 220)
        self.tab_inactive_color = QColor(180, 180, 200)
        self.text_color = QColor(50, 50, 50)
        self.error_color = QColor(220, 53, 69)
        self.clear_button_color = QColor(255, 193, 7)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, self.bg_color)
        palette.setColor(QPalette.ColorRole.WindowText, self.text_color)
        self.setPalette(palette)

        self.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
            }}

            QTabBar::tab {{
                background: {self.tab_inactive_color.name()};
                color: white;
                padding: 12px 20px;
                border: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
                font-size: 14px;
                font-weight: 500;
            }}

            QTabBar::tab:selected {{
                background: {self.tab_active_color.name()};
            }}

            QTabBar::tab:hover {{
                background: {self.tab_active_color.lighter(110).name()};
            }}

            QLabel {{
                color: {self.text_color.name()};
                font-size: 14px;
            }}

            QPushButton {{
                background-color: {self.tab_active_color.name()};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
            }}

            QPushButton:hover {{
                background-color: {self.tab_active_color.darker(110).name()};
            }}

            QPushButton#logoutButton {{
                background-color: {self.error_color.name()};
            }}

            QPushButton#logoutButton:hover {{
                background-color: {self.error_color.darker(110).name()};
            }}

            QPushButton#clearButton {{
                background-color: {self.clear_button_color.name()};
                color: black;
            }}

            QPushButton#clearButton:hover {{
                background-color: {self.clear_button_color.darker(110).name()};
            }}

            QLineEdit {{
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }}

            QLineEdit:focus {{
                border: 2px solid {self.tab_active_color.name()};
            }}
        """)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        header = QHBoxLayout()
        header.addStretch()

        self.logout_button = QPushButton("Выйти")
        self.logout_button.setObjectName("logoutButton")
        self.logout_button.setCursor(Qt.CursorShape.PointingHandCursor)
        header.addWidget(self.logout_button, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.addLayout(header)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("QTabBar::tab { min-width: 120px; }")

        self.search_tab = SearchTab(self.user_id)
        self.favorites_tab = FavoritesTab(self.user_id)
        self.my_reviews_tab = MyReviewsTab(self.user_id)

        self.tab_widget.addTab(self.search_tab, "Поиск фильмов")
        self.tab_widget.addTab(self.favorites_tab, "Избранное")
        self.tab_widget.addTab(self.my_reviews_tab, "Мои отзывы")

        main_layout.addWidget(self.tab_widget)

        self.favorites_tab.favorite_removed_signal.connect(self.handle_favorite_removed)
        self.logout_button.clicked.connect(self.close)

    def handle_favorite_removed(self, imdb_id: str):
        print(f"Favorite removed (imdb_id: {imdb_id}), MovieAppWindow notified.")

    def closeEvent(self, event):
        print("Закрытие основного приложения MovieApp...")
        super().closeEvent(event)