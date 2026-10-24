#!/usr/bin/env bash
# ============================================================
#  AI Driver Monitoring System — Linux / macOS Setup Script
#  Run once to install all dependencies and build the frontend
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
echo " AI Driver Monitoring System — Setup (Linux / macOS)"
echo "============================================================"
echo ""

# ── Detect OS ─────────────────────────────────────────────────
OS="$(uname -s)"
ok "Detected OS: $OS"

# ── Check Python 3 ────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    err "python3 is not installed or not on PATH. Install it first."
fi
ok "Found $(python3 --version)"

# ── Check Node.js ─────────────────────────────────────────────
if ! command -v node &>/dev/null; then
    err "Node.js is not installed or not on PATH. Install from https://nodejs.org/"
fi
ok "Found Node.js $(node --version)"

# ── Create virtual environment ────────────────────────────────
if [ ! -d ".venv" ]; then
    info "Creating Python virtual environment..."
    python3 -m venv .venv
    ok "Virtual environment created at .venv/"
else
    ok "Virtual environment already exists at .venv/"
fi

# ── Activate venv ─────────────────────────────────────────────
# shellcheck disable=SC1091
source .venv/bin/activate

# ── Install Python dependencies ───────────────────────────────
info "Installing Python dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt
ok "Python dependencies installed."

# ── Install frontend dependencies ─────────────────────────────
info "Installing frontend dependencies (npm install)..."
cd frontend
npm install
ok "Frontend dependencies installed."

# ── Build frontend ────────────────────────────────────────────
info "Building frontend (npm run build)..."
npm run build
ok "Frontend built successfully."
cd ..

# ── Verify core module imports ────────────────────────────────
info "Verifying core Python module imports..."
python -c "
from backend.app.models.schemas import DriverStatus
from backend.app.services.state_manager import state_manager
print('[OK] Core modules verified.')
"

echo ""
echo "============================================================"
echo " Setup complete!"
echo " Run the dashboard with:  ./run_dashboard.sh"
echo "============================================================"
echo ""
