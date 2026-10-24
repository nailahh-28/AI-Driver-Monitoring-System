#!/usr/bin/env bash
# ============================================================
#  AI Driver Monitoring System — Run Dashboard (Linux / macOS)
#  Starts the FastAPI backend and Vite dev server, then opens
#  the browser automatically.
# ============================================================
set -euo pipefail

COLOR_OK="\033[0;32m"
COLOR_ERR="\033[0;31m"
COLOR_INFO="\033[0;34m"
COLOR_RESET="\033[0m"

ok()   { echo -e "${COLOR_OK}[OK]${COLOR_RESET}   $*"; }
err()  { echo -e "${COLOR_ERR}[ERROR]${COLOR_RESET} $*" >&2; exit 1; }
info() { echo -e "${COLOR_INFO}[STEP]${COLOR_RESET} $*"; }

echo ""
echo "============================================================"
echo " AI Driver Monitoring System — Starting Dashboard"
echo "============================================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Check venv exists ─────────────────────────────────────────
if [ ! -f ".venv/bin/activate" ]; then
    err "Virtual environment not found. Run ./setup.sh first."
fi

# ── Check node_modules exists ─────────────────────────────────
if [ ! -d "frontend/node_modules" ]; then
    err "Frontend node_modules not found. Run ./setup.sh first."
fi

# ── Activate venv ─────────────────────────────────────────────
# shellcheck disable=SC1091
source .venv/bin/activate

# ── Cleanup handler: kill child processes on Ctrl+C ───────────
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    echo ""
    echo "Shutting down servers..."
    [ -n "$BACKEND_PID" ]  && kill "$BACKEND_PID"  2>/dev/null || true
    [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null || true
    wait 2>/dev/null || true
    echo "Done. Goodbye."
    exit 0
}
trap cleanup INT TERM

# ── Start FastAPI backend ─────────────────────────────────────
info "Starting FastAPI backend on http://localhost:8000 ..."
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
ok "Backend started (PID $BACKEND_PID)"

# ── Wait for backend to be ready ─────────────────────────────
sleep 3

# ── Start Vite frontend dev server ────────────────────────────
info "Starting Vite frontend on http://localhost:5173 ..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..
ok "Frontend started (PID $FRONTEND_PID)"

# ── Wait for frontend to spin up ─────────────────────────────
sleep 4

# ── Open browser (best-effort, non-blocking) ──────────────────
info "Opening dashboard in default browser..."
if command -v xdg-open &>/dev/null; then
    xdg-open "http://localhost:5173" &>/dev/null &
elif command -v open &>/dev/null; then           # macOS
    open "http://localhost:5173"
fi

echo ""
echo "============================================================"
echo " Dashboard is running!"
echo "  Backend  : http://localhost:8000"
echo "  Frontend : http://localhost:5173"
echo "  API Docs : http://localhost:8000/docs"
echo ""
echo "  Press Ctrl+C to stop both servers."
echo "============================================================"
echo ""

# ── Keep script alive until Ctrl+C ───────────────────────────
wait
