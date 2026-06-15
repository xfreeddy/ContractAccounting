"""Главное окно приложения с навигацией, дашбордом и реестром договоров."""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLineEdit,
    QLabel,
    QFrame,
    QHeaderView,
    QStackedWidget,
    QMessageBox,
)
from PySide6.QtCore import Qt
from database.repository import ContractRepository, test_connection, DB_AVAILABLE
from services.contract_service import ContractService


class MainWindow(QMainWindow):
    """Главное окно системы учёта договоров."""

    def __init__(self):
        """Инициализация главного окна."""
        super().__init__()
        self.setWindowTitle("АС «Контракт-Учёт»")
        self.resize(1200, 800)
        self.setStyleSheet("background-color: #F9F9F9;")
        self.service = ContractService()
        self.editing_row = None  # Для отслеживания режима редактирования
        self.init_ui()
        self._refresh_data()

    def init_ui(self):
        """Создание элементов главного интерфейса."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Навигационная панель (синяя)
        navbar = self.create_navbar()
        main_layout.addWidget(navbar)

        # Стек виджетов для переключения между Дашбордом и Реестром
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Создаём страницы
        self.dashboard_page = self.create_dashboard_page()
        self.registry_page = self.create_registry_page()

        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.registry_page)

        # По умолчанию показываем дашборд
        self.stacked_widget.setCurrentIndex(0)

    def create_navbar(self) -> QFrame:
        """Создание синей навигационной панели."""
        navbar = QFrame()
        navbar.setStyleSheet("""
            QFrame {
                background-color: #0056B3;
                padding: 15px 20px;
            }
        """)
        layout = QHBoxLayout(navbar)
        layout.setContentsMargins(20, 10, 20, 10)

        # Название системы
        title_label = QLabel("АС «Контракт-Учёт»")
        title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)

        layout.addSpacing(30)

        # Кнопка "Дашборд"
        self.btn_dashboard = QPushButton("Дашборд")
        self.btn_dashboard.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: none;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 3px;
            }
        """)
        self.btn_dashboard.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(0)
        )
        layout.addWidget(self.btn_dashboard)

        # Кнопка "Реестр договоров"
        self.btn_registry = QPushButton("Реестр договоров")
        self.btn_registry.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: none;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 3px;
            }
        """)
        self.btn_registry.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(1)
        )
        layout.addWidget(self.btn_registry)

        layout.addStretch()

        # Кнопка "Выход"
        btn_logout = QPushButton("Выход")
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: none;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 3px;
            }
        """)
        btn_logout.clicked.connect(self.close)
        layout.addWidget(btn_logout)

        return navbar

    def create_dashboard_page(self) -> QWidget:
        """Создание страницы дашборда."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)

        # Заголовок
        title_label = QLabel("Главная панель")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333333;")
        layout.addWidget(title_label)

        # Карточки статистики
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        # Карточка "Всего договоров"
        self.card_total = self.create_stat_card("0", "Всего договоров")
        stats_layout.addWidget(self.card_total)

        # Карточка "Истекают в ближайшие 30 дней"
        self.card_expiring = self.create_stat_card("0", "Истекают в ближайшие 30 дней")
        stats_layout.addWidget(self.card_expiring)

        stats_layout.addStretch()
        layout.addLayout(stats_layout)

        # Таблица "Требуют внимания"
        attention_label = QLabel("⚠️ Требуют внимания (истекающий срок)")
        attention_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #333333; margin-top: 10px;"
        )
        layout.addWidget(attention_label)

        self.urgent_table = QTableWidget()
        self.urgent_table.setColumnCount(5)
        self.urgent_table.setHorizontalHeaderLabels(
            ["№ Договора", "Контрагент", "Сумма", "Дата окончания", "Статус"]
        )
        self.urgent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.urgent_table.verticalHeader().setVisible(False)
        self.urgent_table.setMinimumHeight(150)
        self.urgent_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #F1F1F1;
                color: black;
                font-weight: bold;
                font-size: 14px;
                padding: 10px;
                border-bottom: 1px solid black;
            }
            QTableWidget::item {
                padding: 8px;
                color: black;
            }
        """)
        layout.addWidget(self.urgent_table)

        # Ссылка на реестр
        link_label = QLabel("Перейти в полный реестр и добавить новый →")
        link_label.setStyleSheet(
            "color: #0056B3; font-size: 14px; font-weight: bold; margin-top: 10px;"
        )
        link_label.setCursor(Qt.PointingHandCursor)
        link_label.mousePressEvent = lambda e: self.stacked_widget.setCurrentIndex(1)
        layout.addWidget(link_label)

        layout.addStretch()
        return page

    def create_stat_card(self, value: str, label: str) -> QFrame:
        """Создание карточки статистики."""
        card = QFrame()
        card.setFixedWidth(300)
        card.setFixedHeight(120)
        card.setStyleSheet("background-color: white; border-radius: 5px;")

        container = QWidget(card)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(5)

        left_bar = QFrame()
        left_bar.setFixedWidth(5)
        left_bar.setStyleSheet("background-color: black; border: none;")

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 0, 0, 0)
        content_layout.setSpacing(5)

        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #333333;")
        content_layout.addWidget(value_label)

        label_widget = QLabel(label)
        label_widget.setAlignment(Qt.AlignCenter)
        label_widget.setStyleSheet("font-size: 16px; color: #666666;")
        content_layout.addWidget(label_widget)

        card_layout = QHBoxLayout(container)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)
        card_layout.addWidget(left_bar)
        card_layout.addWidget(content_widget, 1)

        return card

    def create_registry_page(self) -> QWidget:
        """Создание страницы реестра договоров."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        title_label = QLabel("Реестр договоров")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333333;")
        layout.addWidget(title_label)

        # Панель поиска
        search_frame = QFrame()
        search_frame.setStyleSheet(
            "background-color: white; border-radius: 5px; padding: 15px;"
        )
        search_layout = QHBoxLayout(search_frame)

        search_label = QLabel("Поиск:")
        search_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #333333;"
        )
        search_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                font-size: 14px;
                color: black;
                background-color: white;
            }
        """)
        search_layout.addWidget(self.search_input, 1)

        search_btn = QPushButton("Найти")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                padding: 8px 20px;
                font-size: 14px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #218838; }
        """)
        search_btn.clicked.connect(self._search_contracts)
        search_layout.addWidget(search_btn)

        layout.addWidget(search_frame)

        # Таблица реестра
        self.registry_table = QTableWidget()
        self.registry_table.setColumnCount(6)
        self.registry_table.setHorizontalHeaderLabels(
            ["№", "Контрагент", "Сумма", "Дата окончания", "Статус", "Действия"]
        )
        self.registry_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.registry_table.verticalHeader().setVisible(False)
        self.registry_table.setMinimumHeight(200)
        self.registry_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #F1F1F1;
                color: black;
                font-weight: bold;
                font-size: 14px;
                padding: 10px;
                border-bottom: 1px solid black;
            }
            QTableWidget::item {
                padding: 8px;
                color: black;
            }
        """)
        layout.addWidget(self.registry_table)

        # Форма добавления договора
        add_form = self.create_add_form()
        layout.addWidget(add_form)

        layout.addStretch()
        return page

    def create_add_form(self) -> QFrame:
        """Создание формы добавления нового договора."""
        form_frame = QFrame()
        form_frame.setStyleSheet(
            "background-color: white; border: 1px solid #DDDDDD; border-radius: 5px; padding: 20px;"
        )
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)

        self.form_title_label = QLabel("Добавить новый договор")
        self.form_title_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #333333; border-bottom: 1px solid black; padding-bottom: 10px;"
        )
        form_layout.addWidget(self.form_title_label)

        # Первая строка полей
        row1_layout = QHBoxLayout()
        self.new_id_input = self._create_field("Номер договора:")
        self.new_counterparty_input = self._create_field("Контрагент:")
        row1_layout.addWidget(self.new_id_input[0])
        row1_layout.addWidget(self.new_id_input[1])
        row1_layout.addSpacing(15)
        row1_layout.addWidget(self.new_counterparty_input[0])
        row1_layout.addWidget(self.new_counterparty_input[1])
        form_layout.addLayout(row1_layout)

        # Вторая строка полей
        row2_layout = QHBoxLayout()
        self.new_amount_input = self._create_field("Сумма (₽):")
        self.new_end_date_input = self._create_field("Дата окончания:")
        self.new_end_date_input[1].setPlaceholderText("ГГГГ-ММ-ДД")
        row2_layout.addWidget(self.new_amount_input[0])
        row2_layout.addWidget(self.new_amount_input[1])
        row2_layout.addSpacing(15)
        row2_layout.addWidget(self.new_end_date_input[0])
        row2_layout.addWidget(self.new_end_date_input[1])
        form_layout.addLayout(row2_layout)

        # Панель кнопок
        buttons_layout = QHBoxLayout()

        self.save_form_btn = QPushButton("💾 Сохранить договор в систему")
        self.save_form_btn.setStyleSheet("""
            QPushButton {
                background-color: #0056B3;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #004494; }
        """)
        self.save_form_btn.clicked.connect(self._save_contract)
        buttons_layout.addWidget(self.save_form_btn)

        self.cancel_edit_btn = QPushButton("✖ Отменить редактирование")
        self.cancel_edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #545B62; }
        """)
        self.cancel_edit_btn.clicked.connect(self._cancel_edit)
        self.cancel_edit_btn.hide()
        buttons_layout.addWidget(self.cancel_edit_btn)

        buttons_layout.addStretch()
        form_layout.addLayout(buttons_layout)

        return form_frame

    def _create_field(self, label_text: str) -> tuple:
        """Вспомогательный метод для создания полей."""
        lbl = QLabel(label_text)
        lbl.setStyleSheet("font-weight: bold; font-size: 13px;")
        widget = QLineEdit()
        widget.setStyleSheet("""
            QLineEdit {
                padding: 7px;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                font-size: 13px;
                color: black;
                background-color: white;
            }
        """)
        return lbl, widget

    def _refresh_data(self):
        """Загрузка данных из базы данных в таблицы."""
        if not DB_AVAILABLE:
            self._load_demo_data()
            return

        contracts = ContractRepository.get_all_contracts()
        self.registry_table.setRowCount(0)

        for contract, cp_name in contracts:
            row = self.registry_table.rowCount()
            self.registry_table.setRowCount(row + 1)

            self.registry_table.setItem(
                row, 0, QTableWidgetItem(str(contract.КодДоговора))
            )
            self.registry_table.setItem(row, 1, QTableWidgetItem(cp_name))
            self.registry_table.setItem(
                row, 2, QTableWidgetItem(f"{contract.Сумма:,.2f}")
            )
            self.registry_table.setItem(
                row, 3, QTableWidgetItem(str(contract.ДатаОкончания))
            )
            self.registry_table.setItem(row, 4, QTableWidgetItem(contract.Статус))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            actions_layout.setSpacing(5)

            btn_edit = QPushButton("Изменить")
            btn_edit.setStyleSheet("""
                QPushButton {
                    background-color: #FFC107; color: black; border: none;
                    border-radius: 3px; padding: 4px 10px; font-size: 11px; font-weight: bold;
                }
                QPushButton:hover { background-color: #E0A800; }
            """)
            btn_edit.clicked.connect(
                lambda checked=False, r=row: self._edit_contract(r)
            )
            actions_layout.addWidget(btn_edit)

            btn_delete = QPushButton("Удалить")
            btn_delete.setStyleSheet("""
                QPushButton {
                    background-color: #DC3545; color: white; border: none;
                    border-radius: 3px; padding: 4px 10px; font-size: 11px; font-weight: bold;
                }
                QPushButton:hover { background-color: #C82333; }
            """)
            btn_delete.clicked.connect(
                lambda checked=False, r=row: self._delete_contract(r)
            )
            actions_layout.addWidget(btn_delete)

            self.registry_table.setCellWidget(row, 5, actions_widget)
            self.registry_table.setRowHeight(row, 40)

        # Обновление карточек статистики
        stats = self.service.get_contract_statistics()
        self._update_stat_card(self.card_total, str(stats["total"]), "Всего договоров")
        self._update_stat_card(
            self.card_expiring, str(stats["expiring"]), "Истекают в ближайшие 30 дней"
        )

        # Загрузка истекающих договоров
        expiring = ContractRepository.get_expiring_contracts()
        self.urgent_table.setRowCount(0)
        if expiring:
            for contract, cp_name in expiring:
                row = self.urgent_table.rowCount()
                self.urgent_table.setRowCount(row + 1)
                self.urgent_table.setItem(
                    row, 0, QTableWidgetItem(str(contract.КодДоговора))
                )
                self.urgent_table.setItem(row, 1, QTableWidgetItem(cp_name))
                self.urgent_table.setItem(
                    row, 2, QTableWidgetItem(f"{contract.Сумма:,.2f}")
                )
                self.urgent_table.setItem(
                    row, 3, QTableWidgetItem(str(contract.ДатаОкончания))
                )
                self.urgent_table.setItem(row, 4, QTableWidgetItem(contract.Статус))
                self.urgent_table.setRowHeight(row, 36)
        else:
            # Заглушка когда нет истекающих договоров
            self.urgent_table.setRowCount(1)
            placeholder = QTableWidgetItem(
                "✅  Нет договоров с истекающим сроком в ближайшие 30 дней"
            )
            placeholder.setTextAlignment(Qt.AlignCenter)
            placeholder.setForeground(Qt.darkGreen)
            self.urgent_table.setItem(0, 0, placeholder)
            self.urgent_table.setSpan(0, 0, 1, 5)
            self.urgent_table.setRowHeight(0, 48)

    def _load_demo_data(self):
        """Показывает демо-данные когда нет подключения к БД."""
        from datetime import date, timedelta

        # Демо-договоры для реестра
        demo_contracts = [
            ("001", "ООО «Альфа Трейд»", "450 000,00", "2026-08-15", "Активен"),
            ("002", "ИП Иванов А.С.", "120 500,00", "2026-07-01", "Активен"),
            ("003", "ЗАО «СтройГрупп»", "1 200 000,00", "2026-06-25", "Активен"),
            ("004", "ООО «ТехСервис»", "87 300,00", "2025-12-31", "Истёк"),
        ]

        self.registry_table.setRowCount(0)
        for data in demo_contracts:
            row = self.registry_table.rowCount()
            self.registry_table.setRowCount(row + 1)
            for col, val in enumerate(data):
                item = QTableWidgetItem(val)
                self.registry_table.setItem(row, col, item)

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            actions_layout.setSpacing(5)

            btn_edit = QPushButton("Изменить")
            btn_edit.setStyleSheet("""
                QPushButton {
                    background-color: #FFC107; color: black; border: none;
                    border-radius: 3px; padding: 4px 10px; font-size: 11px; font-weight: bold;
                }
                QPushButton:hover { background-color: #E0A800; }
            """)
            btn_edit.clicked.connect(
                lambda checked=False, r=row: self._edit_contract(r)
            )
            actions_layout.addWidget(btn_edit)

            btn_delete = QPushButton("Удалить")
            btn_delete.setStyleSheet("""
                QPushButton {
                    background-color: #DC3545; color: white; border: none;
                    border-radius: 3px; padding: 4px 10px; font-size: 11px; font-weight: bold;
                }
                QPushButton:hover { background-color: #C82333; }
            """)
            btn_delete.clicked.connect(
                lambda checked=False, r=row: self._delete_contract(r)
            )
            actions_layout.addWidget(btn_delete)

            self.registry_table.setCellWidget(row, 5, actions_widget)
            self.registry_table.setRowHeight(row, 40)

        # Карточки статистики
        self._update_stat_card(self.card_total, "4", "Всего договоров")
        self._update_stat_card(self.card_expiring, "2", "Истекают в ближайшие 30 дней")

        # Демо-данные для таблицы "Требуют внимания"
        today = date.today()
        demo_expiring = [
            (
                "002",
                "ИП Иванов А.С.",
                "120 500,00",
                str(today + timedelta(days=20)),
                "Активен",
            ),
            (
                "003",
                "ЗАО «СтройГрупп»",
                "1 200 000,00",
                str(today + timedelta(days=14)),
                "Активен",
            ),
        ]

        self.urgent_table.setRowCount(0)
        for data in demo_expiring:
            row = self.urgent_table.rowCount()
            self.urgent_table.setRowCount(row + 1)
            for col, val in enumerate(data):
                item = QTableWidgetItem(val)
                # Подсветить строки с истекающим сроком
                if col == 3:
                    item.setForeground(Qt.red)
                self.urgent_table.setItem(row, col, item)
            self.urgent_table.setRowHeight(row, 36)

    def _update_stat_card(self, card: QFrame, value: str, label: str):
        """Обновляет текст внутри карточки статистики."""
        labels = card.findChildren(QLabel)
        if len(labels) >= 2:
            labels[0].setText(value)
            labels[1].setText(label)

    def _search_contracts(self):
        """Поиск договоров."""
        query = self.search_input.text().strip()
        if not query:
            self._refresh_data()
            return
        results = ContractRepository.search_contracts(query)
        self.registry_table.setRowCount(0)
        for contract, cp_name in results:
            row = self.registry_table.rowCount()
            self.registry_table.setRowCount(row + 1)
            self.registry_table.setItem(
                row, 0, QTableWidgetItem(str(contract.КодДоговора))
            )
            self.registry_table.setItem(row, 1, QTableWidgetItem(cp_name))
            self.registry_table.setItem(
                row, 2, QTableWidgetItem(f"{contract.Сумма:,.2f}")
            )
            self.registry_table.setItem(
                row, 3, QTableWidgetItem(str(contract.ДатаОкончания))
            )
            self.registry_table.setItem(row, 4, QTableWidgetItem(contract.Статус))

            # Кнопки действий (как в _refresh_data)
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            actions_layout.setSpacing(5)

            btn_edit = QPushButton("Изменить")
            btn_edit.setStyleSheet("""
                QPushButton {
                    background-color: #FFC107;
                    color: black;
                    border: none;
                    border-radius: 3px;
                    padding: 4px 10px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #E0A800; }
            """)
            btn_edit.clicked.connect(
                lambda checked=False, r=row: self._edit_contract(r)
            )
            actions_layout.addWidget(btn_edit)

            btn_delete = QPushButton("Удалить")
            btn_delete.setStyleSheet("""
                QPushButton {
                    background-color: #DC3545;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 4px 10px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #C82333; }
            """)
            btn_delete.clicked.connect(
                lambda checked=False, r=row: self._delete_contract(r)
            )
            actions_layout.addWidget(btn_delete)

            self.registry_table.setCellWidget(row, 5, actions_widget)
            self.registry_table.setRowHeight(row, 40)

        if not results:
            QMessageBox.information(self, "Поиск", "Ничего не найдено")

    def _save_contract(self):
        """Сохранение договора."""
        name = self.new_id_input[1].text().strip()
        cp = self.new_counterparty_input[1].text().strip()
        amount = self.new_amount_input[1].text().strip()
        end_date = self.new_end_date_input[1].text().strip()

        if not all([name, cp, amount, end_date]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        try:
            from datetime import date as dt

            contract_data = {
                "Наименование": name,
                "ДатаНачала": dt.today(),
                "ДатаОкончания": dt.fromisoformat(end_date),
                "Сумма": float(amount.replace(",", ".")),
                "ТипДоговора": "Поставка",
                "Статус": "Активен",
            }
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Неверный формат даты или суммы")
            return

        # Проверка бизнес-правил через сервисный слой
        # (сумма > 0, дата окончания не раньше даты начала)
        errors = self.service.validate_contract_data(contract_data)
        if errors:
            QMessageBox.warning(self, "Ошибка", "\n".join(errors))
            return

        if self.editing_row is not None:
            # Режим редактирования — обновляем существующий договор
            contract_id_item = self.registry_table.item(self.editing_row, 0)
            if contract_id_item is None:
                QMessageBox.critical(self, "Ошибка", "Не удалось определить ID договора")
                return
            contract_id = int(contract_id_item.text())

            # Получаем/создаём контрагента чтобы получить его код
            from database.repository import CounterpartyRepository
            counterparty = CounterpartyRepository.get_or_create(cp)
            if not counterparty:
                QMessageBox.critical(self, "Ошибка", "Не удалось найти или создать контрагента")
                return
            contract_data["КодКонтрагента"] = counterparty.КодКонтрагента

            if ContractRepository.update_contract(contract_id, contract_data):
                QMessageBox.information(self, "Успех", f"Договор №{contract_id} обновлён!")
                self._clear_form()
                self._refresh_data()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось обновить запись в БД")
        else:
            # Режим создания нового договора
            if self.service.create_with_counterparty(contract_data, cp):
                QMessageBox.information(self, "Успех", "Договор сохранен!")
                self._clear_form()
                self._refresh_data()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось сохранить в БД")

    def _edit_contract(self, row: int):
        """Редактирование договора."""
        self.new_id_input[1].setText(self.registry_table.item(row, 0).text())
        self.new_counterparty_input[1].setText(self.registry_table.item(row, 1).text())
        self.new_amount_input[1].setText(
            self.registry_table.item(row, 2).text().replace(" ", "").replace(",", "")
        )
        self.new_end_date_input[1].setText(self.registry_table.item(row, 3).text())
        self.editing_row = row

        # Обновляем UI формы — переходим в режим редактирования
        contract_id = self.registry_table.item(row, 0).text()
        self.form_title_label.setText(f"✏️ Редактирование договора №{contract_id}")
        self.form_title_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #856404; "
            "border-bottom: 1px solid #856404; padding-bottom: 10px;"
        )
        self.save_form_btn.setText("💾 Сохранить изменения")
        self.cancel_edit_btn.show()

        # Прокручиваем к форме
        self.stacked_widget.setCurrentIndex(1)
        QMessageBox.information(
            self,
            "Редактирование",
            f"Данные договора №{contract_id} загружены в форму.\nИзмените нужные поля и нажмите «Сохранить изменения».",
        )

    def _delete_contract(self, row: int):
        """Удаление договора."""
        contract_id = self.registry_table.item(row, 0).text()
        if (
            QMessageBox.question(
                self, "Подтверждение", f"Удалить договор №{contract_id}?"
            )
            == QMessageBox.Yes
        ):
            if ContractRepository.delete_contract(int(contract_id)):
                QMessageBox.information(self, "Успех", "Удалено")
                self._refresh_data()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить")

    def _cancel_edit(self):
        """Отмена режима редактирования без сохранения."""
        self._clear_form()

    def _clear_form(self):
        """Очистка формы и сброс в режим добавления."""
        self.new_id_input[1].clear()
        self.new_counterparty_input[1].clear()
        self.new_amount_input[1].clear()
        self.new_end_date_input[1].clear()
        self.editing_row = None

        # Возвращаем форму в режим добавления
        self.form_title_label.setText("Добавить новый договор")
        self.form_title_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #333333; "
            "border-bottom: 1px solid black; padding-bottom: 10px;"
        )
        self.save_form_btn.setText("💾 Сохранить договор в систему")
        self.cancel_edit_btn.hide()
