"""
Централизованная настройка логирования приложения АС «Контракт-Учёт».

Логи пишутся одновременно в файл app.log (для последующего анализа)
и в консоль (для оперативной отладки во время разработки).
Используется в рамках Дня 5 для отладки и трассировки работы программы.
"""

import logging
import sys

LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(log_file: str = "app.log", level: int = logging.DEBUG):
    """
    Настраивает корневой логгер: вывод в файл и в консоль.

    Args:
        log_file: Имя файла журнала.
        level: Минимальный уровень логирования.
    """
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Запись в файл (UTF-8, чтобы корректно сохранялась кириллица)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    # Вывод в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    # Защита от дублирования обработчиков при повторном вызове
    if not root.handlers:
        root.addHandler(file_handler)
        root.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Возвращает именованный логгер для модуля."""
    return logging.getLogger(name)
