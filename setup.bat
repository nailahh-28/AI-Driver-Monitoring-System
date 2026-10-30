@echo off
setlocal EnableDelayedExpansion

REM ============================================================
REM  AI Driver Monitoring System — Windows Setup Script
REM  Run once to install all dependencies and build the frontend
REM ============================================================

echo.
echo ============================================================
echo  AI Driver Monitoring System — Setup (Windows)
echo ============================================================
echo.

REM ── Ensure Node and Python are in PATH ──────────────────────
set "PATH=C:\Program Files\nodejs;%APPDATA%\npm;%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"

REM ── Check Python ────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not on PATH.
    echo         Download from: https://www.python.org/downloads/
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo [OK] Found %%i

REM ── Check Node.js ───────────────────────────────────────────
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not on PATH.
    echo         Download from: https://nodejs.org/
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do echo [OK] Found Node.js %%i

REM ── Create virtual environment ───────────────────────────────
if not exist ".venv" (
    echo.
    echo [STEP] Creating Python virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        exit /b 1
    )
    echo [OK] Virtual environment created at .venv\
) else (
    echo [OK] Virtual environment already exists at .venv\
)

REM ── Activate venv and install Python dependencies ───────────
echo.
echo [STEP] Installing Python dependencies...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install Python dependencies.
    exit /b 1
)
echo [OK] Python dependencies installed.

REM ── Install frontend Node.js dependencies ───────────────────
echo.
echo [STEP] Installing frontend dependencies (call npm install)...
cd frontend
call npm install
if errorlevel 1 (
    echo [ERROR] call npm install failed.
    cd ..
    exit /b 1
)
echo [OK] Frontend dependencies installed.

REM ── Build frontend ───────────────────────────────────────────
echo.
echo [STEP] Building frontend (call npm run build)...
call npm run build
if errorlevel 1 (
    echo [ERROR] Frontend build failed.
    cd ..
    exit /b 1
)
cd ..
echo [OK] Frontend built successfully.

REM ── Verify core modules import cleanly ──────────────────────
echo.
echo [STEP] Verifying core Python module imports...
call .venv\Scripts\activate.bat
python -c "from backend.app.models.schemas import DriverStatus; from backend.app.services.state_manager import state_manager; print('[OK] Core modules verified.')"
if errorlevel 1 (
    echo [ERROR] Core module verification failed. Check your Python path.
    exit /b 1
)

echo.
echo ============================================================
echo  Setup complete!
echo  Run the dashboard with:  run_dashboard.bat
echo ============================================================
echo.
endlocal


