"""Репозиторий для операций с базой данных (CRUD)."""

import uuid
import pyodbc
from sqlalchemy import create_engine, or_, text
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta
from .models import Base, Contract, Counterparty, User

# ========================================
# ПРЯМОЕ ПОДКЛЮЧЕНИЕ ЧЕРЕЗ PYODBC
# ========================================
SERVER = r"MOONXRCRY\SQLEXPRESS"
DATABASE = "УчётДоговоров2"

CONNECTION_STRING = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"Trusted_Connection=yes;"
)

try:
    # Тестовое подключение через pyodbc
    test_conn = pyodbc.connect(CONNECTION_STRING)
    test_conn.close()

    def get_connection():
        return pyodbc.connect(CONNECTION_STRING)

    engine = create_engine("mssql+pyodbc://", creator=get_connection, echo=False)
    SessionLocal = sessionmaker(bind=engine)
    DB_AVAILABLE = True
    print(f"✅ Подключение к базе данных '{DATABASE}' успешно установлено")
    print(f"🖥 Сервер: {SERVER}")
except Exception as e:
    print(f"⚠ Ошибка подключения к БД: {e}")
    print(f"⚠ Строка подключения: {CONNECTION_STRING}")
    print("⚠ Приложение будет работать в демо-режиме")
    DB_AVAILABLE = False


def test_connection():
    """Проверка подключения к базе данных."""
    if not DB_AVAILABLE:
        return False, "Движок БД не создан"
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        return True, "Подключение успешно"
    except Exception as e:
        return False, str(e)


class ContractRepository:
    """Репозиторий для работы с договорами."""

    @staticmethod
    def get_all_contracts():
        """Получить все договоры с информацией о контрагентах."""
        if not DB_AVAILABLE:
            return []
        try:
            with SessionLocal() as session:
                results = (
                    session.query(Contract, Counterparty.Наименование)
                    .join(
                        Counterparty,
                        Contract.КодКонтрагента == Counterparty.КодКонтрагента,
                    )
                    .all()
                )
                return results
        except Exception as e:
            print(f"Ошибка получения договоров: {e}")
            return []

    @staticmethod
    def create_contract(contract_data: dict):
        """Создать новый договор."""
        if not DB_AVAILABLE:
            return None
        try:
            with SessionLocal() as session:
                new_contract = Contract(**contract_data)
                session.add(new_contract)
                session.commit()
                # session.refresh не используем — несовместимо с implicit_returning=False
                return new_contract
        except Exception as e:
            print(f"Ошибка создания договора: {e}")
            return None

    @staticmethod
    def search_contracts(query: str):
        """Поиск договоров по названию или ИНН контрагента."""
        if not DB_AVAILABLE:
            return []
        try:
            with SessionLocal() as session:
                results = (
                    session.query(Contract, Counterparty.Наименование)
                    .join(
                        Counterparty,
                        Contract.КодКонтрагента == Counterparty.КодКонтрагента,
                    )
                    .filter(
                        or_(
                            Contract.Наименование.ilike(f"%{query}%"),
                            Counterparty.ИНН.ilike(f"%{query}%"),
                            Counterparty.Наименование.ilike(f"%{query}%"),
                        )
                    )
                    .all()
                )
                return results
        except Exception as e:
            print(f"Ошибка поиска: {e}")
            return []

    @staticmethod
    def delete_contract(contract_id: int):
        """Удалить договор по ID."""
        if not DB_AVAILABLE:
            return False
        try:
            with SessionLocal() as session:
                contract = (
                    session.query(Contract).filter_by(КодДоговора=contract_id).first()
                )
                if contract:
                    session.delete(contract)
                    session.commit()
                    return True
                return False
        except Exception as e:
            print(f"Ошибка удаления: {e}")
            return False

    @staticmethod
    def update_contract(contract_id: int, contract_data: dict):
        """Обновить договор."""
        if not DB_AVAILABLE:
            return False
        try:
            with SessionLocal() as session:
                contract = (
                    session.query(Contract).filter_by(КодДоговора=contract_id).first()
                )
                if contract:
                    for key, value in contract_data.items():
                        setattr(contract, key, value)
                    session.commit()
                    return True
                return False
        except Exception as e:
            print(f"Ошибка обновления: {e}")
            return False

    @staticmethod
    def get_expiring_contracts(days: int = 30):
        """Получить договоры, истекающие в ближайшие N дней."""
        if not DB_AVAILABLE:
            return []
        try:
            with SessionLocal() as session:
                today = date.today()
                future_date = today + timedelta(days=days)

                # Ищем договоры, которые истекают между сегодня и через N дней
                results = (
                    session.query(Contract, Counterparty.Наименование)
                    .join(
                        Counterparty,
                        Contract.КодКонтрагента == Counterparty.КодКонтрагента,
                    )
                    .filter(
                        Contract.ДатаОкончания >= today,  # Не истёкшие
                        Contract.ДатаОкончания
                        <= future_date,  # Истекают в ближайшие N дней
                        Contract.Статус == "Активен",
                    )
                    .all()
                )
                return results
        except Exception as e:
            print(f"Ошибка получения истекающих: {e}")
            return []


class CounterpartyRepository:
    """Репозиторий для работы с контрагентами."""

    @staticmethod
    def get_or_create(name: str, inn: str = "", phone: str = ""):
        """Получить контрагента по имени или создать нового."""
        if not DB_AVAILABLE:
            return None
        try:
            with SessionLocal() as session:
                counterparty = (
                    session.query(Counterparty).filter_by(Наименование=name).first()
                )
                if not counterparty:
                    # Если ИНН не передан — генерируем уникальный псевдо-ИНН
                    # чтобы не нарушать UNIQUE constraint на колонке ИНН
                    effective_inn = (
                        inn if inn else f"TEMP{uuid.uuid4().hex[:6].upper()}"
                    )
                    counterparty = Counterparty(
                        Наименование=name, ИНН=effective_inn, КонтактныйТелефон=phone
                    )
                    session.add(counterparty)
                    session.commit()
                    # refresh не используем — несовместимо с implicit_returning=False
                return counterparty
        except Exception as e:
            print(f"Ошибка работы с контрагентом: {e}")
            return None


class UserRepository:
    """Репозиторий для работы с пользователями."""

    @staticmethod
    def authenticate(username: str, password: str):
        """Проверить учётные данные пользователя."""
        if not DB_AVAILABLE:
            if username in ("admin", "manager") and password == "123":
                return {
                    "username": username,
                    "role": "Администратор" if username == "admin" else "Менеджер",
                }
            return None
        try:
            with SessionLocal() as session:
                user = (
                    session.query(User)
                    .filter_by(ИмяПользователя=username, ХешПароля=password)
                    .first()
                )
                if user:
                    return {"username": user.ИмяПользователя, "role": user.Роль}
                return None
        except Exception as e:
            print(f"Ошибка авторизации: {e}")
            return None
