@echo off
REM ============================================================
REM  Build script for AS "Kontrakt-Uchet" (ContractAccounting)
REM  Run from project root. Activated venv is not required.
REM ============================================================

set VENV_PYTHON=.venv\Scripts\python.exe

if not exist "%VENV_PYTHON%" (
    echo [ERROR] Virtual environment not found at .venv
    echo Create it first: python -m venv .venv
    pause
    exit /b 1
)

echo [1/4] Checking PyInstaller...
"%VENV_PYTHON%" -m PyInstaller --version >nul 2>nul
if errorlevel 1 (
    echo PyInstaller not found, installing...
    "%VENV_PYTHON%" -m pip install pyinstaller
)

echo [2/4] Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [3/4] Building executable with PyInstaller...
"%VENV_PYTHON%" -m PyInstaller --noconfirm --onefile --windowed --name ContractAccounting --hidden-import=PySide6 --hidden-import=pyodbc --hidden-import=bcrypt main.py

echo [4/4] Done.
echo ============================================================
echo  Executable created: dist\ContractAccounting.exe
echo ============================================================
pause
