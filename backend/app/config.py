import os
import sys
import glob

# Execution Mode: "local" (standalone CPU simulation) or "cloud" (Cloud GPU + CARLA server)
EXECUTION_MODE = os.getenv("EXECUTION_MODE", "local").lower()

# Optional CARLA Installation Root directory on Device 2 (e.g., C:\CARLA_0.9.16)
CARLA_ROOT = os.getenv("CARLA_ROOT", "")

# If CARLA_ROOT is specified and carla is not yet imported, check PythonAPI/carla/dist
if CARLA_ROOT and os.path.isdir(CARLA_ROOT):
    dist_dir = os.path.join(CARLA_ROOT, "PythonAPI", "carla", "dist")
    if os.path.isdir(dist_dir):
        # Look for matching .whl or .egg files in CARLA's dist folder
        py_ver = f"py{sys.version_info.major}.{sys.version_info.minor}"
        py_ver_compact = f"cp{sys.version_info.major}{sys.version_info.minor}"
        packages = (
            glob.glob(os.path.join(dist_dir, f"*{py_ver}*.egg")) +
            glob.glob(os.path.join(dist_dir, f"*{py_ver_compact}*.whl")) +
            glob.glob(os.path.join(dist_dir, "*.egg"))
        )
        for pkg in packages:
            if pkg not in sys.path:
                sys.path.append(pkg)

# Default GPS location (Bangalore Center / Tech Hub default, fully configurable)
DEFAULT_LATITUDE = float(os.getenv("GPS_ORIGIN_LAT", "12.971820"))
DEFAULT_LONGITUDE = float(os.getenv("GPS_ORIGIN_LON", "77.594003"))

# Response Time Windows
DEMO_RESPONSE_TIME_SECONDS = int(os.getenv("DEMO_RESPONSE_TIME_SECONDS", "10"))
PROD_RESPONSE_TIME_SECONDS = int(os.getenv("PROD_RESPONSE_TIME_SECONDS", "60"))

# CARLA connection parameters
CARLA_HOST = os.getenv("CARLA_HOST", "127.0.0.1")
CARLA_PORT = int(os.getenv("CARLA_PORT", "2000"))
CARLA_TIMEOUT = float(os.getenv("CARLA_TIMEOUT", "10.0"))

# CARLA Autonomous Navigation Look-Ahead Parameters
NAV_LOOKAHEAD_MIN = float(os.getenv("NAV_LOOKAHEAD_MIN", "4.0"))    # Min look-ahead distance in meters (low speed)
NAV_LOOKAHEAD_MAX = float(os.getenv("NAV_LOOKAHEAD_MAX", "12.0"))   # Max look-ahead distance in meters (high speed)
NAV_WAYPOINT_RADIUS = float(os.getenv("NAV_WAYPOINT_RADIUS", "2.0")) # Target waypoint acceptance radius in meters
NAV_MAX_SPEED_KMH = float(os.getenv("NAV_MAX_SPEED_KMH", "45.0"))   # Max autonomous speed in km/h

# Overpass API endpoints for fallback redundancy
OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
]

# OSRM router endpoint
OSRM_BASE_URL = os.getenv("OSRM_BASE_URL", "http://router.project-osrm.org/route/v1/driving")

# Speed constants (km/h)
NORMAL_SPEED_KMH = 60.0
PULLOVER_SPEED_KMH = 15.0
AUTONOMOUS_NAV_SPEED_KMH = 45.0
