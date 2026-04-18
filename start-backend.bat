@echo off
echo Starting Hospital Management System - Backend
echo ================================================
cd /d "%~dp0backend"

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Backend starting at http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.

python run.py
pause
