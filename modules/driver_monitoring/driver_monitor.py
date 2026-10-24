from backend.app.models.schemas import DriverStatus
from backend.app.services.state_manager import state_manager


class DriverMonitor:
    """Simulates driver state monitoring and handles driver response interaction."""

    def __init__(self):
        pass

    def get_status(self) -> DriverStatus:
        state = state_manager.get_state()
        return state.driver_status

    def set_status(self, status: DriverStatus):
        state_manager.update_state(driver_status=status)

    def trigger_emergency(self):
        """Sets driver to UNRESPONSIVE and initializes emergency flags."""
        state_manager.update_state(
            driver_status=DriverStatus.UNRESPONSIVE,
            driver_responsive=False,  # MUST strictly default to False (BUG 1 fix)
            emergency_active=True
        )

    def set_driver_responded(self) -> bool:
        """Processes driver click on 'Driver Responded' button during response window."""
        state = state_manager.get_state()
        
        # Must only work if emergency is active and in waiting window
        if not state.emergency_active:
            return False
        
        if state.response_time_remaining <= 0 and state.emergency_stage not in ["WAITING_FOR_DRIVER", "FAMILY_ALERT_SENT"]:
            # If window expired or invalid stage
            if state.emergency_stage == "AUTONOMOUS_EMERGENCY":
                return False

        state_manager.update_state(
            driver_status=DriverStatus.DRIVER_RESPONDED,
            driver_responsive=True,
            emergency_stage="CANCELLED",
            navigation_status="CANCELLED"
        )
        return True


driver_monitor = DriverMonitor()
