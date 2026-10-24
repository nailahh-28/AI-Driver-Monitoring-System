import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from modules.vehicle_control.vehicle_state import VehicleState
from modules.vehicle_control.emergency_controller import (
    EmergencyController
)

from modules.gps.gps_service import GPSService

from modules.hospital.hospital_finder import (
    HospitalFinder
)

from modules.routing.route_planner import (
    RoutePlanner
)


def main():

    print("\n")
    print("=" * 70)
    print("       AI DRIVER MONITORING & EMERGENCY SYSTEM")
    print("=" * 70)

    # =========================================================
    # 1. VEHICLE
    # =========================================================

    vehicle = VehicleState()

    vehicle.speed_kmh = 60

    # =========================================================
    # 2. GPS
    # =========================================================

    gps = GPSService()

    # Bengaluru
    gps.set_location(
        latitude=12.9716,
        longitude=77.5946
    )

    location = gps.get_location()

    print("\n📍 VEHICLE LOCATION")

    print(location)

    # =========================================================
    # 3. EMERGENCY CONTROLLER
    # =========================================================

    controller = EmergencyController(vehicle)

    # Use 10 seconds for testing
    result = controller.execute_emergency_sequence(
        wait_seconds=10
    )

    # =========================================================
    # 4. CHECK AUTONOMOUS MODE
    # =========================================================

    if not vehicle.autonomous_mode:

        print(
            "\n🟢 Driver responded."
        )

        return

    # =========================================================
    # 5. FIND NEAREST HOSPITAL
    # =========================================================

    print("\n")
    print("=" * 70)
    print("SEARCHING FOR NEAREST HOSPITAL")
    print("=" * 70)

    hospital_finder = HospitalFinder()

    hospital = (
        hospital_finder.find_nearest_hospital(
            location.latitude,
            location.longitude
        )
    )

    if hospital is None:

        print(
            "\n❌ Could not find a hospital."
        )

        return

    print("\n🏥 NEAREST HOSPITAL")

    print(hospital)

    # =========================================================
    # 6. STORE DESTINATION
    # =========================================================

    vehicle.destination_name = hospital.name

    vehicle.destination_latitude = (
        hospital.latitude
    )

    vehicle.destination_longitude = (
        hospital.longitude
    )

    # =========================================================
    # 7. ROUTE PLANNER
    # =========================================================

    print("\n")
    print("=" * 70)
    print("CALCULATING HOSPITAL ROUTE")
    print("=" * 70)

    planner = RoutePlanner()

    route = planner.get_route(
        start_latitude=location.latitude,
        start_longitude=location.longitude,
        destination_latitude=hospital.latitude,
        destination_longitude=hospital.longitude
    )

    # =========================================================
    # 8. FINAL RESULT
    # =========================================================

    print("\n")
    print("=" * 70)
    print("EMERGENCY NAVIGATION READY")
    print("=" * 70)

    print(
        f"\n🚗 Mode: "
        f"{vehicle.mode.value}"
    )

    print(
        f"🏥 Destination: "
        f"{vehicle.destination_name}"
    )

    print(
        f"📍 Destination: "
        f"{vehicle.destination_latitude}, "
        f"{vehicle.destination_longitude}"
    )

    print(
        f"🛣️ Distance: "
        f"{route.distance_km:.2f} km"
    )

    print(
        f"⏱️ Estimated time: "
        f"{route.duration_minutes:.1f} minutes"
    )

    print(
        f"🗺️ Route points: "
        f"{len(route.points)}"
    )

    print("\n✅ PHASE 6 COMPLETE.")


if __name__ == "__main__":
    main()
