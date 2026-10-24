import logging
import requests
from typing import Optional, Dict, Any, List
from backend.app.config import OVERPASS_SERVERS
from backend.app.models.schemas import HospitalInfo
from modules.gps.gps_service import gps_service

logger = logging.getLogger(__name__)

# Realistic fallback hospitals around default GPS (Bangalore) if Overpass is down or un-routable
FALLBACK_HOSPITALS = [
    {
        "name": "Vydehi Superspeciality Hospital",
        "latitude": 12.968155,
        "longitude": 77.595042,
        "address": "Vittal Mallya Rd, Ashok Nagar",
        "amenity": "hospital"
    },
    {
        "name": "Fortis Hospital - Richmond Road",
        "latitude": 12.963400,
        "longitude": 77.599200,
        "address": "Richmond Rd, Shantala Nagar",
        "amenity": "hospital"
    },
    {
        "name": "Manipal Hospital Central",
        "latitude": 12.958500,
        "longitude": 77.648100,
        "address": "HAL Old Airport Rd",
        "amenity": "hospital"
    }
]


class HospitalFinder:
    """Finds nearest hospitals using OpenStreetMap / Overpass API with server redundancy & fallback."""

    def __init__(self, search_radius_meters: int = 10000):
        self.search_radius_meters = search_radius_meters

    def find_nearest_hospital(self, current_lat: float, current_lng: float) -> Optional[HospitalInfo]:
        """Queries Overpass API endpoints across redundant servers. Sorts by Haversine distance."""
        overpass_query = f"""
        [out:json][timeout:10];
        (
          node["amenity"="hospital"](around:{self.search_radius_meters},{current_lat},{current_lng});
          way["amenity"="hospital"](around:{self.search_radius_meters},{current_lat},{current_lng});
        );
        out center;
        """

        hospitals: List[Dict[str, Any]] = []

        for server in OVERPASS_SERVERS:
            try:
                logger.info(f"Querying Overpass server: {server}")
                response = requests.post(server, data={"data": overpass_query}, timeout=6.0)
                if response.status_code == 200:
                    data = response.json()
                    elements = data.get("elements", [])
                    for elem in elements:
                        tags = elem.get("tags", {})
                        name = tags.get("name") or tags.get("name:en") or "Emergency Hospital"
                        
                        # Get coordinates (node vs way center)
                        lat = elem.get("lat") or elem.get("center", {}).get("lat")
                        lng = elem.get("lon") or elem.get("center", {}).get("lon")
                        
                        if lat and lng:
                            dist_km = gps_service.haversine_distance(current_lat, current_lng, lat, lng)
                            hospitals.append({
                                "name": name,
                                "latitude": round(lat, 6),
                                "longitude": round(lng, 6),
                                "distance_km": round(dist_km, 2),
                                "address": tags.get("addr:street") or tags.get("address") or "Emergency Care",
                                "amenity": "hospital"
                            })
                    
                    if hospitals:
                        logger.info(f"Successfully retrieved {len(hospitals)} hospitals from {server}")
                        break
            except Exception as e:
                logger.warning(f"Overpass server {server} failed: {e}. Trying fallback server...")

        # If Overpass API returned results, sort and select nearest
        if hospitals:
            hospitals.sort(key=lambda h: h["distance_km"])
            nearest = hospitals[0]
            return HospitalInfo(**nearest)

        # Fallback if Overpass API is down / blocked by firewall / offline (BUG 5 & 6 fix)
        logger.info("Using fallback emergency hospital database...")
        fallback_list = []
        for fb in FALLBACK_HOSPITALS:
            dist_km = gps_service.haversine_distance(current_lat, current_lng, fb["latitude"], fb["longitude"])
            item = dict(fb)
            item["distance_km"] = round(dist_km, 2)
            fallback_list.append(item)
        
        fallback_list.sort(key=lambda h: h["distance_km"])
        return HospitalInfo(**fallback_list[0])


hospital_finder = HospitalFinder()
