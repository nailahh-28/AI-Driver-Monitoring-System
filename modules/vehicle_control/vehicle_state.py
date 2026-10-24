from enum import Enum


class VehicleMode(Enum):
    NORMAL = "NORMAL"
    EMERGENCY = "EMERGENCY"
    SLOWING_DOWN = "SLOWING_DOWN"
    PULLING_OVER = "PULLING_OVER"
    STOPPED = "STOPPED"
    WAITING_FOR_DRIVER = "WAITING_FOR_DRIVER"
    AUTONOMOUS_EMERGENCY = "AUTONOMOUS_EMERGENCY"


class VehicleState:

    def __init__(self):

        self.mode = VehicleMode.NORMAL

        self.speed_kmh = 0.0
        self.target_speed_kmh = 0.0

        # IMPORTANT:
        # At the beginning of an emergency,
        # assume the driver has NOT responded.
        self.driver_responsive = False

        self.family_alert_sent = False

        self.emergency_active = False
        self.autonomous_mode = False

        self.current_latitude = None
        self.current_longitude = None

        self.destination_latitude = None
        self.destination_longitude = None

        self.destination_name = None

    def set_mode(self, mode: VehicleMode):

        self.mode = mode

    def activate_emergency(self):

        self.emergency_active = True
        self.driver_responsive = False

        self.set_mode(VehicleMode.EMERGENCY)

    def activate_autonomous_mode(self):

        self.autonomous_mode = True

        self.set_mode(
            VehicleMode.AUTONOMOUS_EMERGENCY
        )

    def reset(self):

        self.mode = VehicleMode.NORMAL

        self.speed_kmh = 0.0
        self.target_speed_kmh = 0.0

        # New emergency starts with NO response
        self.driver_responsive = False

        self.family_alert_sent = False

        self.emergency_active = False
        self.autonomous_mode = False

        self.destination_latitude = None
        self.destination_longitude = None
        self.destination_name = None

    def __str__(self):

        return (
            f"VehicleState("
            f"mode={self.mode.value}, "
            f"speed={self.speed_kmh:.1f} km/h, "
            f"emergency={self.emergency_active}, "
            f"autonomous={self.autonomous_mode}"
            f")"
        )