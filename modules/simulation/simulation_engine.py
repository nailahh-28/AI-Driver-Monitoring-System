import time
import math
import cv2
import logging
import threading
import numpy as np
from typing import Optional
from backend.app.config import DEFAULT_LATITUDE, DEFAULT_LONGITUDE, EXECUTION_MODE
from backend.app.models.schemas import VehicleMode, SimulationMode, DriverStatus
from backend.app.services.state_manager import state_manager
from modules.gps.gps_service import gps_service
from carla.carla_client_wrapper import carla_wrapper
from modules.carla.lookahead_controller import carla_lookahead_controller
from ai_worker.worker import ai_worker

logger = logging.getLogger(__name__)


class SimulationEngine:
    """Core physics and motion simulation loop supporting both standalone offline SIMULATION mode and CARLA mode."""

    def __init__(self):
        self.is_running = False
        self.sim_thread: Optional[threading.Thread] = None
        self.sim_lock = threading.Lock()
        self.canvas_angle = 0.0

    def start(self):
        """Starts the background simulation tick loop."""
        with self.sim_lock:
            if not self.is_running:
                self.is_running = True
                self.sim_thread = threading.Thread(target=self._sim_loop, daemon=True)
                self.sim_thread.start()
                logger.info("Simulation engine started.")

    def stop(self):
        """Stops the simulation loop."""
        with self.sim_lock:
            self.is_running = False
            if self.sim_thread and self.sim_thread.is_alive():
                self.sim_thread.join(timeout=1.0)
                logger.info("Simulation engine stopped.")

    def _sim_loop(self):
        """10Hz simulation update tick loop."""
        while self.is_running:
            try:
                state = state_manager.get_state()

                # Sync AI worker and GPU status
                ai_info = ai_worker.get_status()
                state_manager.update_state(
                    cuda_available=ai_info["cuda_available"],
                    ai_device=ai_info["ai_device"],
                    gpu_name=ai_info["gpu_name"],
                    vram_usage=ai_info["vram_usage"],
                    ai_fps=ai_info["inference_fps"],
                    ai_worker_status=ai_info["status"]
                )

                if state.mode == SimulationMode.CARLA and state.carla_connected:
                    self._step_carla(state)
                else:
                    self._step_offline_simulation(state)

                time.sleep(0.1)  # 10Hz tick
            except Exception as e:
                logger.error(f"Error in simulation loop: {e}")
                time.sleep(0.5)

    def _step_offline_simulation(self, state):
        """Updates simulated speed, position, and hospital navigation when offline."""
        curr_speed = state.vehicle_speed
        target_speed = state.target_speed

        # Smooth speed adjustment toward target speed
        if abs(curr_speed - target_speed) > 0.5:
            if curr_speed < target_speed:
                curr_speed = min(target_speed, curr_speed + 1.5)
            else:
                curr_speed = max(target_speed, curr_speed - 2.5)
        else:
            curr_speed = target_speed

        state_manager.update_state(vehicle_speed=round(curr_speed, 1))

        # Handle Autonomous Hospital Navigation
        if state.vehicle_mode == VehicleMode.NAVIGATING_TO_HOSPITAL:
            waypoints, curr_idx = state_manager.get_route_waypoints()
            
            if waypoints and curr_idx < len(waypoints):
                target_wp = waypoints[curr_idx]
                curr_lat = state.gps_latitude
                curr_lng = state.gps_longitude

                # Distance to current waypoint
                dist_to_wp = gps_service.haversine_distance(curr_lat, curr_lng, target_wp["lat"], target_wp["lng"])

                if dist_to_wp < 0.015:  # Within ~15m of waypoint -> target next
                    state_manager.increment_waypoint_index()
                    curr_idx += 1

                if curr_idx < len(waypoints):
                    next_wp = waypoints[curr_idx]
                    km_per_tick = (curr_speed / 3600.0) * 0.1
                    
                    bearing = math.atan2(
                        next_wp["lng"] - curr_lng,
                        next_wp["lat"] - curr_lat
                    )
                    
                    d_lat = (km_per_tick / 111.0) * math.cos(bearing)
                    d_lng = (km_per_tick / (111.0 * math.cos(math.radians(curr_lat)))) * math.sin(bearing)

                    new_lat = curr_lat + d_lat
                    new_lng = curr_lng + d_lng
                    
                    if state.hospital_latitude and state.hospital_longitude:
                        hospital_dist = gps_service.haversine_distance(
                            new_lat, new_lng, state.hospital_latitude, state.hospital_longitude
                        )
                        eta_min = round((hospital_dist / max(curr_speed, 20.0)) * 60.0, 1) if curr_speed > 0 else 0.0
                        
                        state_manager.update_state(
                            gps_latitude=round(new_lat, 6),
                            gps_longitude=round(new_lng, 6),
                            hospital_distance=round(hospital_dist, 2),
                            route_eta=eta_min,
                            current_waypoint=curr_idx + 1,
                            total_waypoints=len(waypoints),
                            navigation_status=f"NAVIGATING (WAYPOINT {curr_idx + 1}/{len(waypoints)})",
                            target_speed=45.0
                        )

                        # Check destination arrival
                        if hospital_dist <= 0.03 or curr_idx >= len(waypoints) - 1:
                            logger.info("Destination Hospital Reached!")
                            state_manager.update_state(
                                vehicle_mode=VehicleMode.HOSPITAL_REACHED,
                                navigation_status="HOSPITAL_REACHED",
                                vehicle_speed=0.0,
                                target_speed=0.0,
                                hospital_distance=0.0,
                                route_eta=0.0
                            )
            elif waypoints and curr_idx >= len(waypoints):
                state_manager.update_state(
                    vehicle_mode=VehicleMode.HOSPITAL_REACHED,
                    navigation_status="HOSPITAL_REACHED",
                    vehicle_speed=0.0,
                    target_speed=0.0,
                    hospital_distance=0.0,
                    route_eta=0.0
                )
        elif state.vehicle_mode == VehicleMode.NORMAL and curr_speed > 0:
            km_per_tick = (curr_speed / 3600.0) * 0.1
            d_lng = (km_per_tick / 111.0) * 0.5
            state_manager.update_state(
                gps_longitude=round(state.gps_longitude + d_lng, 6)
            )

    def _step_carla(self, state):
        """CARLA mode vehicle telemetry update using Look-Ahead Steering & Throttle control (No Teleportation)."""
        if carla_wrapper.vehicle:
            try:
                v = carla_wrapper.vehicle.get_velocity()
                speed_mps = math.sqrt(v.x**2 + v.y**2 + v.z**2)
                speed_kmh = speed_mps * 3.6
                
                transform = carla_wrapper.vehicle.get_transform()
                lat, lng = gps_service.carla_to_gps(transform.location.x, transform.location.y)
                
                state_manager.update_state(
                    vehicle_speed=round(speed_kmh, 1),
                    gps_latitude=lat,
                    gps_longitude=lng,
                    carla_fps=carla_wrapper.carla_fps,
                    camera_fps=carla_wrapper.camera_fps,
                    camera_connected=carla_wrapper.camera is not None
                )

                # Run Look-Ahead Autonomous Controller if navigating
                if state.vehicle_mode == VehicleMode.NAVIGATING_TO_HOSPITAL:
                    throttle, brake, steer, reached = carla_lookahead_controller.compute_control(
                        carla_wrapper.vehicle, speed_kmh
                    )
                    
                    if reached:
                        logger.info("CARLA Destination Hospital Reached!")
                        state_manager.update_state(
                            vehicle_mode=VehicleMode.HOSPITAL_REACHED,
                            navigation_status="HOSPITAL_REACHED",
                            vehicle_speed=0.0,
                            target_speed=0.0,
                            hospital_distance=0.0,
                            route_eta=0.0
                        )
            except Exception as e:
                logger.error(f"CARLA step error: {e}")

    def generate_synthetic_camera_frame(self) -> np.ndarray:
        """Generates a dynamic 1280x720 OpenCV HUD image simulating third-person vehicle view."""
        state = state_manager.get_state()
        
        height, width = 720, 1280
        img = np.zeros((height, width, 3), dtype=np.uint8)

        # Sky background
        img[0:360, :] = [30, 20, 15]
        # Ground
        img[360:720, :] = [20, 45, 20]

        # Animated Road Perspective
        self.canvas_angle += (state.vehicle_speed / 60.0) * 0.1
        offset = int(math.sin(self.canvas_angle) * 20)

        pts_road = np.array([
            [width // 2 - 80 + offset, 360],
            [width // 2 + 80 + offset, 360],
            [width - 100, height],
            [100, height]
        ], np.int32)
        
        cv2.fillPoly(img, [pts_road], (60, 60, 65))

        for y in range(380, height, 40):
            t = (y - 360) / 360.0
            x_center = int((width // 2 + offset) * (1 - t) + (width // 2) * t)
            line_w = int(4 + 20 * t)
            cv2.line(img, (x_center, y), (x_center, y + 20), (255, 255, 255), line_w)

        # Vehicle Rear Silhouette
        car_w, car_h = 240, 140
        car_x = width // 2 - car_w // 2
        car_y = height - 200
        
        cv2.rectangle(img, (car_x, car_y), (car_x + car_w, car_y + car_h), (180, 100, 30), -1)
        cv2.rectangle(img, (car_x + 30, car_y - 50), (car_x + car_w - 30, car_y), (140, 70, 20), -1)
        cv2.rectangle(img, (car_x + 10, car_y + 20), (car_x + 60, car_y + 40), (0, 0, 255), -1)
        cv2.rectangle(img, (car_x + car_w - 60, car_y + 20), (car_x + car_w - 10, car_y + 40), (0, 0, 255), -1)
        
        if state.vehicle_mode in [VehicleMode.SLOWING_DOWN, VehicleMode.STOPPED, VehicleMode.PULLING_OVER]:
            cv2.circle(img, (car_x + 35, car_y + 30), 25, (0, 0, 255), -1)
            cv2.circle(img, (car_x + car_w - 35, car_y + 30), 25, (0, 0, 255), -1)

        # HUD Overlay Header Banner
        cv2.rectangle(img, (0, 0), (width, 80), (15, 15, 20), -1)
        cv2.putText(img, "AI DRIVER MONITORING & EMERGENCY RESPONSE - LIVE CAMERA", (30, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        
        mode_str = f"MODE: {state.vehicle_mode.value}"
        cv2.putText(img, mode_str, (width - 420, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        # Telemetry HUD overlay on bottom left
        cv2.rectangle(img, (30, height - 160), (450, height - 30), (0, 0, 0), -1)
        cv2.putText(img, f"SPEED: {state.vehicle_speed:.1f} km/h", (45, height - 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(img, f"GPS: {state.gps_latitude:.6f}, {state.gps_longitude:.6f}", (45, height - 85),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(img, f"DRIVER: {state.driver_status.value}", (45, height - 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255) if state.emergency_active else (0, 255, 0), 2)

        # GPU / Hardware Badge overlay on top right
        device_str = f"GPU: {state.gpu_name}" if state.cuda_available else "AI: CPU SIMULATION"
        cv2.putText(img, device_str, (width - 420, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 180) if state.cuda_available else (180, 180, 180), 1)

        # Emergency Warning Box if emergency active
        if state.emergency_active:
            pulse = int((time.time() * 4) % 2)
            banner_color = (0, 0, 220) if pulse else (0, 0, 140)
            cv2.rectangle(img, (width // 2 - 350, 100), (width // 2 + 350, 170), banner_color, -1)
            
            msg = f"EMERGENCY: {state.emergency_stage}"
            if state.emergency_stage == "WAITING_FOR_DRIVER":
                msg = f"WAITING FOR DRIVER ({state.response_time_remaining}s)"
            
            cv2.putText(img, msg, (width // 2 - 320, 145),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        if state.vehicle_mode == VehicleMode.HOSPITAL_REACHED:
            cv2.rectangle(img, (width // 2 - 350, 100), (width // 2 + 350, 170), (0, 180, 0), -1)
            cv2.putText(img, "HOSPITAL REACHED - EMERGENCY COMPLETE", (width // 2 - 330, 145),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        return img


simulation_engine = SimulationEngine()
