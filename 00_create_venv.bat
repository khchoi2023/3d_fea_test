@echo off
cd /d "%~dp0"
echo ========================================
echo Create Python Virtual Environment
echo ========================================

python --version

if exist ".venv" (
    echo.
    echo [INFO] .venv already exists.
    echo If you want to recreate it, delete the .venv folder first.
) else (
    echo.
    echo [INFO] Creating .venv...
    python -m venv .venv
    echo [INFO] Virtual environment created.
)

pause
