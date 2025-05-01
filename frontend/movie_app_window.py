from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QListWidget, QLabel, QMessageBox, QListWidgetItem
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal
import requests
from backend import database, omdb_client
# from backend.database import get_all_favorites


# --- Потоки для фоновых задач ---
class SearchThread(QThread):
    """Поток для выполнения поиска в OMDb API."""
    results_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, search_term):
        super().__init__()
        self.search_term = search_term

    def run(self):
        results = omdb_client.search_movie_by_title(self.search_term)
        if results is not None:
            self.results_ready.emit(results)
        else:
            self.error_occurred.emit("Ошибка при поиске. Проверьте консоль или соединение.")


class ImageLoaderThread(QThread):
    """Поток для загрузки изображения."""
    image_ready = pyqtSignal(str, QPixmap)  # imdb_id, pixmap

    def __init__(self, imdb_id, url):
        super().__init__()
        self.imdb_id = imdb_id
        self.url = url

    def run(self):
        if self.url and self.url != 'N/A':
            try:
                response = requests.get(self.url, stream=True)
                response.raise_for_status()
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                self.image_ready.emit(self.imdb_id, pixmap)
            except requests.exceptions.RequestException as e:
                print(f"Не удалось загрузить постер {self.imdb_id}: {e}")
            except Exception as e:
                print(f"Ошибка обработки постера {self.imdb_id}: {e}")


# --- Основное окно приложения ---
class MovieApp(QWidget):
    def __init__(self):
        super().__init__()
        self.search_results = []  # Храним результаты поиска
        self.image_loaders = {}  # Храним активные загрузчики изображений
        self.init_ui()
        self.load_favorites()  # Загружаем избранное при старте

    def init_ui(self):
        self.setWindowTitle('Мои Любимые Фильмы и Сериалы')
        self.setGeometry(100, 100, 800, 600)  # Позиция и размер окна

        # --- Макеты ---
        main_layout = QVBoxLayout()
        search_layout = QHBoxLayout()
        lists_layout = QHBoxLayout()

        # --- Поиск ---
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите название фильма или сериала...")
        self.search_button = QPushButton("Найти")
        self.search_button.clicked.connect(self.perform_search)
        self.search_input.returnPressed.connect(self.perform_search)  # Поиск по Enter

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)

        # --- Список результатов поиска ---
        results_group_layout = QVBoxLayout()
        results_label = QLabel("Результаты поиска:")
        self.results_list = QListWidget()
        self.results_list.setIconSize(QSize(60, 90))  # Размер для мини-постеров
        self.results_list.itemDoubleClicked.connect(self.add_selected_to_favorites)  # Добавить по двойному клику
        self.add_button = QPushButton("Добавить в избранное")
        self.add_button.clicked.connect(self.add_selected_to_favorites)
        self.add_button.setEnabled(False)  # Неактивна, пока ничего не выбрано
        self.results_list.itemSelectionChanged.connect(
            lambda: self.add_button.setEnabled(len(self.results_list.selectedItems()) > 0)
        )

        results_group_layout.addWidget(results_label)
        results_group_layout.addWidget(self.results_list)
        results_group_layout.addWidget(self.add_button)

        # --- Список избранного ---
        favorites_group_layout = QVBoxLayout()
        favorites_label = QLabel("Избранное:")
        self.favorites_list = QListWidget()
        self.favorites_list.setIconSize(QSize(60, 90))
        self.remove_button = QPushButton("Удалить из избранного")
        self.remove_button.clicked.connect(self.remove_selected_favorite)
        self.remove_button.setEnabled(False)  # Неактивна, пока ничего не выбрано
        self.favorites_list.itemSelectionChanged.connect(
            lambda: self.remove_button.setEnabled(len(self.favorites_list.selectedItems()) > 0)
        )

        favorites_group_layout.addWidget(favorites_label)
        favorites_group_layout.addWidget(self.favorites_list)
        favorites_group_layout.addWidget(self.remove_button)

        # --- Сборка макетов ---
        lists_layout.addLayout(results_group_layout, 1)  # 1 - доля ширины
        lists_layout.addLayout(favorites_group_layout, 1)

        main_layout.addLayout(search_layout)
        main_layout.addLayout(lists_layout)
        self.setLayout(main_layout)

    # --- Методы для взаимодействия ---

    def perform_search(self):
        search_term = self.search_input.text().strip()
        if not search_term:
            QMessageBox.warning(self, "Поиск", "Введите название для поиска.")
            return

        self.search_button.setEnabled(False)
        self.search_button.setText("Поиск...")
        self.results_list.clear()  # Очищаем предыдущие результаты

        # Запускаем поиск в отдельном потоке
        self.search_thread = SearchThread(search_term)
        self.search_thread.results_ready.connect(self.display_search_results)
        self.search_thread.error_occurred.connect(self.show_search_error)
        self.search_thread.finished.connect(self.on_search_finished)  # Восстановить кнопку
        self.search_thread.start()

    def on_search_finished(self):
        self.search_button.setEnabled(True)
        self.search_button.setText("Найти")

    def show_search_error(self, error_message):
        QMessageBox.critical(self, "Ошибка поиска", error_message)

    def display_search_results(self, results):
        self.results_list.clear()
        self.search_results = results  # Сохраняем результаты

        if not results:
            QMessageBox.information(self, "Поиск", "Ничего не найдено.")
            return

        # Отменяем старые загрузчики для этого списка
        self.cancel_image_loaders(self.results_list)

        for item in results:
            list_item = QListWidgetItem(f"{item['Title']} ({item['Year']}) - {item['Type'].capitalize()}")
            # Сохраняем imdbID прямо в элементе списка
            list_item.setData(Qt.ItemDataRole.UserRole, item['imdbID'])
            list_item.setIcon(QIcon(QPixmap(60, 90)))  # Placeholder icon
            self.results_list.addItem(list_item)
            # Запускаем загрузку постера в фоне
            self.load_list_item_icon(item['imdbID'], item.get('Poster', 'N/A'), self.results_list)

    def add_selected_to_favorites(self):
        selected_items = self.results_list.selectedItems()
        if not selected_items:
            return

        selected_item_widget = selected_items[0]
        imdb_id = selected_item_widget.data(Qt.ItemDataRole.UserRole)

        # Находим данные по imdbID в результатах поиска
        selected_movie_data = next((item for item in self.search_results if item['imdbID'] == imdb_id), None)

        if selected_movie_data:
            added = database.add_favorite(
                imdb_id=selected_movie_data['imdbID'],
                title=selected_movie_data['Title'],
                year=selected_movie_data['Year'],
                type=selected_movie_data['Type'],
                poster_url=selected_movie_data.get('Poster', 'N/A')
            )
            if added:
                self.load_favorites()  # Обновляем список избранного
                QMessageBox.information(self, "Успех", f"'{selected_movie_data['Title']}' добавлен в избранное!")
            else:
                # Возможно, уже существует (ON CONFLICT) или ошибка БД
                QMessageBox.warning(self, "Информация",
                                    f"'{selected_movie_data['Title']}' уже в избранном или произошла ошибка добавления.")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось найти данные для добавления.")

    def load_favorites(self):
        self.favorites_list.clear()
        favorites = database.get_all_favorites()

        # Отменяем старые загрузчики для этого списка
        self.cancel_image_loaders(self.favorites_list)

        if not favorites:
            # Можно добавить Placeholder item
            # item = QListWidgetItem("Список избранного пуст")
            # item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable) # Сделать невыделяемым
            # self.favorites_list.addItem(item)
            return

        for item in favorites:
            list_item = QListWidgetItem(f"{item['title']} ({item['year']}) - {item['type'].capitalize()}")
            list_item.setData(Qt.ItemDataRole.UserRole, item['imdb_id'])  # Сохраняем ID
            list_item.setIcon(QIcon(QPixmap(60, 90)))  # Placeholder
            self.favorites_list.addItem(list_item)
            # Загружаем постер
            self.load_list_item_icon(item['imdb_id'], item.get('poster_url', 'N/A'), self.favorites_list)

    def remove_selected_favorite(self):
        selected_items = self.favorites_list.selectedItems()
        if not selected_items:
            return

        selected_item_widget = selected_items[0]
        imdb_id = selected_item_widget.data(Qt.ItemDataRole.UserRole)
        title = selected_item_widget.text().split(' (')[0]  # Получаем название для сообщения

        confirm = QMessageBox.question(self, "Подтверждение",
                                       f"Вы уверены, что хотите удалить '{title}' из избранного?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm == QMessageBox.StandardButton.Yes:
            removed = database.remove_favorite(imdb_id)
            if removed:
                self.load_favorites()  # Обновляем список
                QMessageBox.information(self, "Успех", f"'{title}' удален из избранного.")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить '{title}'.")

    def load_list_item_icon(self, imdb_id, url, target_list_widget):
        """Запускает загрузку иконки для элемента списка."""
        # Если уже грузится для этого ID и списка, не запускаем снова
        key = (imdb_id, id(target_list_widget))  # Уникальный ключ: ID фильма + ID виджета списка
        if key in self.image_loaders and self.image_loaders[key].isRunning():
            return

        loader = ImageLoaderThread(imdb_id, url)
        loader.image_ready.connect(
            lambda loaded_id, pixmap: self.set_list_item_icon(loaded_id, pixmap, target_list_widget))
        loader.finished.connect(lambda: self.image_loaders.pop(key, None))  # Удаляем из словаря по завершению
        self.image_loaders[key] = loader
        loader.start()

    def set_list_item_icon(self, imdb_id, pixmap, target_list_widget):
        """Устанавливает загруженную иконку для нужного элемента."""
        for i in range(target_list_widget.count()):
            item = target_list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == imdb_id:
                if not pixmap.isNull():
                    item.setIcon(QIcon(pixmap.scaled(QSize(60, 90), Qt.AspectRatioMode.KeepAspectRatio,
                                                     Qt.TransformationMode.SmoothTransformation)))
                else:
                    # Можно установить иконку по умолчанию, если загрузка не удалась
                    pass
                break  # Нашли нужный элемент

    def cancel_image_loaders(self, target_list_widget):
        """Отменяет все текущие загрузки для указанного списка."""
        list_id = id(target_list_widget)
        loaders_to_remove = []
        for key, loader in self.image_loaders.items():
            item_id, loader_list_id = key
            if loader_list_id == list_id and loader.isRunning():
                # QThread не имеет прямого метода cancel, но можно прервать
                # В данном случае, просто перестаем обрабатывать результат
                # loader.terminate() # terminate() использовать не рекомендуется
                loader.quit()
                loaders_to_remove.append(key)

        for key in loaders_to_remove:
            self.image_loaders.pop(key, None)  # Удаляем из словаря

    def closeEvent(self, event):
        """Обработка закрытия окна для остановки потоков."""
        print("Закрытие приложения...")
        # Отменяем все активные загрузчики
        keys_to_remove = list(self.image_loaders.keys())
        for key in keys_to_remove:
            loader = self.image_loaders.pop(key, None)
            if loader and loader.isRunning():
                loader.quit()  # Просим поток завершиться
                loader.wait(100)  # Даем немного времени на завершение (не идеально)
        print("Загрузчики остановлены.")
        event.accept()  # Разрешаем закрытие
