@echo off
REM Change to the script's directory
cd /d "%~dp0"

REM Run Django development server
python manage.py runserver

pause
