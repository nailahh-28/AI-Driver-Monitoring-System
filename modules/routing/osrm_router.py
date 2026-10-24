import logging
import requests
from typing import Optional, List, Tuple
from backend.app.config import OSRM_BASE_URL
from backend.app.models.schemas import RouteInfo
from modules.gps.gps_service import gps_service

logger = logging.getLogger(__name__)


class OSRMRouter:
    """Calculates road driving routes using OSRM API with offline interpolation fallback."""

    def __init__(self):
        pass

    def get_route(self, start_lat: float, start_lng: float, dest_lat: float, dest_lng: float) -> RouteInfo:
        """Requests route geometry and metrics from OSRM driving service."""
        # OSRM expects coordinates as {longitude},{latitude}
        url = f"{OSRM_BASE_URL}/{start_lng},{start_lat};{dest_lng},{dest_lat}?overview=full&geometries=geojson&steps=true"
        
        try:
            logger.info(f"Querying OSRM route: {url}")
            response = requests.get(url, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                routes = data.get("routes", [])
                if routes:
                    primary_route = routes[0]
                    distance_meters = primary_route.get("distance", 0)
                    duration_seconds = primary_route.get("duration", 0)
                    
                    # OSRM geojson coordinates are [lng, lat] -> convert to [lat, lng]
                    raw_coords = primary_route.get("geometry", {}).get("coordinates", [])
                    formatted_coords: List[Tuple[float, float]] = [
                        (round(coord[1], 6), round(coord[0], 6)) for coord in raw_coords
                    ]

                    distance_km = round(distance_meters / 1000.0, 2)
                    duration_min = round(duration_seconds / 60.0, 1)

                    logger.info(f"OSRM Route computed: {distance_km} km, {duration_min} min, {len(formatted_coords)} waypoints.")
                    return RouteInfo(
                        distance_km=distance_km,
                        duration_min=duration_min,
                        waypoints_count=len(formatted_coords),
                        coordinates=formatted_coords
                    )
        except Exception as e:
            logger.warning(f"OSRM routing request failed: {e}. Generating interpolated route...")

        # Fallback offline route generation if OSRM is unreachable
        return self._generate_fallback_route(start_lat, start_lng, dest_lat, dest_lng)

    def _generate_fallback_route(self, start_lat: float, start_lng: float, dest_lat: float, dest_lng: float) -> RouteInfo:
        """Generates a smooth multi-point roadside waypoint path between start and destination."""
        num_points = 20
        coords: List[Tuple[float, float]] = []
        
        # Add slight curve / road jitter for realism
        for i in range(num_points + 1):
            t = i / float(num_points)
            lat = start_lat + t * (dest_lat - start_lat)
            lng = start_lng + t * (dest_lng - start_lng)
            
            # Add small orthogonal detour in middle to simulate city grid turn
            if 0.2 < t < 0.8:
                lat += 0.00015 * (1 - abs(t - 0.5) * 2)
            
            coords.append((round(lat, 6), round(lng, 6)))

        dist_km = gps_service.haversine_distance(start_lat, start_lng, dest_lat, dest_lng)
        # Assume average emergency speed 40 km/h -> duration = dist / 40 * 60 min
        eta_min = round((dist_km / 40.0) * 60.0, 1)

        return RouteInfo(
            distance_km=round(dist_km, 2),
            duration_min=max(eta_min, 0.5),
            waypoints_count=len(coords),
            coordinates=coords
        )


osrm_router = OSRMRouter()
