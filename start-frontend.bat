@echo off
echo Starting Hospital Management System - Frontend
echo ================================================
cd /d "%~dp0frontend"

echo Installing npm packages (first run may take a few minutes)...
call npm install

echo.
echo Frontend starting at http://localhost:4200
echo.

call npm start
pause
