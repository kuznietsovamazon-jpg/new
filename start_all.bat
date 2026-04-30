@echo off
title Amazon Tracker Launcher
echo ====================================================
echo    LAUNCHING AMAZON COMPETITOR TRACKER SYSTEM
echo ====================================================

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed! Please install Python 3.10+ first.
    pause
    exit
)

echo [2/3] Installing dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies.
    pause
    exit
)

echo [3/3] Starting system components...
echo Launching Backend (Monitor)...
start "Amazon Monitor - BACKEND" cmd /k "python monitor.py"

echo Launching Frontend (Dashboard)...
start "Amazon Dashboard - FRONTEND" cmd /k "streamlit run app.py"

echo ====================================================
echo    SUCCESS! SYSTEM IS NOW RUNNING.
echo    - Monitor is running in a separate window.
echo    - Dashboard will open in your browser.
echo ====================================================
pause
