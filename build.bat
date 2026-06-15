@echo off
REM ============================================================
REM  Скрипт сборки исполняемого файла АС «Контракт-Учёт»
REM  Запускать из активированного виртуального окружения venv
REM ============================================================

echo [1/3] Активация виртуального окружения...
call venv\Scripts\activate

echo [2/3] Очистка предыдущей сборки...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [3/3] Сборка исполняемого файла через PyInstaller...
pyinstaller --noconfirm --onefile --windowed ^
    --name "ContractAccounting" ^
    --hidden-import=PySide6 ^
    --hidden-import=pyodbc ^
    --hidden-import=bcrypt ^
    main.py

echo.
echo ============================================================
echo  Готово. Исполняемый файл: dist\ContractAccounting.exe
echo ============================================================
pause
