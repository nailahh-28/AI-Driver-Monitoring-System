import math
import logging
from typing import List, Tuple, Optional, Dict
from backend.app.config import (
    NAV_LOOKAHEAD_MIN, NAV_LOOKAHEAD_MAX, NAV_WAYPOINT_RADIUS, NAV_MAX_SPEED_KMH
)
from modules.gps.gps_service import gps_service

logger = logging.getLogger(__name__)

CARLA_AVAILABLE = False
try:
    import carla
    CARLA_AVAILABLE = True
except ImportError:
    carla = None


class CarlaLookAheadController:
    """Pure Pursuit Look-Ahead Vehicle Controller for CARLA Road Networks (Zero Teleportation)."""

    def __init__(self):
        self.carla_waypoints: List[Any] = []
        self.current_index: int = 0

    def generate_carla_road_waypoints(self, world, route_gps_coords: List[Tuple[float, float]]) -> List[Any]:
        """Converts GPS route coordinates to CARLA road waypoints snapped to valid driving lanes."""
        if not CARLA_AVAILABLE or not world:
            return []

        carla_map = world.get_map()
        road_waypoints = []

        for lat, lng in route_gps_coords:
            cx, cy = gps_service.gps_to_carla(lat, lng)
            location = carla.Location(x=cx, y=cy, z=0.5)
            
            # Snap coordinate to closest driving lane waypoint on CARLA road network
            waypoint = carla_map.get_waypoint(
                location,
                project_to_road=True,
                lane_type=carla.LaneType.Driving
            )
            
            if waypoint:
                road_waypoints.append(waypoint)

        self.carla_waypoints = road_waypoints
        self.current_index = 0
        logger.info(f"Generated {len(road_waypoints)} CARLA road network waypoints with lane projection.")
        return road_waypoints

    def compute_control(self, vehicle, current_speed_kmh: float) -> Tuple[float, float, float, bool]:
        """Calculates throttle, brake, and steering inputs to follow CARLA road waypoints without teleportation.

        Returns: (throttle, brake, steer, destination_reached)
        """
        if not CARLA_AVAILABLE or not vehicle or not self.carla_waypoints:
            return 0.0, 1.0, 0.0, False

        v_transform = vehicle.get_transform()
        v_loc = v_transform.location
        v_yaw = math.radians(v_transform.rotation.yaw)

        # Dynamic look-ahead distance scaled by current speed
        speed_factor = min(1.0, max(0.0, current_speed_kmh / NAV_MAX_SPEED_KMH))
        lookahead_dist = NAV_LOOKAHEAD_MIN + speed_factor * (NAV_LOOKAHEAD_MAX - NAV_LOOKAHEAD_MIN)

        # Advance current waypoint index if vehicle is within acceptance radius
        while self.current_index < len(self.carla_waypoints):
            target_wp_loc = self.carla_waypoints[self.current_index].transform.location
            dist_to_wp = v_loc.distance(target_wp_loc)
            if dist_to_wp < NAV_WAYPOINT_RADIUS:
                self.current_index += 1
            else:
                break

        # Check if route completed
        if self.current_index >= len(self.carla_waypoints):
            logger.info("CARLA Look-Ahead Controller: Destination Hospital Reached!")
            return 0.0, 1.0, 0.0, True

        # Find look-ahead target waypoint along path
        target_wp_loc = self.carla_waypoints[self.current_index].transform.location
        for idx in range(self.current_index, len(self.carla_waypoints)):
            wp_loc = self.carla_waypoints[idx].transform.location
            if v_loc.distance(wp_loc) >= lookahead_dist:
                target_wp_loc = wp_loc
                break

        # Calculate target vector & local steering angle
        dx = target_wp_loc.x - v_loc.x
        dy = target_wp_loc.y - v_loc.y
        target_angle = math.atan2(dy, dx)

        heading_diff = target_angle - v_yaw
        # Normalize angle to [-pi, pi]
        heading_diff = math.atan2(math.sin(heading_diff), math.cos(heading_diff))

        # Steering calculation with gain
        steer = max(-1.0, min(1.0, heading_diff * 1.2))

        # Throttle & Brake Speed Control
        target_speed = NAV_MAX_SPEED_KMH
        # Slow down during sharp turns
        if abs(steer) > 0.3:
            target_speed *= 0.6

        if current_speed_kmh < target_speed:
            throttle = max(0.2, min(0.75, (target_speed - current_speed_kmh) / 10.0))
            brake = 0.0
        else:
            throttle = 0.0
            brake = max(0.1, min(0.6, (current_speed_kmh - target_speed) / 10.0))

        # Apply physical VehicleControl to CARLA vehicle actor (Zero Teleportation)
        control = carla.VehicleControl(
            throttle=float(throttle),
            steer=float(steer),
            brake=float(brake)
        )
        vehicle.apply_control(control)

        return throttle, brake, steer, False


carla_lookahead_controller = CarlaLookAheadController()
