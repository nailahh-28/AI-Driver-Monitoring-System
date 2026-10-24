# Setup and Execution Guide on Device 2 (CARLA Device)

This guide walks you through setting up and running the transferred **AI-Based Driver Monitoring and Automated Emergency Response System** on **Device 2**, where CARLA 0.9.16 and Python 3.12 are installed.

---

## 📌 Prerequisites on Device 2

1. **Operating System**: Windows 10/11 (or Ubuntu 20.04/22.04 LTS)
2. **CARLA Simulator**: Version **0.9.16** (pre-installed)
3. **Python**: **Python 3.12** (x64)
4. **Node.js**: v18+ with `npm`
5. **GPU**: Dedicated GPU (NVIDIA GTX 1060 / RTX series or equivalent recommended for CARLA)

---

## 🚀 Step-by-Step Installation

### Step 1: Extract the Transferred Project
Extract `AI-Driver-Monitoring-System.zip` to your preferred workspace on Device 2, for example:
```cmd
C:\Projects\AI-Driver-Monitoring-System
```
Open a Command Prompt or PowerShell window in that directory:
```cmd
cd C:\Projects\AI-Driver-Monitoring-System
```

---

### Step 2: Confirm Python 3.12
Check your Python version:
```cmd
python --version
```
> [!IMPORTANT]
> CARLA 0.9.16 Python API requires **Python 3.12**. Ensure your terminal displays `Python 3.12.x`. If multiple Python versions are installed, use `py -3.12 --version`.

---

### Step 3: Create a Clean Virtual Environment
Create and activate an isolated virtual environment:
```cmd
python -m venv .venv
.venv\Scripts\activate
```
*(On PowerShell, run `.venv\Scripts\Activate.ps1`. If execution policies block scripts, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

---

### Step 4: Install the CARLA 0.9.16 Python API Wheel
Locate your CARLA 0.9.16 directory on Device 2 (e.g., `C:\CARLA_0.9.16` or `D:\CARLA_0.9.16`).

The CARLA wheel is located inside:
```
<CARLA_ROOT>\PythonAPI\carla\dist\
```
Look for:
`carla-0.9.16-cp312-cp312-win_amd64.whl` (or matching your exact CARLA build).

Install it into your activated virtual environment:
```cmd
pip install "<CARLA_ROOT>\PythonAPI\carla\dist\carla-0.9.16-cp312-cp312-win_amd64.whl"
```
*(Replace `<CARLA_ROOT>` with your actual CARLA path, e.g. `pip install "C:\CARLA_0.9.16\PythonAPI\carla\dist\carla-0.9.16-cp312-cp312-win_amd64.whl"`).*

---

### Step 5: Install Project Dependencies
With `.venv` activated, install the remaining requirements:
```cmd
pip install -r requirements.txt
```

---

### Step 6: Install Frontend Dependencies
Open a second terminal or navigate to the `frontend` folder:
```cmd
cd frontend
npm install
cd ..
```

---

### Step 7: Configure Environment Variables
Copy the template configuration:
```cmd
copy .env.example .env
```
Open `.env` in any text editor. If desired, specify your CARLA path:
```ini
EXECUTION_MODE=local
CARLA_ROOT=C:\CARLA_0.9.16
CARLA_HOST=127.0.0.1
CARLA_PORT=2000
DEMO_RESPONSE_TIME_SECONDS=10
```

---

## 🎮 Running the Simulation

### 1. Launch CARLA Simulator
Open a new terminal, navigate to your CARLA root directory, and launch the simulator:
```cmd
cd C:\CARLA_0.9.16
CarlaUE4.exe -quality-level=Low
```
*(Using `-quality-level=Low` provides higher framerates; remove it if you have a high-end GPU).*
Wait until the CARLA window opens and loads the town.

---

### 2. Verify Port 2000 & Python Connection
In PowerShell:
```powershell
Test-NetConnection -ComputerName 127.0.0.1 -Port 2000
```
Or test connection via Python:
```cmd
python -c "import carla; client = carla.Client('127.0.0.1', 2000); client.set_timeout(5.0); print('CARLA Version:', client.get_server_version())"
```
Expected output:
```
CARLA Version: 0.9.16
```

---

### 3. Start the Backend API
In your project root (with `.venv` activated):
```cmd
python -m uvicorn backend.app.main:app --reload --port 8000
```
Backend API will be running on `http://127.0.0.1:8000`.

---

### 4. Start the Frontend Dashboard
In another terminal, navigate to `frontend`:
```cmd
cd frontend
npm run dev
```
Open your browser and navigate to:
```
http://localhost:5173
```

---

## 🧪 Acceptance Test Scenarios

### TEST A — Driver Responds (Emergency Cancelled)
1. In the dashboard, click **Start Simulation**.
2. Verify vehicle status updates to `NORMAL` and begins driving.
3. Click **Simulate Emergency**.
   - Vehicle slows down dynamically (`60 -> 50 -> 40 -> 30 -> 20 -> 10 km/h`).
   - Vehicle pulls over and stops.
   - Family alert sent (`📱 Emergency alert sent to family`).
   - 10-second countdown window begins.
4. Click the green button: **🟢 DRIVER RESPONDED**.
5. **Expected**: Status changes to `CONFIRMED`, emergency is cancelled, and vehicle returns to `NORMAL` driving.

---

### TEST B — Driver Does Not Respond (Autonomous Hospital Navigation)
1. Click **Simulate Emergency**.
2. Do **NOT** click the response button. Let the countdown reach `00`.
3. **Expected**:
   - Status updates to `UNRESPONSIVE`.
   - `🤖 AUTONOMOUS EMERGENCY MODE` activates.
   - System queries nearest hospital via Overpass API (*Vydehi Superspeciality Hospital* or local match).
   - OSRM calculates the driving road route.
   - Interactive Leaflet map shows the route and vehicle position.
   - CARLA vehicle autonomously follows the road waypoints using real throttle, steering, and braking (**zero teleportation**).
   - Real-time vehicle camera streams follow-view.
   - When reaching destination: `🏥 HOSPITAL REACHED - EMERGENCY COMPLETE`.

---

## 🛠️ Troubleshooting on Device 2

| Issue | Cause | Fix |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'carla'` | The CARLA wheel was not installed in the virtual environment. | Run `pip install "<CARLA_ROOT>\PythonAPI\carla\dist\carla-0.9.16-cp312-cp312-win_amd64.whl"`. |
| `CARLA is not running on 127.0.0.1:2000` | CarlaUE4.exe is not started or blocked by Windows Firewall. | Start `CarlaUE4.exe` first and check that port 2000 is open. |
| `Python version mismatch / wheel error` | Attempting to install Python 3.12 wheel into Python 3.14 or 3.11. | Confirm `python --version` says 3.12. Use Python 3.12 to create `.venv`. |
| `Port 8000 already in use` | Another process is using port 8000. | Run `netstat -ano \| findstr :8000` to find the PID, or run uvicorn on port 8001: `python -m uvicorn backend.app.main:app --port 8001`. |
| `Simulation fallback mode activated` | CARLA server timed out or wasn't reachable. | System automatically falls back to offline simulation mode so demos never crash. Start CarlaUE4 and click **Start Simulation** to reconnect. |
