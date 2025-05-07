from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout
from frontend.tabs.search_tab import SearchTab
from frontend.tabs.favorites_tab import FavoritesTab
from frontend.tabs.reviews_tab import MyReviewsTab


class MovieAppWindow(QMainWindow):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Movie Application")
        self.setGeometry(100, 100, 800, 600)  # x, y, width, height

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        self.search_tab = SearchTab(self.user_id)
        # self.favorites_tab = FavoritesTab(self.user_id)
        # self.my_reviews_tab = MyReviewsTab(self.user_id)

        self.tab_widget.addTab(self.search_tab, "Поиск фильмов")
        # self.tab_widget.addTab(self.favorites_tab, "Избранное")
        # self.tab_widget.addTab(self.my_reviews_tab, "Мои отзывы")

        # self.favorites_tab.favorite_removed_signal.connect(self.handle_favorite_removed)

    # def handle_favorite_removed(self, imdb_id: str):
    #     print(f"Favorite removed (imdb_id: {imdb_id}), MovieAppWindow notified.")

    def closeEvent(self, event):
        print("Закрытие основного приложения MovieApp...")
        super().closeEvent(event)