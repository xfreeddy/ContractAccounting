git --version
АС «Контракт-Учёт» — Система учёта договоров и контрактов

Установка
1. Установите Python 3.9+
2. Установите MS SQL Server Express и ODBC Driver 17
3. Создайте виртуальное окружение: `python -m venv venv`
4. Активируйте его: `venv\Scripts\activate`
5. Установите зависимости: `pip install -r requirements.txt`
6. Выполните скрипт `setup_db.sql` в SSMS для создания базы данных
7. Запустите приложение: `python main.py`

Тестовые учетные данные
Администратор: admin / 123
Менеджер: manager / 123