"""
Тесты сервиса договоров.
Проверяют валидацию данных и расчёт статистики.
"""

import pytest
from services.contract_service import ContractService
from datetime import date, timedelta


def test_validation_empty_name():
    svc = ContractService()
    assert "Название договора обязательно" in svc.validate(
        {
            "Сумма": 100,
            "ДатаНачала": date.today(),
            "ДатаОкончания": date.today() + timedelta(days=10),
        }
    )


def test_validation_negative_amount():
    svc = ContractService()
    assert "Сумма должна быть больше нуля" in svc.validate(
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
    assert "Дата окончания не может быть раньше начала" in svc.validate(
        {
            "Наименование": "Тест",
            "Сумма": 100,
            "ДатаНачала": today + timedelta(days=5),
            "ДатаОкончания": today,
        }
    )
