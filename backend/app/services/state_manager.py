import time
import threading
from typing import Dict, Any, List, Tuple
from backend.app.models.schemas import SystemState, DriverStatus, VehicleMode, SimulationMode, SpeedHistoryPoint
from backend.app.config import DEFAULT_LATITUDE, DEFAULT_LONGITUDE, DEMO_RESPONSE_TIME_SECONDS


class StateManager:
    """Centralized, thread-safe state container for the AI Driver Monitoring System."""

    def __init__(self):
        self._lock = threading.Lock()
        self._state = SystemState(
            driver_status=DriverStatus.NORMAL,
            driver_responsive=False,
            emergency_active=False,
            emergency_stage="INACTIVE",
            vehicle_mode=VehicleMode.NORMAL,
            vehicle_speed=60.0,
            target_speed=60.0,
            gps_latitude=DEFAULT_LATITUDE,
            gps_longitude=DEFAULT_LONGITUDE,
            navigation_status="IDLE",
            response_time_remaining=0,
            response_time_total=DEMO_RESPONSE_TIME_SECONDS,
            mode=SimulationMode.SIMULATION,
            carla_connected=False,
            family_alert_sent=False,
            last_updated=time.time(),
            speed_history=[]
        )
        # Store route waypoints separately for simulation loop execution
        self.route_waypoints: List[Dict[str, float]] = []
        self.current_waypoint_index: int = 0

    def get_state(self) -> SystemState:
        with self._lock:
            return self._state.model_copy()

    def get_dict(self) -> Dict[str, Any]:
        with self._lock:
            return self._state.model_dump()

    def update_state(self, **kwargs):
        with self._lock:
            current_dict = self._state.model_dump()
            for key, value in kwargs.items():
                if hasattr(self._state, key):
                    current_dict[key] = value
            
            current_dict["last_updated"] = time.time()
            self._state = SystemState(**current_dict)
            
            # Maintain speed history buffer
            if "vehicle_speed" in kwargs:
                now = time.time()
                history = list(self._state.speed_history)
                history.append(SpeedHistoryPoint(timestamp=now, speed_kmh=round(float(kwargs["vehicle_speed"]), 1)))
                # Keep last 60 data points (~1 minute at 1Hz or ~6s at 10Hz)
                if len(history) > 60:
                    history = history[-60:]
                self._state.speed_history = history

    def set_route_waypoints(self, waypoints: List[Dict[str, float]]):
        with self._lock:
            self.route_waypoints = waypoints
            self.current_waypoint_index = 0

    def get_route_waypoints(self) -> Tuple[List[Dict[str, float]], int]:
        with self._lock:
            return list(self.route_waypoints), self.current_waypoint_index

    def increment_waypoint_index(self):
        with self._lock:
            self.current_waypoint_index += 1

    def reset(self):
        with self._lock:
            self._state = SystemState(
                driver_status=DriverStatus.NORMAL,
                driver_responsive=False,
                emergency_active=False,
                emergency_stage="INACTIVE",
                vehicle_mode=VehicleMode.NORMAL,
                vehicle_speed=60.0,
                target_speed=60.0,
                gps_latitude=DEFAULT_LATITUDE,
                gps_longitude=DEFAULT_LONGITUDE,
                hospital_name=None,
                hospital_latitude=None,
                hospital_longitude=None,
                hospital_distance=None,
                route_distance=None,
                route_eta=None,
                navigation_status="IDLE",
                response_time_remaining=0,
                response_time_total=DEMO_RESPONSE_TIME_SECONDS,
                mode=self._state.mode,
                carla_connected=self._state.carla_connected,
                family_alert_sent=False,
                last_updated=time.time(),
                speed_history=[]
            )
            self.route_waypoints = []
            self.current_waypoint_index = 0


# Global singleton instance
state_manager = StateManager()
