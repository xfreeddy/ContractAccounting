"""
Тесты сервиса договоров.
Проверяют валидацию данных и расчёт статистики.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import date, timedelta


# Патчим репозитории ДО импорта ContractService,
# чтобы не было попытки подключения к SQL Server при инициализации.
@pytest.fixture
def svc():
    with patch("services.contract_service.ContractRepository") as mock_repo, \
         patch("services.contract_service.CounterpartyRepository") as mock_cp:
        mock_repo.return_value = MagicMock()
        mock_cp.return_value = MagicMock()
        from services.contract_service import ContractService
        yield ContractService()


def test_validation_empty_name(svc):
    assert "Название договора обязательно" in svc.validate_contract_data(
        {
            "Сумма": 100,
            "ДатаНачала": date.today(),
            "ДатаОкончания": date.today() + timedelta(days=10),
        }
    )


def test_validation_negative_amount(svc):
    assert "Сумма договора должна быть больше 0" in svc.validate_contract_data(
        {
            "Наименование": "Тест",
            "Сумма": -50,
            "ДатаНачала": date.today(),
            "ДатаОкончания": date.today() + timedelta(days=10),
        }
    )


def test_validation_date_order(svc):
    today = date.today()
    assert "Дата окончания не может быть раньше даты начала" in svc.validate_contract_data(
        {
            "Наименование": "Тест",
            "Сумма": 100,
            "ДатаНачала": today + timedelta(days=5),
            "ДатаОкончания": today,
        }
    )
