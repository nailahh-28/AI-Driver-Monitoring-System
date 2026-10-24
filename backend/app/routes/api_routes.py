import cv2
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse

from backend.app.config import EXECUTION_MODE, CARLA_HOST, CARLA_PORT
from backend.app.models.schemas import (
    SystemState, EmergencyStartRequest, DriverRespondRequest,
    SimulationStartRequest, SimulationMode, DriverStatus, VehicleMode,
    HealthCheckResponse, GpuStatusInfo
)
from backend.app.services.state_manager import state_manager
from modules.driver_monitoring.driver_monitor import driver_monitor
from modules.vehicle_control.emergency_controller import emergency_controller
from modules.simulation.simulation_engine import simulation_engine
from carla.carla_client_wrapper import carla_wrapper
from ai_worker.worker import ai_worker
from camera_monitoring_service import monitoring_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["API"])


@router.get("/status", response_model=SystemState)
def get_system_status():
    return state_manager.get_state()


@router.get("/gpu/status", response_model=GpuStatusInfo)
def get_gpu_status():
    info = ai_worker.get_status()
    return GpuStatusInfo(
        cuda_available=info["cuda_available"],
        ai_device=info["ai_device"],
        gpu_name=info["gpu_name"],
        vram_usage=info["vram_usage"],
        pytorch_version=info["pytorch_version"],
        cuda_version=info["cuda_version"]
    )


@router.get("/carla/status")
def get_carla_status():
    state = state_manager.get_state()
    return {
        "connected": state.carla_connected,
        "host": CARLA_HOST,
        "port": CARLA_PORT,
        "carla_fps": state.carla_fps,
        "camera_fps": state.camera_fps
    }


@router.get("/vehicle")
def get_vehicle_status():
    state = state_manager.get_state()
    return {
        "vehicle_id": state.vehicle_id,
        "vehicle_mode": state.vehicle_mode,
        "vehicle_speed": state.vehicle_speed,
        "emergency_active": state.emergency_active
    }


@router.get("/driver")
def get_driver_status():
    state = state_manager.get_state()
    return {
        "driver_status": state.driver_status,
        "driver_responsive": state.driver_responsive,
        "response_time_remaining": state.response_time_remaining
    }


@router.get("/gps")
def get_gps_location():
    state = state_manager.get_state()
    return {
        "latitude": state.gps_latitude,
        "longitude": state.gps_longitude
    }


@router.get("/hospital")
@router.get("/hospital/nearest")
def get_hospital_info():
    state = state_manager.get_state()
    return {
        "hospital_name": state.hospital_name,
        "hospital_latitude": state.hospital_latitude,
        "hospital_longitude": state.hospital_longitude,
        "hospital_distance": state.hospital_distance,
        "route_eta": state.route_eta
    }


@router.get("/route")
@router.get("/navigation/route")
def get_route_info():
    state = state_manager.get_state()
    waypoints, _ = state_manager.get_route_waypoints()
    return {
        "route_distance": state.route_distance,
        "route_eta": state.route_eta,
        "waypoints_count": len(waypoints),
        "waypoints": waypoints
    }


@router.get("/navigation")
def get_navigation_status():
    state = state_manager.get_state()
    return {
        "navigation_status": state.navigation_status,
        "vehicle_mode": state.vehicle_mode,
        "hospital_distance": state.hospital_distance,
        "route_eta": state.route_eta,
        "current_waypoint": state.current_waypoint,
        "total_waypoints": state.total_waypoints
    }


@router.post("/emergency/start")
@router.post("/emergency/trigger")
def start_emergency(req: EmergencyStartRequest = EmergencyStartRequest()):
    """Triggers serious driver emergency and starts response window workflow."""
    driver_monitor.trigger_emergency()
    emergency_controller.start_emergency_sequence(
        demo_mode=req.demo_mode,
        custom_response_time=req.response_time
    )
    return {"status": "SUCCESS", "message": "Emergency sequence initiated."}


@router.post("/driver/respond")
@router.post("/emergency/cancel")
def driver_respond():
    """Allows driver to click on-screen 'Driver Responded' button during response window."""
    success = driver_monitor.set_driver_responded()
    if not success:
        return {
            "status": "FAILED",
            "message": "Driver response rejected (no active response window or window expired)."
        }
    emergency_controller.stop_emergency()
    return {"status": "SUCCESS", "message": "Driver responded. Emergency cancelled."}


@router.post("/simulation/start")
def start_simulation(req: SimulationStartRequest = SimulationStartRequest()):
    """Starts CARLA mode or standalone offline SIMULATION mode."""
    target_mode = req.execution_mode or EXECUTION_MODE
    state_manager.update_state(execution_mode=target_mode)

    if req.use_carla:
        success, msg = carla_wrapper.connect()
        if success:
            spawn_success, spawn_msg = carla_wrapper.spawn_vehicle_and_camera()
            if spawn_success:
                state_manager.update_state(
                    mode=SimulationMode.CARLA,
                    carla_connected=True,
                    vehicle_mode=VehicleMode.NORMAL,
                    target_speed=60.0
                )
                simulation_engine.start()
                return {"status": "SUCCESS", "message": "CARLA simulation started."}
            else:
                state_manager.update_state(
                    mode=SimulationMode.SIMULATION,
                    carla_connected=False,
                    vehicle_mode=VehicleMode.NORMAL,
                    target_speed=60.0,
                    emergency_active=False,
                    driver_status=DriverStatus.NORMAL
                )
                simulation_engine.start()
                return {"status": "PARTIAL", "message": f"CARLA not available on system. Switched to Standalone SIMULATION mode."}
        else:
            state_manager.update_state(
                mode=SimulationMode.SIMULATION,
                carla_connected=False,
                vehicle_mode=VehicleMode.NORMAL,
                target_speed=60.0,
                emergency_active=False,
                driver_status=DriverStatus.NORMAL
            )
            simulation_engine.start()
            return {"status": "PARTIAL", "message": "CARLA not running. Switched to Standalone SIMULATION mode (No CARLA required)."}
    else:
        state_manager.update_state(
            mode=SimulationMode.SIMULATION,
            carla_connected=False,
            vehicle_mode=VehicleMode.NORMAL,
            target_speed=60.0,
            vehicle_speed=60.0,
            emergency_active=False,
            driver_status=DriverStatus.NORMAL,
            navigation_status="NORMAL_DRIVING"
        )
        simulation_engine.start()
        return {"status": "SUCCESS", "message": f"SIMULATION mode started ({target_mode.upper()} mode). Vehicle is now driving normally."}


@router.post("/simulation/reset")
def reset_simulation():
    """Resets system state, stops emergency threads, cleans up CARLA actors."""
    emergency_controller.stop_emergency()
    carla_wrapper.cleanup()
    state_manager.reset()
    simulation_engine.start()
    return {"status": "SUCCESS", "message": "System state and simulation reset to NORMAL."}


@router.post("/vehicle/stop")
def stop_vehicle():
    """Emergency manual vehicle stop."""
    emergency_controller.stop_emergency()
    state_manager.update_state(
        vehicle_speed=0.0,
        target_speed=0.0,
        vehicle_mode=VehicleMode.STOPPED,
        navigation_status="MANUAL_STOP"
    )
    return {"status": "SUCCESS", "message": "Vehicle manually stopped."}


def generate_mjpeg_stream():
    """MJPEG Video Frame Streaming Generator."""
    while True:
        frame = None
        state = state_manager.get_state()
        
        # Prefer the monitored webcam feed in either simulation mode.
        frame = monitoring_service.get_current_frame()

        # Fall back to CARLA when no local webcam frame is available.
        if frame is None and state.mode == SimulationMode.CARLA and state.carla_connected:
            frame = carla_wrapper.get_latest_frame()

        # Fallback to synthetic HUD camera frame
        if frame is None:
            frame = simulation_engine.generate_synthetic_camera_frame()

        ret, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if ret:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        
        cv2.waitKey(66)  # ~15 FPS MJPEG stream


@router.get("/camera/stream")
def camera_stream():
    """Returns live MJPEG camera feed for React dashboard canvas/img component."""
    return StreamingResponse(
        generate_mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
