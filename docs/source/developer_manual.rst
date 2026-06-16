Руководство разработчика
=========================

Настройка среды разработки
---------------------------

1. Установите Python 3.9 или выше с официального сайта https://python.org
2. Клонируйте репозиторий проекта::

      git clone <url_репозитория>
      cd ContractAccounting_new

3. Создайте и активируйте виртуальное окружение::

      python -m venv .venv
      .venv\Scripts\activate

4. Установите зависимости::

      pip install -r requirements.txt

Настройка базы данных
---------------------

1. Установите MS SQL Server Express.
2. Создайте базу данных ``ContractAccounting``.
3. Откройте файл ``config.py`` и укажите параметры подключения::

      DB_SERVER = 'localhost'
      DB_NAME = 'ContractAccounting'
      DB_USER = 'sa'
      DB_PASSWORD = 'ваш_пароль'

4. Выполните скрипт создания таблиц::

      python database/create_tables.py

Запуск приложения
-----------------

::

   python main.py

Запуск тестов
-------------

::

   pytest tests/

Для просмотра подробного вывода::

   pytest tests/ -v

Сборка исполняемого файла
--------------------------

::

   pyinstaller --onefile --windowed main.py

Готовый файл появится в папке ``dist/``.

Структура проекта
-----------------

::

   ContractAccounting_new/
   ├── main.py