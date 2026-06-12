"""Сервис для бизнес-логики работы с договорами."""

from datetime import date
from database.repository import ContractRepository, CounterpartyRepository


class ContractService:
    """Сервисный слой для обработки бизнес-логики договоров."""

    def __init__(self):
        """Инициализация сервиса контрактов."""
        self.repository = ContractRepository()
        self.counterparty_repo = CounterpartyRepository()

    def validate_contract_data(self, data: dict) -> list:
        """
        Валидация данных договора.

        Args:
            data: Словарь с данными договора

        Returns:
            Список ошибок валидации
        """
        errors = []

        if not data.get("Наименование"):
            errors.append("Название договора обязательно")

        if not data.get("Сумма") or data["Сумма"] <= 0:
            errors.append("Сумма договора должна быть больше 0")

        if data.get("ДатаОкончания") and data.get("ДатаНачала"):
            if data["ДатаОкончания"] < data["ДатаНачала"]:
                errors.append("Дата окончания не может быть раньше даты начала")

        return errors

    def create_with_counterparty(
        self, contract_data: dict, counterparty_name: str
    ) -> bool:
        """
        Создать договор с автоматическим созданием контрагента.

        Args:
            contract_data: Данные договора
            counterparty_name: Название контрагента

        Returns:
            bool: True при успешном создании
        """
        counterparty = self.counterparty_repo.get_or_create(counterparty_name)
        if not counterparty:
            return False

        contract_data["КодКонтрагента"] = counterparty.КодКонтрагента
        return self.repository.create_contract(contract_data) is not None

    def get_contract_statistics(self):
        """Получить статистику для дашборда."""
        contracts = self.repository.get_all_contracts()

        total = len(contracts)
        active = sum(1 for c, _ in contracts if c.Статус == "Активен")
        today = date.today()
        expiring = sum(
            1
            for c, _ in contracts
            if c.ДатаОкончания
            and (c.ДатаОкончания - today).days <= 30
            and c.Статус == "Активен"
        )

        return {"total": total, "active": active, "expiring": expiring}
