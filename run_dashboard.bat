@echo off
setlocal EnableDelayedExpansion

REM ============================================================
REM  AI Driver Monitoring System — Run Dashboard (Windows)
REM  Starts both the FastAPI backend and the Vite dev server
REM  in separate windows, then opens the browser.
REM ============================================================

echo.
echo ============================================================
echo  AI Driver Monitoring System — Starting Dashboard
echo ============================================================
echo.

REM ── Check venv exists ────────────────────────────────────────
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found.
    echo         Run setup.bat first to set up the project.
    exit /b 1
)

REM ── Check node_modules exists ────────────────────────────────
if not exist "frontend\node_modules" (
    echo [ERROR] Frontend node_modules not found.
    echo         Run setup.bat first to set up the project.
    exit /b 1
)

REM ── Start FastAPI backend in a new window ────────────────────
echo [STEP] Starting FastAPI backend on http://localhost:8000 ...
start "AI-Driver-Backend" cmd /k "call .venv\Scripts\activate.bat && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

REM ── Wait briefly for backend to start ────────────────────────
timeout /t 3 /nobreak >nul

REM ── Start Vite frontend dev server in a new window ───────────
echo [STEP] Starting Vite frontend on http://localhost:5173 ...
start "AI-Driver-Frontend" cmd /k "cd frontend && npm run dev"

REM ── Wait for frontend to spin up ─────────────────────────────
timeout /t 4 /nobreak >nul

REM ── Open browser ─────────────────────────────────────────────
echo [STEP] Opening dashboard in default browser...
start "" "http://localhost:5173"

echo.
echo ============================================================
echo  Dashboard is running!
echo   Backend  : http://localhost:8000
echo   Frontend : http://localhost:5173
echo   API Docs : http://localhost:8000/docs
echo.
echo  Close the two console windows to stop the servers.
echo ============================================================
echo.
endlocal
