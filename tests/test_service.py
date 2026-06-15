"""
Тесты сервиса договоров.
Проверяют валидацию данных и расчёт статистики.
"""

import pytest
from services.contract_service import ContractService
from datetime import date, timedelta


def test_validation_empty_name():
    svc = ContractService()
    assert "Название договора обязательно" in svc.validate_contract_data(
        {
            "Сумма": 100,
            "ДатаНачала": date.today(),
            "ДатаОкончания": date.today() + timedelta(days=10),
        }
    )


def test_validation_negative_amount():
    svc = ContractService()
    assert "Сумма договора должна быть больше 0" in svc.validate_contract_data(
        {
            "Наименование": "Тест",
            "Сумма": -50,
            "ДатаНачала": date.today(),
            "ДатаОкончания": date.today() + timedelta(days=10),
        }
    )


def test_validation_date_order():
    svc = ContractService()
    today = date.today()
    assert "Дата окончания не может быть раньше даты начала" in svc.validate_contract_data(
        {
            "Наименование": "Тест",
            "Сумма": 100,
            "ДатаНачала": today + timedelta(days=5),
            "ДатаОкончания": today,
        }
    )
