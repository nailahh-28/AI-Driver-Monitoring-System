import requests
from dataclasses import dataclass
from typing import List


@dataclass
class RoutePoint:

    latitude: float
    longitude: float


@dataclass
class Route:

    points: List[RoutePoint]
    distance_km: float
    duration_minutes: float

    def __str__(self):

        return (
            f"Route: "
            f"{len(self.points)} points | "
            f"{self.distance_km:.2f} km | "
            f"{self.duration_minutes:.1f} minutes"
        )


class RoutePlanner:

    def __init__(self):

        self.base_url = (
            "https://router.project-osrm.org"
        )

    # ---------------------------------------------------------
    # GET ROUTE
    # ---------------------------------------------------------

    def get_route(
        self,
        start_latitude,
        start_longitude,
        destination_latitude,
        destination_longitude
    ):

        url = (
            f"{self.base_url}/route/v1/driving/"
            f"{start_longitude},"
            f"{start_latitude};"
            f"{destination_longitude},"
            f"{destination_latitude}"
        )

        params = {
            "overview": "full",
            "geometries": "geojson"
        }

        headers = {
            "User-Agent":
                "AI-Driver-Monitoring-System/1.0"
        }

        print("\n🗺️ Calculating route...")

        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=15
            )

            response.raise_for_status()

            data = response.json()

            if data.get("code") == "Ok":
                route_data = data["routes"][0]

                coordinates = (
                    route_data["geometry"]["coordinates"]
                )

                points = []

                for longitude, latitude in coordinates:

                    points.append(
                        RoutePoint(
                            latitude=latitude,
                            longitude=longitude
                        )
                    )

                distance_km = (
                    route_data["distance"] / 1000
                )

                duration_minutes = (
                    route_data["duration"] / 60
                )

                route = Route(
                    points=points,
                    distance_km=distance_km,
                    duration_minutes=duration_minutes
                )

                print("✅ Route calculated.")

                print(route)

                return route

        except Exception as error:
            print(
                f"\n⚠️ OSRM routing service error: {error}"
                "\nGenerating direct emergency navigation trajectory..."
            )

        # Fallback interpolated emergency trajectory
        from math import radians, sin, cos, sqrt, atan2
        R = 6371.0
        lat1, lon1 = radians(start_latitude), radians(start_longitude)
        lat2, lon2 = radians(destination_latitude), radians(destination_longitude)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = (
            sin(dlat / 2) ** 2
            + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        )
        direct_dist = R * 2 * atan2(sqrt(a), sqrt(1 - a))

        steps = 10
        points = []
        for i in range(steps + 1):
            fraction = i / steps
            points.append(
                RoutePoint(
                    latitude=start_latitude + fraction * (destination_latitude - start_latitude),
                    longitude=start_longitude + fraction * (destination_longitude - start_longitude)
                )
            )

        est_duration = max(1.0, (direct_dist / 40.0) * 60.0)

        route = Route(
            points=points,
            distance_km=direct_dist,
            duration_minutes=est_duration
        )

        print("✅ Emergency trajectory generated.")
        print(route)
        return route
