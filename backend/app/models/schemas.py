from enum import Enum
from typing import List, Optional, Tuple
from pydantic import BaseModel


class DriverStatus(str, Enum):
    NORMAL = "NORMAL"
    DROWSY = "DROWSY"
    FATIGUED = "FATIGUED"
    SERIOUS_EMERGENCY = "SERIOUS_EMERGENCY"
    UNRESPONSIVE = "UNRESPONSIVE"
    DRIVER_RESPONDED = "DRIVER_RESPONDED"


class VehicleMode(str, Enum):
    NORMAL = "NORMAL"
    EMERGENCY = "EMERGENCY"
    SLOWING_DOWN = "SLOWING_DOWN"
    PULLING_OVER = "PULLING_OVER"
    STOPPED = "STOPPED"
    WAITING_FOR_DRIVER = "WAITING_FOR_DRIVER"
    AUTONOMOUS_EMERGENCY = "AUTONOMOUS_EMERGENCY"
    NAVIGATING_TO_HOSPITAL = "NAVIGATING_TO_HOSPITAL"
    HOSPITAL_REACHED = "HOSPITAL_REACHED"


class SimulationMode(str, Enum):
    CARLA = "CARLA"
    SIMULATION = "SIMULATION"


class HospitalInfo(BaseModel):
    name: str
    latitude: float
    longitude: float
    distance_km: float
    address: Optional[str] = "Emergency Medical Service"
    amenity: Optional[str] = "hospital"


class RouteInfo(BaseModel):
    distance_km: float
    duration_min: float
    waypoints_count: int
    coordinates: List[Tuple[float, float]] = []  # List of [lat, lng]


class SpeedHistoryPoint(BaseModel):
    timestamp: float
    speed_kmh: float


class GpuStatusInfo(BaseModel):
    cuda_available: bool = False
    ai_device: str = "cpu"
    gpu_name: str = "None"
    vram_usage: str = "N/A"
    pytorch_version: str = "N/A"
    cuda_version: str = "N/A"


class HealthCheckResponse(BaseModel):
    backend: bool = True
    carla: bool = False
    gpu: bool = False
    ai_worker: bool = False
    camera: bool = False
    execution_mode: str = "local"


class SystemState(BaseModel):
    driver_status: DriverStatus = DriverStatus.NORMAL
    driver_responsive: bool = False
    emergency_active: bool = False
    emergency_stage: str = "INACTIVE"
    vehicle_mode: VehicleMode = VehicleMode.NORMAL
    vehicle_speed: float = 60.0  # km/h starting speed
    target_speed: float = 60.0
    gps_latitude: float = 12.971820
    gps_longitude: float = 77.594003
    hospital_name: Optional[str] = None
    hospital_latitude: Optional[float] = None
    hospital_longitude: Optional[float] = None
    hospital_distance: Optional[float] = None
    route_distance: Optional[float] = None
    route_eta: Optional[float] = None
    navigation_status: str = "IDLE"
    current_waypoint: int = 0
    total_waypoints: int = 0
    response_time_remaining: int = 0
    response_time_total: int = 10
    mode: SimulationMode = SimulationMode.SIMULATION
    execution_mode: str = "local"  # "local" or "cloud"
    carla_connected: bool = False
    camera_connected: bool = False
    family_alert_sent: bool = False
    vehicle_id: str = "CARLA-001"
    
    # Cloud & GPU Hardware Metrics
    cuda_available: bool = False
    ai_device: str = "cpu"
    gpu_name: str = "None"
    vram_usage: str = "N/A"
    ai_worker_status: str = "SIMULATION"
    carla_fps: float = 0.0
    camera_fps: float = 0.0
    ai_fps: float = 0.0
    
    last_updated: float = 0.0
    speed_history: List[SpeedHistoryPoint] = []


class EmergencyStartRequest(BaseModel):
    demo_mode: bool = True
    response_time: Optional[int] = None


class DriverRespondRequest(BaseModel):
    pass


class SimulationStartRequest(BaseModel):
    use_carla: bool = False
    execution_mode: Optional[str] = None
