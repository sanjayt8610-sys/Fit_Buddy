@echo off
title FitBuddy - AI Fitness Plan Generator
echo =======================================================
echo   FITBUDDY - AI Fitness Plan Generator
echo =======================================================
echo.

cd /d "%~dp0"

if exist ".venv\Scripts\activate.bat" (
    goto activate_env
)

echo [1/3] Setting up Python virtual environment...
if exist "C:\Users\%USERNAME%\.local\bin\python3.11.exe" (
    "C:\Users\%USERNAME%\.local\bin\python3.11.exe" -m venv .venv
) else (
    python -m venv .venv
)

:activate_env
echo [2/3] Activating virtual environment & checking dependencies...
call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt --quiet

if not exist ".env" (
    echo [2.5/3] Creating .env from .env.example...
    copy .env.example .env
)

echo [3/3] Starting FitBuddy application on http://127.0.0.1:8000 ...
echo.
echo =======================================================
echo   Application is LIVE at:
echo   - Web App:            http://127.0.0.1:8000
echo   - Admin Portal:       http://127.0.0.1:8000/admin/login
echo   - Swagger API Docs:   http://127.0.0.1:8000/docs
echo =======================================================
echo.

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause
