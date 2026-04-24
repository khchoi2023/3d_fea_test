@echo off
cd /d "%~dp0"
echo ========================================
echo Install Requirements
echo ========================================

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found.
    echo Please run 00_create_venv.bat first.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo.
echo [INFO] Requirements installed successfully.
pause
