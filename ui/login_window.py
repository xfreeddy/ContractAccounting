"""
Окно авторизации пользователя.
Отвечает за ввод учётных данных и передачу их в сервис аутентификации.
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QMessageBox,
)
from PySide6.QtCore import Qt
from database.repository import UserRepository


class LoginWindow(QDialog):
    """
    Диалоговое окно входа в систему.

    Attributes:
        user_data: Словарь с данными авторизованного пользователя.
    """

    def __init__(self, parent=None):
        """Инициализация интерфейса окна входа."""
        super().__init__(parent)
        self.setWindowTitle("АС «Контракт-Учёт» — Вход")
        self.resize(420, 520)
        self.setStyleSheet("background-color: #F4F4F4;")
        self.user_data = None
        self._init_ui()

    def _init_ui(self):
        """Создание и компоновка элементов интерфейса."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(30, 30, 30, 30)

        card = QFrame()
        card.setStyleSheet(
            "background-color: white; border-radius: 6px; padding: 25px;"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)

        title = QLabel("АС «Контракт-Учёт»")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #333333;")
        card_layout.addWidget(title)

        subtitle = QLabel("Введите данные для входа")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #666666; margin-bottom: 8px;")
        card_layout.addWidget(subtitle)

        self.login_input = self._create_input("Логин")
        self.password_input = self._create_input("Пароль", echo_mode=True)
        card_layout.addWidget(self.login_input)
        card_layout.addWidget(self.password_input)

        self.error_label = QLabel()
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet(
            "color: #DC3545; font-size: 13px; background-color: #F8D7DA; "
            "border: 1px solid #F5C6CB; border-radius: 4px; padding: 6px;"
        )
        self.error_label.hide()
        card_layout.addWidget(self.error_label)

        self.login_btn = QPushButton("Войти")
        self.login_btn.setStyleSheet(
            "background-color: #0056B3; color: white; padding: 10px; "
            "font-size: 15px; border: none; border-radius: 4px;"
        )
        self.login_btn.clicked.connect(self._handle_login)
        card_layout.addWidget(self.login_btn)

        info_box = QFrame()
        info_box.setStyleSheet(
            "background-color: #FFF8E1; border: 1px solid #FFE082; border-radius: 4px; padding: 10px;"
        )
        info_layout = QVBoxLayout(info_box)
        info_layout.setSpacing(4)
        info_layout.addWidget(QLabel("Тестовые доступы:"))
        info_layout.addWidget(QLabel("• admin / 123"))
        info_layout.addWidget(QLabel("• manager / 123"))
        card_layout.addWidget(info_box)

        layout.addWidget(card)

    def _create_input(self, placeholder: str, echo_mode: bool = False) -> QLineEdit:
        """Создаёт стилизованное поле ввода."""
        widget = QLineEdit()
        widget.setPlaceholderText(placeholder)
        if echo_mode:
            widget.setEchoMode(QLineEdit.Password)
        widget.setStyleSheet(
            "padding: 9px; border: 1px solid #CCCCCC; border-radius: 4px; "
            "font-size: 14px; background-color: white; color: black;"
        )
        widget.returnPressed.connect(self._handle_login)
        return widget

    def _show_error(self, message: str):
        """Отображает сообщение об ошибке."""
        self.error_label.setText(f"⚠ {message}")
        self.error_label.show()

    def _hide_error(self):
        """Скрывает сообщение об ошибке."""
        self.error_label.hide()
        self.error_label.clear()

    def _handle_login(self):
        """Обрабатывает попытку входа и проверяет учётные данные."""
        self._hide_error()
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()

        if not login or not password:
            self._show_error("Заполните все поля")
            return

        self.user_data = UserRepository.authenticate(login, password)
        if self.user_data:
            self.accept()
        else:
            self._show_error("Неверный логин или пароль")
