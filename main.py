"""
Точка входа в приложение АС «Контракт-Учёт».
Инициализирует среду выполнения, применяет стили и запускает цикл событий.
"""

import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from database.repository import test_connection


def main():
    """Запуск приложения с проверкой окружения и авторизацией."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Глобальные стили для единообразия интерфейса
    app.setStyleSheet(
        "QMainWindow { background-color: #F9F9F9; }"
        "QLineEdit, QComboBox, QDateEdit, QTextEdit { color: black; background-color: white; }"
        "QLabel { color: #333333; }"
        "QPushButton { color: white; }"
    )

    # Проверка подключения к базе данных перед запуском
    success, msg = test_connection()
    if not success:
        QMessageBox.warning(None, "Внимание", f"Не удалось подключиться к БД.\n{msg}")

    login = LoginWindow()
    if login.exec():
        main_win = MainWindow()
        main_win.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
