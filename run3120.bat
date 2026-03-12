@echo off
REM Change to the directory where this batch file is located
cd /d "%~dp0"

REM Check if manage.py exists
if not exist "manage.py" (
    echo Error: manage.py not found in current directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Starting Django development server...
echo.
python manage.py runserver

pause
