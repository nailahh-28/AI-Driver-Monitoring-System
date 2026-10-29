import time
import logging
import threading
from typing import Optional
from backend.app.config import DEMO_RESPONSE_TIME_SECONDS, PROD_RESPONSE_TIME_SECONDS
from backend.app.models.schemas import DriverStatus, VehicleMode, SimulationMode
from backend.app.services.state_manager import state_manager
from modules.hospital.hospital_finder import hospital_finder
from modules.routing.osrm_router import osrm_router
from carla.carla_client_wrapper import carla_wrapper
from modules.carla.lookahead_controller import carla_lookahead_controller

logger = logging.getLogger(__name__)


class EmergencyController:
    """Orchestrates emergency sequence, slowdown stages, driver response countdown, and autonomous mode trigger."""

    def __init__(self):
        self.emergency_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()

    def start_emergency_sequence(self, demo_mode: bool = True, custom_response_time: Optional[int] = None):
        """Triggers the asynchronous emergency controller thread."""
        self.stop_emergency()  # Stop any prior running thread
        self.stop_event.clear()

        response_time = custom_response_time or (DEMO_RESPONSE_TIME_SECONDS if demo_mode else PROD_RESPONSE_TIME_SECONDS)

        self.emergency_thread = threading.Thread(
            target=self._run_emergency_sequence,
            args=(response_time,),
            daemon=True
        )
        self.emergency_thread.start()

    def stop_emergency(self):
        """Cancels running emergency sequence thread."""
        self.stop_event.set()
        if self.emergency_thread and self.emergency_thread.is_alive():
            self.emergency_thread.join(timeout=1.0)
        try:
            from modules.alert.whatsapp_alert import emergency_alert_service
            emergency_alert_service.reset_session()
        except Exception:
            pass

    def _run_emergency_sequence(self, response_time: int):
        logger.info(f"Emergency sequence initiated with {response_time}s response window.")
        
        # Stage 1: Emergency Detected
        state_manager.update_state(
            driver_status=DriverStatus.UNRESPONSIVE,
            driver_responsive=False,
            emergency_active=True,
            emergency_stage="EMERGENCY_DETECTED",
            vehicle_mode=VehicleMode.EMERGENCY,
            response_time_total=response_time,
            response_time_remaining=response_time
        )
        time.sleep(1.0)
        if self.stop_event.is_set():
            return

        # Stage 2: Vehicle Slowing Down (60 -> 50 -> 40 -> 30 -> 20 -> 10 km/h)
        state_manager.update_state(
            emergency_stage="SLOWING_DOWN",
            vehicle_mode=VehicleMode.SLOWING_DOWN
        )
        current_speed = state_manager.get_state().vehicle_speed
        for target_s in [50.0, 40.0, 30.0, 20.0, 10.0]:
            if self.stop_event.is_set() or state_manager.get_state().driver_responsive:
                return
            state_manager.update_state(vehicle_speed=target_s, target_speed=target_s)
            time.sleep(0.5)

        # Stage 3: Vehicle Pulling Over
        if self.stop_event.is_set() or state_manager.get_state().driver_responsive:
            return
        state_manager.update_state(
            emergency_stage="PULLING_OVER",
            vehicle_mode=VehicleMode.PULLING_OVER,
            vehicle_speed=15.0,
            target_speed=15.0
        )
        time.sleep(1.2)

        # Stage 4: Vehicle Stopped
        if self.stop_event.is_set() or state_manager.get_state().driver_responsive:
            return
        state_manager.update_state(
            emergency_stage="VEHICLE_STOPPED",
            vehicle_mode=VehicleMode.STOPPED,
            vehicle_speed=0.0,
            target_speed=0.0
        )
        time.sleep(0.8)

        # Stage 5: Family Alert Sent
        if self.stop_event.is_set() or state_manager.get_state().driver_responsive:
            return
        state_manager.update_state(
            emergency_stage="FAMILY_ALERT_SENT",
            family_alert_sent=True
        )
        time.sleep(0.5)

        # Stage 6: Driver Response Window (Countdown)
        state_manager.update_state(
            emergency_stage="WAITING_FOR_DRIVER",
            vehicle_mode=VehicleMode.WAITING_FOR_DRIVER
        )

        start_time = time.monotonic()
        while not self.stop_event.is_set():
            elapsed = time.monotonic() - start_time
            remaining = max(0, int(response_time - elapsed))
            
            state_manager.update_state(response_time_remaining=remaining)

            current_state = state_manager.get_state()
            if current_state.driver_responsive or current_state.driver_status == DriverStatus.DRIVER_RESPONDED:
                logger.info("Driver responded! Cancelling emergency sequence.")
                state_manager.update_state(
                    emergency_active=False,
                    emergency_stage="CANCELLED",
                    vehicle_mode=VehicleMode.NORMAL,
                    target_speed=60.0,
                    vehicle_speed=60.0,
                    driver_status=DriverStatus.NORMAL
                )
                return

            if remaining <= 0:
                logger.info("Driver response window expired. Activating Autonomous Emergency Mode.")
                break

            time.sleep(0.2)

        if self.stop_event.is_set():
            return

        # Stage 7: Activate Autonomous Emergency Mode
        self._activate_autonomous_emergency()

    def _activate_autonomous_emergency(self):
        """Finds nearest hospital, calculates OSRM route, and begins autonomous navigation."""
        state_manager.update_state(
            driver_status=DriverStatus.UNRESPONSIVE,
            driver_responsive=False,
            emergency_stage="AUTONOMOUS_MODE_ACTIVATED",
            vehicle_mode=VehicleMode.AUTONOMOUS_EMERGENCY,
            navigation_status="SEARCHING_HOSPITAL"
        )
        
        state = state_manager.get_state()
        logger.info(f"Finding nearest hospital for GPS ({state.gps_latitude}, {state.gps_longitude})...")
        
        # 1. Hospital Search
        hospital = hospital_finder.find_nearest_hospital(state.gps_latitude, state.gps_longitude)
        if hospital:
            state_manager.update_state(
                hospital_name=hospital.name,
                hospital_latitude=hospital.latitude,
                hospital_longitude=hospital.longitude,
                hospital_distance=hospital.distance_km,
                navigation_status="CALCULATING_ROUTE"
            )
            logger.info(f"Hospital found: {hospital.name} ({hospital.distance_km} km)")
        else:
            state_manager.update_state(navigation_status="HOSPITAL_SEARCH_FAILED")
            try:
                from modules.alert.whatsapp_alert import emergency_alert_service
                emergency_alert_service.trigger_alert_if_unresponsive()
            except Exception:
                pass
            return

        # 2. Route Planning
        route = osrm_router.get_route(
            start_lat=state.gps_latitude,
            start_lng=state.gps_longitude,
            dest_lat=hospital.latitude,
            dest_lng=hospital.longitude
        )

        state_manager.update_state(
            route_distance=route.distance_km,
            route_eta=route.duration_min,
            navigation_status="STARTING_NAVIGATION",
            vehicle_mode=VehicleMode.NAVIGATING_TO_HOSPITAL
        )

        # Convert route coordinates to dict format
        waypoints = [{"lat": pt[0], "lng": pt[1]} for pt in route.coordinates]
        state_manager.set_route_waypoints(waypoints)
        
        # If in CARLA Mode, project OSRM route points onto CARLA road network
        if state.mode == SimulationMode.CARLA and state.carla_connected and carla_wrapper.world:
            logger.info("Projecting OSRM route onto CARLA road network driving lanes...")
            carla_lookahead_controller.generate_carla_road_waypoints(carla_wrapper.world, route.coordinates)

        logger.info(f"Navigation started with {len(waypoints)} route waypoints.")

        # Dispatch Autonomous WhatsApp Emergency Alert to designated contact
        try:
            from modules.alert.whatsapp_alert import emergency_alert_service
            emergency_alert_service.trigger_alert_if_unresponsive()
        except Exception as e:
            logger.error(f"Error triggering emergency alert: {e}")


emergency_controller = EmergencyController()
