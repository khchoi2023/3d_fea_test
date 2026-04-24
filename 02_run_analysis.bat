@echo off
cd /d "%~dp0"
echo ========================================
echo Run 3D Cantilever FEA Analysis
echo ========================================

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found.
    echo Please run 00_create_venv.bat first.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m src.main

pause
