from backend.database.auth import login_user, register_user
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QPushButton,
                             QLabel, QMessageBox, QFormLayout, QHBoxLayout,
                             QStackedWidget, QWidget)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QPalette


class LoginWindow(QDialog):
    login_successful = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Вход / Регистрация")
        self.setMinimumSize(400, 400)

        self.bg_color = QColor(240, 240, 245)
        self.tab_active_color = QColor(80, 100, 220)
        self.tab_inactive_color = QColor(180, 180, 200)
        self.login_button_color = QColor(76, 175, 80)
        self.text_color = QColor(50, 50, 50)
        self.error_color = QColor(220, 53, 69)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, self.bg_color)
        palette.setColor(QPalette.ColorRole.WindowText, self.text_color)
        self.setPalette(palette)

        self.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
                min-width: 120px;
            }}

            QPushButton#tabButton {{
                background-color: {self.tab_inactive_color.name()};
                color: white;
                padding: 12px 0;
            }}

            QPushButton#tabButton:checked {{
                background-color: {self.tab_active_color.name()};
            }}

            QPushButton#loginButton {{
                background-color: {self.login_button_color.name()};
                color: white;
                font-size: 15px;
                padding: 12px 24px;
            }}

            QPushButton#loginButton:hover {{
                background-color: {self.login_button_color.darker(110).name()};
            }}

            QPushButton#registerButton {{
                background-color: {self.login_button_color.name()};
                color: white;
            }}

            QPushButton#registerButton:hover {{
                background-color: {self.login_button_color.darker(110).name()};
            }}

            QLineEdit {{
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 14px;
                min-height: 20px;
                margin-bottom: 8px;
            }}

            QLineEdit:focus {{
                border: 2px solid {self.tab_active_color.name()};
            }}

            QLabel {{
                color: {self.text_color.name()};
                font-size: 14px;
            }}

            QLabel#title {{
                font-size: 20px;
                font-weight: 600;
                margin-bottom: 15px;
            }}

            QLabel#status {{
                color: {self.error_color.name()};
                font-size: 13px;
                margin-top: 10px;
            }}

            QFormLayout {{
                margin: 0;
                spacing: 15px;
            }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        self.tab_widget = QStackedWidget()

        tab_buttons = QHBoxLayout()
        tab_buttons.setSpacing(10)
        tab_buttons.setContentsMargins(0, 0, 0, 15)

        self.login_tab_btn = QPushButton("Вход")
        self.login_tab_btn.setObjectName("tabButton")
        self.login_tab_btn.setCheckable(True)
        self.login_tab_btn.setChecked(True)
        self.login_tab_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.register_tab_btn = QPushButton("Регистрация")
        self.register_tab_btn.setObjectName("tabButton")
        self.register_tab_btn.setCheckable(True)
        self.register_tab_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        tab_buttons.addWidget(self.login_tab_btn)
        tab_buttons.addWidget(self.register_tab_btn)


        self.login_tab_btn.clicked.connect(self.switch_to_login)
        self.register_tab_btn.clicked.connect(self.switch_to_register)

        main_layout.addLayout(tab_buttons)


        login_widget = QWidget()
        login_layout = QVBoxLayout(login_widget)
        login_layout.setContentsMargins(10, 10, 10, 10)
        login_layout.setSpacing(20)

        login_title = QLabel("Вход в аккаунт")
        login_title.setObjectName("title")
        login_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        login_form = QFormLayout()
        login_form.setContentsMargins(20, 0, 20, 0)
        login_form.setVerticalSpacing(18)

        self.username_login_input = QLineEdit()
        self.username_login_input.setPlaceholderText("Введите имя пользователя")
        self.username_login_input.setMinimumWidth(300)

        self.password_login_input = QLineEdit()
        self.password_login_input.setPlaceholderText("Введите пароль")
        self.password_login_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_login_input.setMinimumWidth(300)

        login_form.addRow("Имя пользователя:", self.username_login_input)
        login_form.addRow("Пароль:", self.password_login_input)

        self.login_button = QPushButton("Войти")
        self.login_button.setObjectName("loginButton")

        self.login_status_label = QLabel("")
        self.login_status_label.setObjectName("status")
        self.login_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        login_layout.addWidget(login_title)
        login_layout.addLayout(login_form)
        login_layout.addWidget(self.login_button, 0, Qt.AlignmentFlag.AlignHCenter)
        login_layout.addWidget(self.login_status_label)
        login_layout.addStretch()


        register_widget = QWidget()
        register_layout = QVBoxLayout(register_widget)
        register_layout.setContentsMargins(10, 10, 10, 10)
        register_layout.setSpacing(20)

        register_title = QLabel("Создать аккаунт")
        register_title.setObjectName("title")
        register_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        reg_form = QFormLayout()
        reg_form.setContentsMargins(20, 0, 20, 0)
        reg_form.setVerticalSpacing(18)

        self.username_reg_input = QLineEdit()
        self.username_reg_input.setPlaceholderText("Придумайте имя пользователя")
        self.username_reg_input.setMinimumWidth(300)

        self.password_reg_input = QLineEdit()
        self.password_reg_input.setPlaceholderText("Создайте пароль (мин. 6 симв.)")
        self.password_reg_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_reg_input.setMinimumWidth(300)

        self.password_reg_confirm_input = QLineEdit()
        self.password_reg_confirm_input.setPlaceholderText("Подтвердите пароль")
        self.password_reg_confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_reg_confirm_input.setMinimumWidth(300)

        reg_form.addRow("Имя пользователя:", self.username_reg_input)
        reg_form.addRow("Пароль:", self.password_reg_input)
        reg_form.addRow("Подтвердите пароль:", self.password_reg_confirm_input)

        self.register_button = QPushButton("Зарегистрироваться")
        self.register_button.setObjectName("loginButton")

        self.reg_status_label = QLabel("")
        self.reg_status_label.setObjectName("status")
        self.reg_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        register_layout.addWidget(register_title)
        register_layout.addLayout(reg_form)
        register_layout.addWidget(self.register_button, 0, Qt.AlignmentFlag.AlignHCenter)
        register_layout.addWidget(self.reg_status_label)
        register_layout.addStretch()

        self.tab_widget.addWidget(login_widget)
        self.tab_widget.addWidget(register_widget)

        main_layout.addWidget(self.tab_widget)


        self.login_button.clicked.connect(self.attempt_login)
        self.username_login_input.returnPressed.connect(self.attempt_login)
        self.password_login_input.returnPressed.connect(self.attempt_login)
        self.register_button.clicked.connect(self.attempt_register)

    def attempt_login(self):
        username = self.username_login_input.text()
        password = self.password_login_input.text()

        success, message, user_id = login_user(username, password)

        self.login_status_label.setText(message)

        if success and user_id is not None:
            self.login_successful.emit(user_id)
            self.accept()

    def attempt_register(self):
        username = self.username_reg_input.text()
        password = self.password_reg_input.text()
        password_confirm = self.password_reg_confirm_input.text()

        if not username or not password or not password_confirm:
            self.reg_status_label.setText("Все поля должны быть заполнены")
            return

        if password != password_confirm:
            self.reg_status_label.setText("Пароли не совпадают")
            return

        if len(password) < 6:
            self.reg_status_label.setText("Пароль должен быть не менее 6 символов")
            return

        success, message = register_user(username, password)
        self.reg_status_label.setText(message)

        if success:
            QMessageBox.information(self, "Регистрация успешна",
                                    f"{message}\nТеперь вы можете войти, используя свои данные.")
            self.username_reg_input.clear()
            self.password_reg_input.clear()
            self.password_reg_confirm_input.clear()
            self.username_login_input.setText(username)
            self.password_login_input.setFocus()
            self.tab_widget.setCurrentIndex(0)
            self.login_tab_btn.setChecked(True)
            self.register_tab_btn.setChecked(False)

    def switch_to_login(self):
        """Переключение на вкладку входа с обновлением состояния кнопок"""
        self.login_tab_btn.setChecked(True)
        self.register_tab_btn.setChecked(False)
        self.tab_widget.setCurrentIndex(0)

    def switch_to_register(self):
        """Переключение на вкладку регистрации с обновлением состояния кнопок"""
        self.register_tab_btn.setChecked(True)
        self.login_tab_btn.setChecked(False)
        self.tab_widget.setCurrentIndex(1)