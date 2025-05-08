from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QPushButton,
                             QLabel, QMessageBox, QFormLayout, QDialogButtonBox)
from PyQt6.QtCore import pyqtSignal, Qt
from backend.database.auth import login_user, register_user


class LoginWindow(QDialog):
    login_successful = pyqtSignal(int)  # Emits user_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Вход / Регистрация")
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)

        self.tabs = QDialogButtonBox()

        # Login section
        self.username_login_input = QLineEdit()
        self.username_login_input.setPlaceholderText("Имя пользователя")
        self.password_login_input = QLineEdit()
        self.password_login_input.setPlaceholderText("Пароль")
        self.password_login_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_button = QPushButton("Войти")

        login_form = QFormLayout()
        login_form.addRow("Имя пользователя:", self.username_login_input)
        login_form.addRow("Пароль:", self.password_login_input)

        # Registration section
        self.username_reg_input = QLineEdit()
        self.username_reg_input.setPlaceholderText("Новое имя пользователя")
        self.password_reg_input = QLineEdit()
        self.password_reg_input.setPlaceholderText("Новый пароль (мин. 6 симв.)")
        self.password_reg_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_reg_confirm_input = QLineEdit()
        self.password_reg_confirm_input.setPlaceholderText("Подтвердите пароль")
        self.password_reg_confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.register_button = QPushButton("Зарегистрироваться")

        reg_form = QFormLayout()
        reg_form.addRow("Имя пользователя:", self.username_reg_input)
        reg_form.addRow("Пароль:", self.password_reg_input)
        reg_form.addRow("Подтвердить пароль:", self.password_reg_confirm_input)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(QLabel("<h2>Вход</h2>"))
        layout.addLayout(login_form)
        layout.addWidget(self.login_button)
        layout.addSpacing(20)
        layout.addWidget(QLabel("<h2>Регистрация</h2>"))
        layout.addLayout(reg_form)
        layout.addWidget(self.register_button)
        layout.addWidget(self.status_label)

        self.login_button.clicked.connect(self.attempt_login)
        self.username_login_input.returnPressed.connect(self.attempt_login)
        self.password_login_input.returnPressed.connect(self.attempt_login)
        self.register_button.clicked.connect(self.attempt_register)

    def attempt_login(self):
        username = self.username_login_input.text()
        password = self.password_login_input.text()

        success, message, user_id = login_user(username, password)
        print(success, message, user_id)

        self.status_label.setText(message)

        if success and user_id is not None:
            print(f"Login successful for user_id: {user_id}")
            self.login_successful.emit(user_id)
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка входа", message)

    def attempt_register(self):
        username = self.username_reg_input.text()
        password = self.password_reg_input.text()
        password_confirm = self.password_reg_confirm_input.text()

        if not username or not password or not password_confirm:
            QMessageBox.warning(self, "Ошибка регистрации", "Все поля должны быть заполнены.")
            return

        if password != password_confirm:
            QMessageBox.warning(self, "Ошибка регистрации", "Пароли не совпадают.")
            return

        if len(password) < 6:
            QMessageBox.warning(self, "Ошибка регистрации", "Пароль должен быть не менее 6 символов.")
            return

        success, message = register_user(username, password)
        self.status_label.setText(message)

        if success:
            QMessageBox.information(self, "Регистрация успешна",
                                    f"{message}\nТеперь вы можете войти, используя свои данные.")
            self.username_reg_input.clear()
            self.password_reg_input.clear()
            self.password_reg_confirm_input.clear()
            self.username_login_input.setText(username)
            self.password_login_input.setFocus()
        else:
            QMessageBox.warning(self, "Ошибка регистрации", message)