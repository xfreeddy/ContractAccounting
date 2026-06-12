"""
Модели данных SQLAlchemy.
Определяют структуру таблиц базы данных и связи между ними.
"""

from sqlalchemy import Column, Integer, String, Date, DECIMAL, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    """
    Модель пользователя системы.

    Attributes:
        КодПользователя: Первичный ключ.
        ИмяПользователя: Уникальное имя для входа.
        ХешПароля: Хешированный пароль (bcrypt).
        Роль: Роль пользователя (Администратор/Менеджер).
    """

    __tablename__ = "Пользователи"

    КодПользователя = Column(Integer, primary_key=True, autoincrement=True)
    ИмяПользователя = Column(String(50), unique=True, nullable=False)
    ХешПароля = Column(String(255), nullable=False)
    Роль = Column(String(20), nullable=False)


class Counterparty(Base):
    """
    Модель контрагента.

    Attributes:
        КодКонтрагента: Первичный ключ.
        Наименование: Название организации или ФИО.
        ИНН: Уникальный идентификационный номер.
        КонтактныйТелефон: Телефон для связи.
    """

    __tablename__ = "Контрагенты"
    __table_args__ = {"implicit_returning": False}

    КодКонтрагента = Column(Integer, primary_key=True, autoincrement=True)
    Наименование = Column(String(255), nullable=False)
    ИНН = Column(String(12), unique=True, nullable=False)
    КонтактныйТелефон = Column(String(20))


class Contract(Base):
    """
    Модель договора.

    Attributes:
        КодДоговора: Первичный ключ.
        КодКонтрагента: Внешний ключ на таблицу Контрагенты.
        КодПользователя: Внешний ключ на таблицу Пользователи (автор).
        Наименование: Название/номер договора.
        ДатаНачала: Дата начала действия.
        ДатаОкончания: Дата окончания действия.
        Сумма: Сумма договора.
        ТипДоговора: Тип (Поставка, Услуги, Аренда, Подряд).
        Статус: Текущий статус (Активен, Истёк, Черновик).
        ПутьКФайлу: Путь к прикрепленному файлу.
    """

    __tablename__ = "Договоры"
    __table_args__ = {"implicit_returning": False}

    КодДоговора = Column(Integer, primary_key=True, autoincrement=True)
    КодКонтрагента = Column(
        Integer, ForeignKey("Контрагенты.КодКонтрагента"), nullable=False
    )
    КодПользователя = Column(
        Integer, ForeignKey("Пользователи.КодПользователя"), nullable=True
    )
    Наименование = Column(String(255), nullable=False)
    ДатаНачала = Column(Date, nullable=False)
    ДатаОкончания = Column(Date, nullable=False)
    Сумма = Column(DECIMAL(15, 2), nullable=False)
    ТипДоговора = Column(String(50), nullable=False)
    Статус = Column(String(20), default="Активен")
    ПутьКФайлу = Column(String(500))
