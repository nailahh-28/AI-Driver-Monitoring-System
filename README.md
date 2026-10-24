# AI-Based Driver Monitoring & Automated Emergency Response System

A complete, runnable major project prototype simulating an intelligent autonomous vehicle system that:
1. Monitors the driver's condition.
2. Detects driver emergencies / unresponsiveness.
3. Provides a configurable response window with live countdown timer.
4. Allows the driver to respond using an on-screen button (`🟢 DRIVER RESPONDED`).
5. Cancels emergency if driver responds within the response window.
6. If the driver does **not** respond:
   - Activates Autonomous Emergency Mode.
   - Discovers the nearest hospital using OpenStreetMap / Overpass API with server redundancy.
   - Calculates real driving route to hospital using OSRM API.
   - Displays hospital name, distance, ETA, vehicle speed, and GPS coordinates.
   - Navigates the simulated vehicle along the road route toward the hospital until destination is reached.
7. Supports **CARLA Simulator 0.9.16** integration and includes a standalone **Offline Simulation Mode** fallback.

---

## 🏗️ Project Architecture & Directory Structure

```
AI-Driver-Monitoring-System/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app & WebSocket endpoint
│   │   ├── config.py            # Global system settings & defaults
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic state & API schemas
│   │   ├── routes/
│   │   │   └── api_routes.py    # REST & MJPEG camera stream endpoints
│   │   └── services/
│   │       └── state_manager.py # Thread-safe centralized state manager
├── modules/
│   ├── driver_monitoring/
│   │   └── driver_monitor.py    # Driver condition & response logic
│   ├── vehicle_control/
│   │   └── emergency_controller.py # Multi-stage emergency state machine
│   ├── gps/
│   │   └── gps_service.py       # GPS & Haversine distance calculator
│   ├── hospital/
│   │   └── hospital_finder.py   # Overpass OSM hospital search
│   ├── routing/
│   │   └── osrm_router.py       # OSRM road route planning
│   └── simulation/
│       └── simulation_engine.py # Physics loop & synthetic camera HUD
├── carla/
│   └── carla_client_wrapper.py  # CARLA 0.9.16 integration & actor lifecycle
├── frontend/
│   ├── src/
│   │   ├── components/          # Dashboard panels (Map, Speed Graph, Camera, etc.)
│   │   ├── pages/Dashboard.jsx  # Main Dark UI Dashboard workspace
│   │   ├── services/api.js      # Axios REST client
│   │   └── hooks/useWebSocket.js # Real-time telemetry hook
│   └── package.json
├── tests/                       # Python unit & integration tests
├── requirements.txt
└── README.md
```

---

## 📋 System Requirements & Stack

- **OS**: Windows / Linux / macOS
- **Backend**: Python 3.12+ (FastAPI, Requests, OpenCV, NumPy, Pytest, Uvicorn, WebSockets)
- **Frontend**: Node.js v18+ (React, Vite, Tailwind CSS, Leaflet, Recharts, Axios, Lucide React)
- **Simulator**: CARLA Simulator 0.9.16 (Optional; system operates in offline SIMULATION mode if CARLA is not running)

---

## ⚡ Quick Start & Setup Instructions

### 1. Backend Setup

```bash
# Navigate to project root
cd AI-Driver-Monitoring-System

# Create virtual environment (optional)
python -m venv .venv
.venv\Scripts\activate   # On Windows PowerShell / CMD

# Install dependencies
pip install -r requirements.txt
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node packages
npm install
```

---

## 🚀 Running the Application

### Step 1: Start Backend API Server

```bash
# From project root directory
uvicorn backend.app.main:app --reload --port 8000
```
*Backend API docs available at `http://localhost:8000/docs`.*

### Step 2: Start React Frontend Dashboard

```bash
# Open a new terminal window inside frontend/
cd frontend
npm run dev
```
*Access the React Dashboard in browser at `http://localhost:5173`.*

### Step 3: Optional - Run CARLA Simulator (CARLA Mode)

1. Launch `CarlaUE4.exe` (CARLA 0.9.16).
2. Ensure localhost port `2000` is open.
3. Click **Start Simulation** or toggle CARLA mode in the frontend dashboard.
4. *Note*: If CARLA is not running, the application automatically switches to **SIMULATION MODE**, displaying a synthetic 3D HUD camera feed and physics movement.

---

## 🧪 Acceptance Test Suite

### TEST A — Driver Responds (Emergency Cancelled)
1. Open dashboard at `http://localhost:5173`.
2. Click **Start Simulation**. Observe vehicle speed updating.
3. Click **Simulate Emergency**.
   - Vehicle mode changes: `EMERGENCY` -> `SLOWING_DOWN` -> `PULLING_OVER` -> `STOPPED`.
   - Family alert is sent (`📱 Emergency alert sent to family`).
   - Response window countdown starts (10 seconds demo window).
4. Click the green **🟢 DRIVER RESPONDED** button before timer reaches 0.
5. **Expected Result**:
   - Status updates to `CONFIRMED`.
   - Emergency is cancelled and vehicle returns to `NORMAL` mode.

### TEST B — Driver Does Not Respond (Autonomous Emergency Navigation)
1. Click **Simulate Emergency**.
2. Do **NOT** click the response button. Let the 10-second countdown reach `00`.
3. **Expected Result**:
   - Status updates to `UNRESPONSIVE`.
   - Mode changes to `🤖 AUTONOMOUS EMERGENCY MODE`.
   - Nearest hospital is queried via Overpass API (e.g. *Vydehi Superspeciality Hospital*).
   - Route is calculated via OSRM.
   - Interactive Leaflet map displays vehicle marker, hospital marker, and route line.
   - Vehicle navigates along road waypoints toward hospital.
   - Distance decreases in real time until reaching destination (`🏥 HOSPITAL REACHED - EMERGENCY COMPLETE`).

---

## 🧪 Running Automated Unit Tests

```bash
# Run test suite from project root
python -m unittest discover tests
```

---

## 📜 How the GPS -> Hospital -> OSRM -> Autonomous Navigation Pipeline Works

```
                        [ EMERGENCY TRIGGERED & TIMEOUT ]
                                       │
                                       ▼
                       1. Read Current GPS Coordinates
                                (Lat, Lng)
                                       │
                                       ▼
                     2. Query Overpass API (OSM)
                    Finds Hospitals within 10 km Radius
                   Calculates Haversine Distance & Ranks
                                       │
                                       ▼
                      3. Query OSRM Driving Router
                Computes Road Waypoints, Distance (km) & ETA
                                       │
                                       ▼
                     4. Autonomous Navigation Engine
            Translates Waypoints to CARLA / Simulated Movement
                Updates Speed & Distance dynamically
                                       │
                                       ▼
                           5. Destination Reached
```
