import math
from typing import Tuple
from backend.app.config import DEFAULT_LATITUDE, DEFAULT_LONGITUDE
from backend.app.services.state_manager import state_manager


class GpsService:
    """Manages vehicle GPS coordinates, distance calculations, and CARLA coordinate mapping."""

    def __init__(self, ref_lat: float = DEFAULT_LATITUDE, ref_lng: float = DEFAULT_LONGITUDE):
        self.ref_lat = ref_lat
        self.ref_lng = ref_lng
        # Conversion scale approximations near reference lat:
        # 1 deg latitude ≈ 111,000 meters
        # 1 deg longitude ≈ 111,000 * cos(lat) meters
        self.meters_per_lat_deg = 111000.0
        self.meters_per_lng_deg = 111000.0 * math.cos(math.radians(ref_lat))

    def get_current_location(self) -> Tuple[float, float]:
        state = state_manager.get_state()
        return state.gps_latitude, state.gps_longitude

    def update_location(self, lat: float, lng: float):
        state_manager.update_state(gps_latitude=round(lat, 6), gps_longitude=round(lng, 6))

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates spherical distance between two points in kilometers."""
        R = 6371.0  # Earth radius in kilometers
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def carla_to_gps(self, carla_x: float, carla_y: float) -> Tuple[float, float]:
        """Converts CARLA local position (x, y in meters) to global (lat, lng)."""
        lat = self.ref_lat + (carla_y / self.meters_per_lat_deg)
        lng = self.ref_lng + (carla_x / self.meters_per_lng_deg)
        return round(lat, 6), round(lng, 6)

    def gps_to_carla(self, lat: float, lng: float) -> Tuple[float, float]:
        """Converts global (lat, lng) to CARLA local position (x, y in meters)."""
        carla_y = (lat - self.ref_lat) * self.meters_per_lat_deg
        carla_x = (lng - self.ref_lng) * self.meters_per_lng_deg
        return round(carla_x, 2), round(carla_y, 2)


gps_service = GpsService()

# Backward compatibility alias
GPSService = GpsService
