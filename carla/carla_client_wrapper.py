import time
import logging
import threading
from typing import Optional, Tuple, List
import numpy as np

from backend.app.config import CARLA_HOST, CARLA_PORT, CARLA_TIMEOUT

logger = logging.getLogger(__name__)

# Safe dynamic import of CARLA API to prevent crash on non-CARLA systems
CARLA_AVAILABLE = False
try:
    import carla
    CARLA_AVAILABLE = True
except ImportError:
    carla = None


class CarlaClientWrapper:
    """Wrapper for CARLA Simulator 0.9.16 Python API integration."""

    def __init__(self, host: str = CARLA_HOST, port: int = CARLA_PORT, timeout: float = CARLA_TIMEOUT):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.client = None
        self.world = None
        self.vehicle = None
        self.camera = None
        self.is_connected = False
        self.latest_camera_frame: Optional[np.ndarray] = None
        self.frame_lock = threading.Lock()
        
        # Telemetry metrics
        self.carla_fps: float = 0.0
        self.camera_fps: float = 0.0
        self._frame_count: int = 0
        self._fps_start_time: float = time.time()

    def connect(self, host: Optional[str] = None, port: Optional[int] = None) -> Tuple[bool, str]:
        """Attempts connection to CARLA simulator (supports local & remote host IPs)."""
        target_host = host or self.host
        target_port = port or self.port

        if not CARLA_AVAILABLE:
            self.is_connected = False
            return False, "CARLA Python API package ('carla') is not installed in current environment."

        try:
            logger.info(f"Connecting to CARLA simulator at {target_host}:{target_port}...")
            self.client = carla.Client(target_host, target_port)
            self.client.set_timeout(self.timeout)
            self.world = self.client.get_world()
            self.is_connected = True
            logger.info(f"Successfully connected to CARLA Simulator at {target_host}:{target_port}!")
            return True, f"Connected to CARLA Simulator at {target_host}:{target_port}."
        except Exception as e:
            self.is_connected = False
            error_msg = (
                f"CARLA is not running on {target_host}:{target_port}. "
                "Ensure CarlaUE4 server is running."
            )
            logger.warning(f"CARLA connection failed: {e}. {error_msg}")
            return False, error_msg

    def spawn_vehicle_and_camera(self) -> Tuple[bool, str]:
        """Spawns Tesla Model 3 and attaches third-person RGB camera sensor."""
        if not self.is_connected or not self.world:
            return False, "CARLA not connected."

        try:
            blueprint_library = self.world.get_blueprint_library()
            
            # Spawn Tesla Model 3
            vehicle_bp = blueprint_library.find("vehicle.tesla.model3")
            spawn_points = self.world.get_map().get_spawn_points()
            spawn_point = spawn_points[0] if spawn_points else carla.Transform()

            self.vehicle = self.world.try_spawn_actor(vehicle_bp, spawn_point)
            if not self.vehicle:
                return False, "Failed to spawn CARLA vehicle."

            # Spawn RGB camera: 1280x720, 90 deg FOV, third-person view
            camera_bp = blueprint_library.find("sensor.camera.rgb")
            camera_bp.set_attribute("image_size_x", "1280")
            camera_bp.set_attribute("image_size_y", "720")
            camera_bp.set_attribute("fov", "90")

            # Position camera behind (-5.5m) and above (+2.8m) vehicle, pitch down -15 deg
            camera_transform = carla.Transform(
                carla.Location(x=-5.5, z=2.8),
                carla.Rotation(pitch=-15)
            )

            self.camera = self.world.spawn_actor(
                camera_bp, camera_transform, attach_to=self.vehicle
            )
            self.camera.listen(self._on_camera_image)
            self._fps_start_time = time.time()
            self._frame_count = 0

            logger.info("Spawned Tesla Model 3 and third-person camera sensor in CARLA.")
            return True, "Vehicle and camera spawned in CARLA."
        except Exception as e:
            logger.error(f"Error spawning CARLA actors: {e}")
            return False, f"CARLA spawn error: {e}"

    def _on_camera_image(self, image):
        """Callback processing raw camera sensor frames."""
        try:
            array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
            array = np.reshape(array, (image.height, image.width, 4))
            bgr_array = array[:, :, :3]  # Extract RGB/BGR
            with self.frame_lock:
                self.latest_camera_frame = bgr_array
                
            self._frame_count += 1
            now = time.time()
            elapsed = now - self._fps_start_time
            if elapsed >= 1.0:
                self.camera_fps = round(self._frame_count / elapsed, 1)
                self.carla_fps = self.camera_fps
                self._frame_count = 0
                self._fps_start_time = now
        except Exception as e:
            logger.error(f"Camera frame process error: {e}")

    def get_latest_frame(self) -> Optional[np.ndarray]:
        with self.frame_lock:
            return self.latest_camera_frame.copy() if self.latest_camera_frame is not None else None

    def apply_control(self, throttle: float = 0.0, brake: float = 0.0, steer: float = 0.0):
        """Applies physical VehicleControl inputs (No Teleportation)."""
        if self.vehicle:
            control = carla.VehicleControl(
                throttle=max(0.0, min(1.0, throttle)),
                steer=max(-1.0, min(1.0, steer)),
                brake=max(0.0, min(1.0, brake))
            )
            self.vehicle.apply_control(control)

    def cleanup(self):
        """Safely destroys camera sensor and vehicle actors."""
        logger.info("Cleaning up CARLA actors...")
        if self.camera:
            try:
                self.camera.stop()
                self.camera.destroy()
            except Exception:
                pass
            self.camera = None

        if self.vehicle:
            try:
                self.vehicle.destroy()
            except Exception:
                pass
            self.vehicle = None

        self.is_connected = False


carla_wrapper = CarlaClientWrapper()
