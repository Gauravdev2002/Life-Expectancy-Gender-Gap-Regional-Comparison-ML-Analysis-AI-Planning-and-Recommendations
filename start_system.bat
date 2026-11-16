@echo off
title HealthIQ Intelligence System - Launcher
echo ========================================================
echo   Launching HealthIQ Intelligence System
echo   FastAPI Backend (Port 8000) ^& React Frontend (Port 5173)
echo ========================================================
echo.

echo [1/2] Starting FastAPI Backend on http://localhost:8000 ...
start "HealthIQ - Backend (FastAPI)" cmd /k "cd /d "%~dp0backend" && venv\Scripts\python -m uvicorn main:app --reload --port 8000"

echo [2/2] Starting React Frontend on http://localhost:5173 ...
start "HealthIQ - Frontend (Vite)" cmd /k "cd /d "%~dp0frontend" && npm run dev -- --host 0.0.0.0 --port 5173"

echo.
echo Both servers are launching!
echo Opening browser at http://localhost:5173 ...
timeout /t 3 >nul
start http://localhost:5173
echo Done!
pause
