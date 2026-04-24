@echo off
cd /d "%~dp0"
echo ========================================
echo Open 3D FEA Result Viewer
echo ========================================

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found.
    echo Please run 00_create_venv.bat first.
    pause
    exit /b 1
)

if not exist "results\3d_cantilever_result.vtu" (
    echo [ERROR] Result file not found.
    echo Please run 02_run_analysis.bat first.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m src.open_result_viewer

pause
