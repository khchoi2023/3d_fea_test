@echo off
cd /d "%~dp0"
echo ========================================
echo Run All - 3D Cantilever FEA Project
echo ========================================

if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Virtual environment not found. Creating .venv...
    python -m venv .venv
)

echo.
echo [INFO] Installing requirements...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo.
echo [INFO] Running analysis...
".venv\Scripts\python.exe" -m src.main

echo.
echo [INFO] Opening result viewer...
".venv\Scripts\python.exe" -m src.open_result_viewer

pause
