import sys
from PyQt6.QtWidgets import QApplication, QDialog
from frontend.login_window import LoginWindow
from frontend.movie_app_window import MovieAppWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_dialog = LoginWindow()
    main_window = None


    def on_login_success(user_id: int):
        global main_window
        print(f"Вход успешен (User ID: {user_id}). Запуск основного приложения...")
        main_window = MovieAppWindow(user_id=user_id)
        main_window.show()


    login_dialog.login_successful.connect(on_login_success)
    dialog_result = login_dialog.exec()
    if dialog_result == QDialog.DialogCode.Accepted and main_window:
        print("Запуск главного цикла событий приложения...")
        sys.exit(app.exec())
    else:
        print("Вход не выполнен или окно закрыто. Завершение работы.")
        sys.exit(0)
