"""
Модуль формы для создания и редактирования договоров.
Реализует диалоговое окно с валидацией данных.
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QDateEdit,
    QPushButton,
    QScrollArea,
    QWidget,
    QMessageBox,
    QFrame,
)
from PySide6.QtCore import QDate


class ContractFormDialog(QDialog):
    """
    Диалоговое окно для создания и редактирования договора.
    Содержит поля ввода с валидацией обязательных полей.
    """

    def __init__(self, parent=None):
        """
        Инициализация формы договора.

        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.setWindowTitle("Новый договор")
        self.resize(600, 700)
        self.init_ui()

    def init_ui(self):
        """
        Создание и настройка элементов интерфейса формы.
        Включает поля ввода, выпадающие списки и кнопки управления.
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок формы
        title_label = QLabel("Создание нового договора")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #0078D7;")
        layout.addWidget(title_label)

        # Область прокрутки для полей формы
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        form_layout = QVBoxLayout(content_widget)
        form_layout.setSpacing(12)

        # Поле: Название договора (обязательное)
        self.title_input = self.create_field(
            "Название договора", QLineEdit(), required=True
        )
        form_layout.addWidget(self.title_input[0])
        form_layout.addWidget(self.title_input[1])

        # Поле: Контрагент (обязательное)
        self.counterparty_input = self.create_field(
            "Контрагент", QLineEdit(), required=True
        )
        form_layout.addWidget(self.counterparty_input[0])
        form_layout.addWidget(self.counterparty_input[1])

        # Поле: Тип договора с расшифрованными значениями
        # Исправлено согласно юзабилити-тестированию (проблема №3)
        self.type_combo = self.create_field("Тип договора", QComboBox(), required=True)
        self.type_combo[1].addItems(["Поставка", "Услуги", "Аренда", "Подряд"])
        form_layout.addWidget(self.type_combo[0])
        form_layout.addWidget(self.type_combo[1])

        # Поле: Сумма договора (обязательное)
        self.amount_input = self.create_field(
            "Сумма (руб.)", QLineEdit(), required=True
        )
        self.amount_input[1].setPlaceholderText("Введите сумму")
        form_layout.addWidget(self.amount_input[0])
        form_layout.addWidget(self.amount_input[1])

        # Поле: Дата начала (обязательное)
        self.start_date = self.create_field("Дата начала", QDateEdit(), required=True)
        self.start_date[1].setCalendarPopup(True)
        self.start_date[1].setDate(QDate.currentDate())
        form_layout.addWidget(self.start_date[0])
        form_layout.addWidget(self.start_date[1])

        # Поле: Дата окончания (обязательное)
        self.end_date = self.create_field("Дата окончания", QDateEdit(), required=True)
        self.end_date[1].setCalendarPopup(True)
        self.end_date[1].setDate(QDate.currentDate().addYears(1))
        form_layout.addWidget(self.end_date[0])
        form_layout.addWidget(self.end_date[1])

        # Пояснение к обязательным полям
        note_label = QLabel("* - обязательные поля для заполнения")
        note_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
        form_layout.addWidget(note_label)

        form_layout.addStretch()
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # Панель кнопок закреплена внизу (решение проблемы юзабилити №5)
        button_frame = QFrame()
        button_frame.setStyleSheet(
            "background-color: #f5f5f5; padding: 15px; border-radius: 6px;"
        )
        button_layout = QHBoxLayout(button_frame)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #ccc;
                color: black;
                padding: 12px 24px;
                font-size: 14px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #bbb;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)

        self.save_button = QPushButton("💾 Сохранить")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #106EBE;
            }
        """)
        self.save_button.clicked.connect(self.save_contract)

        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        layout.addWidget(button_frame)

    def create_field(self, label_text, widget, required=False):
        """
        Создаёт поле формы с меткой и стилизацией.

        Args:
            label_text: Текст метки поля
            widget: Виджет поля ввода (QLineEdit, QComboBox, QDateEdit)
            required: Флаг обязательности поля (добавляет красную звёздочку)

        Returns:
            tuple: Кортеж из метки (QLabel) и виджета поля
        """
        label = QLabel(label_text)
        label.setStyleSheet("font-weight: bold; font-size: 13px;")

        # Добавление красной звёздочки для обязательных полей
        # Реализация требования юзабилити №4
        if required:
            label.setText(f"{label_text} *")
            label.setStyleSheet("font-weight: bold; font-size: 13px; color: #D83B01;")

        widget.setStyleSheet("""
            QLineEdit, QComboBox, QDateEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 1px solid #0078D7;
            }
        """)

        return label, widget

    def save_contract(self):
        """
        Валидация и сохранение данных договора.
        Проверяет обязательные поля перед сохранением.
        """
        # Проверка заполнения обязательных полей
        if not self.title_input[1].text().strip():
            QMessageBox.warning(
                self, "Ошибка", "Пожалуйста, заполните название договора"
            )
            return

        if not self.counterparty_input[1].text().strip():
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, укажите контрагента")
            return

        if not self.amount_input[1].text().strip():
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите сумму договора")
            return

        # Проверка, что сумма — положительное число
        try:
            amount = float(self.amount_input[1].text().strip().replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Сумма должна быть числом")
            return
        if amount <= 0:
            QMessageBox.warning(self, "Ошибка", "Сумма должна быть больше 0")
            return

        # Проверка порядка дат
        if self.end_date[1].date() < self.start_date[1].date():
            QMessageBox.warning(
                self, "Ошибка", "Дата окончания не может быть раньше даты начала"
            )
            return

        # Здесь будет вызов сервиса для сохранения в БД
        # self.accept() закроет диалог с кодом успеха
        self.accept()
