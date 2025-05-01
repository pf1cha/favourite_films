import sys
from PyQt6.QtWidgets import QApplication
from frontend.main_window import MovieApp

if __name__ == '__main__':
    # Важно: Создаем таблицу перед запуском GUI
    # Проверка/создание таблицы базы данных
    # database.create_table_if_not_exists()
    print("Запуск приложения...")

    app = QApplication(sys.argv)
    main_window = MovieApp()
    main_window.show()
    sys.exit(app.exec())
