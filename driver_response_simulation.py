import sys
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import tkinter as tk
from tkinter import messagebox
import threading

from modules.vehicle_control.vehicle_state import (
    VehicleState,
    VehicleMode
)

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


class DriverResponseSimulation:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "AI Driver Monitoring - Emergency Simulation"
        )

        self.root.geometry(
            "850x750"
        )

        self.root.resizable(
            False,
            False
        )

        # =====================================================
        # VEHICLE
        # =====================================================

        self.vehicle = VehicleState()

        self.vehicle.speed_kmh = 60

        self.controller = EmergencyController(
            self.vehicle
        )

        # =====================================================
        # GPS
        # =====================================================

        self.gps = GPSService()

        # Simulated Bengaluru location
        self.gps.set_location(
            latitude=12.9716,
            longitude=77.5946
        )

        self.location = (
            self.gps.get_location()
        )

        # =====================================================
        # SERVICES
        # =====================================================

        self.hospital_finder = HospitalFinder()

        self.route_planner = RoutePlanner()

        # =====================================================
        # STATE
        # =====================================================

        self.countdown_running = False

        self.driver_responded = False

        self.remaining_time = 10

        self.simulation_running = False

        # =====================================================
        # UI
        # =====================================================

        self.create_interface()

    # =========================================================
    # CREATE INTERFACE
    # =========================================================

    def create_interface(self):

        # -----------------------------------------------------
        # TITLE
        # -----------------------------------------------------

        title = tk.Label(
            self.root,
            text="AI DRIVER MONITORING SYSTEM",
            font=("Arial", 24, "bold")
        )

        title.pack(
            pady=(15, 5)
        )

        subtitle = tk.Label(
            self.root,
            text="Emergency Response Simulation",
            font=("Arial", 14)
        )

        subtitle.pack(
            pady=(0, 10)
        )

        # -----------------------------------------------------
        # STATUS
        # -----------------------------------------------------

        self.status_frame = tk.Frame(
            self.root,
            relief=tk.GROOVE,
            borderwidth=2
        )

        self.status_frame.pack(
            padx=30,
            pady=5,
            fill="x"
        )

        tk.Label(
            self.status_frame,
            text="SYSTEM STATUS",
            font=("Arial", 13, "bold")
        ).pack(
            pady=(8, 3)
        )

        self.status_label = tk.Label(
            self.status_frame,
            text="Ready to start simulation",
            font=("Arial", 14)
        )

        self.status_label.pack(
            pady=(0, 8)
        )

        # -----------------------------------------------------
        # VEHICLE STATUS
        # -----------------------------------------------------

        self.vehicle_label = tk.Label(
            self.root,
            text="Vehicle Speed: 60 km/h\nMode: NORMAL",
            font=("Arial", 13)
        )

        self.vehicle_label.pack(
            pady=5
        )

        # -----------------------------------------------------
        # GPS LOCATION
        # -----------------------------------------------------

        self.location_frame = tk.Frame(
            self.root,
            relief=tk.GROOVE,
            borderwidth=2
        )

        self.location_frame.pack(
            padx=30,
            pady=5,
            fill="x"
        )

        tk.Label(
            self.location_frame,
            text="📍 VEHICLE LOCATION",
            font=("Arial", 13, "bold")
        ).pack(
            pady=(7, 3)
        )

        self.location_label = tk.Label(
            self.location_frame,
            text=(
                f"Latitude: {self.location.latitude:.6f}\n"
                f"Longitude: {self.location.longitude:.6f}"
            ),
            font=("Arial", 12)
        )

        self.location_label.pack(
            pady=(0, 7)
        )

        # -----------------------------------------------------
        # DESTINATION
        # -----------------------------------------------------

        self.destination_label = tk.Label(
            self.root,
            text="Hospital: Not selected",
            font=("Arial", 12)
        )

        self.destination_label.pack(
            pady=3
        )

        # -----------------------------------------------------
        # COUNTDOWN
        # -----------------------------------------------------

        self.countdown_label = tk.Label(
            self.root,
            text="10",
            font=("Arial", 42, "bold")
        )

        self.countdown_label.pack(
            pady=2
        )

        self.countdown_text = tk.Label(
            self.root,
            text="Driver response window",
            font=("Arial", 12)
        )

        self.countdown_text.pack()

        # -----------------------------------------------------
        # DRIVER RESPONSE BUTTON
        # -----------------------------------------------------

        self.response_button = tk.Button(
            self.root,
            text="🟢 DRIVER RESPONDS",
            font=("Arial", 15, "bold"),
            width=25,
            height=2,
            command=self.driver_response
        )

        self.response_button.pack(
            pady=10
        )

        self.response_button.config(
            state=tk.DISABLED
        )

        # -----------------------------------------------------
        # START BUTTON
        # -----------------------------------------------------

        self.start_button = tk.Button(
            self.root,
            text="🚨 START EMERGENCY SIMULATION",
            font=("Arial", 14, "bold"),
            width=30,
            height=2,
            command=self.start_simulation
        )

        self.start_button.pack(
            pady=5
        )

        # -----------------------------------------------------
        # RESULT
        # -----------------------------------------------------

        self.result_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 13, "bold")
        )

        self.result_label.pack(
            pady=5
        )

    # =========================================================
    # START SIMULATION
    # =========================================================

    def start_simulation(self):

        if self.simulation_running:
            return

        self.simulation_running = True

        self.countdown_running = False

        self.driver_responded = False

        self.remaining_time = 10

        # Reset vehicle

        self.vehicle.reset()

        self.vehicle.speed_kmh = 60

        # Reset destination

        self.destination_label.config(
            text="Hospital: Not selected"
        )

        self.result_label.config(
            text=""
        )

        self.countdown_label.config(
            text="10"
        )

        self.start_button.config(
            state=tk.DISABLED
        )

        self.response_button.config(
            state=tk.DISABLED
        )

        # Run emergency sequence in background

        thread = threading.Thread(
            target=self.run_emergency_sequence,
            daemon=True
        )

        thread.start()

    # =========================================================
    # EMERGENCY SEQUENCE
    # =========================================================

    def run_emergency_sequence(self):

        # -----------------------------------------------------
        # EMERGENCY
        # -----------------------------------------------------

        self.root.after(
            0,
            lambda: self.status_label.config(
                text="🚨 EMERGENCY DETECTED"
            )
        )

        self.controller.trigger_emergency()

        # -----------------------------------------------------
        # SLOW DOWN
        # -----------------------------------------------------

        self.root.after(
            0,
            lambda: self.status_label.config(
                text="🟡 Vehicle slowing down..."
            )
        )

        self.controller.slow_down()

        self.root.after(
            0,
            self.update_vehicle_status
        )

        # -----------------------------------------------------
        # PULL OVER
        # -----------------------------------------------------

        self.root.after(
            0,
            lambda: self.status_label.config(
                text="➡️ Vehicle pulling over..."
            )
        )

        self.controller.pull_over()

        # -----------------------------------------------------
        # STOP
        # -----------------------------------------------------

        self.root.after(
            0,
            lambda: self.status_label.config(
                text="🛑 Vehicle stopping..."
            )
        )

        self.controller.stop_vehicle()

        self.root.after(
            0,
            self.update_vehicle_status
        )

        # -----------------------------------------------------
        # FAMILY ALERT
        # -----------------------------------------------------

        self.root.after(
            0,
            lambda: self.status_label.config(
                text="📱 Sending emergency alert..."
            )
        )

        self.controller.send_family_alert()

        # -----------------------------------------------------
        # DRIVER RESPONSE WINDOW
        # -----------------------------------------------------

        self.root.after(
            0,
            self.enable_response_window
        )

    # =========================================================
    # DRIVER RESPONSE WINDOW
    # =========================================================

    def enable_response_window(self):

        if self.driver_responded:
            return

        self.status_label.config(
            text="⚠️ DRIVER RESPONSE REQUIRED"
        )

        self.countdown_text.config(
            text="Click the button if the driver responds"
        )

        self.response_button.config(
            state=tk.NORMAL
        )

        self.remaining_time = 10

        self.countdown_running = True

        self.update_countdown()

    # =========================================================
    # COUNTDOWN
    # =========================================================

    def update_countdown(self):

        if not self.countdown_running:
            return

        if self.driver_responded:
            return

        self.countdown_label.config(
            text=str(
                self.remaining_time
            )
        )

        if self.remaining_time <= 0:

            self.countdown_running = False

            self.response_button.config(
                state=tk.DISABLED
            )

            self.no_driver_response()

            return

        self.remaining_time -= 1

        self.root.after(
            1000,
            self.update_countdown
        )

    # =========================================================
    # DRIVER RESPONDS
    # =========================================================

    def driver_response(self):

        if not self.countdown_running:
            return

        if self.driver_responded:
            return

        self.driver_responded = True

        self.countdown_running = False

        # Tell controller

        self.controller.driver_response()

        # Update UI

        self.response_button.config(
            state=tk.DISABLED
        )

        self.countdown_label.config(
            text="✓"
        )

        self.countdown_text.config(
            text="Driver response received"
        )

        self.status_label.config(
            text="🟢 DRIVER RESPONDED"
        )

        self.result_label.config(
            text="🟢 EMERGENCY CANCELLED"
        )

        self.vehicle.emergency_active = False

        self.vehicle.set_mode(
            VehicleMode.NORMAL
        )

        self.update_vehicle_status()

        self.simulation_running = False

        self.start_button.config(
            state=tk.NORMAL
        )

        messagebox.showinfo(
            "Driver Response",
            "Driver responded successfully.\n\n"
            "Emergency sequence cancelled."
        )

    # =========================================================
    # NO DRIVER RESPONSE
    # =========================================================

    def no_driver_response(self):

        self.status_label.config(
            text="❌ DRIVER DID NOT RESPOND"
        )

        self.countdown_text.config(
            text="Response timeout"
        )

        self.countdown_label.config(
            text="0"
        )

        self.result_label.config(
            text="🚨 EMERGENCY CONFIRMED"
        )

        # -----------------------------------------------------
        # AUTONOMOUS MODE
        # -----------------------------------------------------

        self.controller.activate_autonomous_emergency_mode()

        self.update_vehicle_status()

        # -----------------------------------------------------
        # FIND HOSPITAL
        # -----------------------------------------------------

        self.status_label.config(
            text="🏥 Finding nearest hospital..."
        )

        # Run network operation in background

        thread = threading.Thread(
            target=self.find_hospital_and_route,
            daemon=True
        )

        thread.start()

    # =========================================================
    # FIND HOSPITAL + ROUTE
    # =========================================================

    def find_hospital_and_route(self):

        try:

            latitude = (
                self.location.latitude
            )

            longitude = (
                self.location.longitude
            )

            # -------------------------------------------------
            # Hospital search
            # -------------------------------------------------

            hospital = (
                self.hospital_finder
                .find_nearest_hospital(
                    latitude,
                    longitude
                )
            )

            if hospital is None:

                self.root.after(
                    0,
                    self.hospital_not_found
                )

                return

            # -------------------------------------------------
            # Store destination
            # -------------------------------------------------

            self.vehicle.destination_name = (
                hospital.name
            )

            self.vehicle.destination_latitude = (
                hospital.latitude
            )

            self.vehicle.destination_longitude = (
                hospital.longitude
            )

            self.root.after(
                0,
                lambda: self.destination_label.config(
                    text=(
                        f"🏥 Hospital: "
                        f"{hospital.name}\n"
                        f"Distance: "
                        f"{hospital.distance_km:.2f} km"
                    )
                )
            )

            # -------------------------------------------------
            # Route calculation
            # -------------------------------------------------

            self.root.after(
                0,
                lambda: self.status_label.config(
                    text="🗺️ Calculating emergency route..."
                )
            )

            route = (
                self.route_planner.get_route(
                    start_latitude=latitude,
                    start_longitude=longitude,
                    destination_latitude=(
                        hospital.latitude
                    ),
                    destination_longitude=(
                        hospital.longitude
                    )
                )
            )

            # -------------------------------------------------
            # Route result
            # -------------------------------------------------

            self.root.after(
                0,
                lambda: self.show_route_result(
                    hospital,
                    route
                )
            )

        except Exception as error:

            self.root.after(
                0,
                lambda: self.show_navigation_error(
                    error
                )
            )

    # =========================================================
    # HOSPITAL NOT FOUND
    # =========================================================

    def hospital_not_found(self):

        self.status_label.config(
            text="⚠️ Hospital search unsuccessful"
        )

        self.result_label.config(
            text=(
                "🚨 Autonomous emergency mode active\n"
                "📍 GPS location available"
            )
        )

        self.simulation_running = False

        self.start_button.config(
            state=tk.NORMAL
        )

        messagebox.showwarning(
            "Hospital Search",
            "No hospital was found.\n\n"
            "The vehicle remains in autonomous "
            "emergency mode."
        )

    # =========================================================
    # ROUTE RESULT
    # =========================================================

    def show_route_result(
        self,
        hospital,
        route
    ):

        self.status_label.config(
            text="🚗 AUTONOMOUS NAVIGATION READY"
        )

        self.result_label.config(
            text=(
                "🚨 EMERGENCY CONFIRMED\n"
                f"🏥 {hospital.name}\n"
                f"🛣️ Distance: "
                f"{route.distance_km:.2f} km\n"
                f"⏱️ ETA: "
                f"{route.duration_minutes:.1f} minutes\n"
                f"🗺️ Route points: "
                f"{len(route.points)}"
            )
        )

        self.simulation_running = False

        self.start_button.config(
            state=tk.NORMAL
        )

        messagebox.showinfo(
            "Autonomous Emergency Navigation",
            "Driver did not respond.\n\n"
            "Autonomous emergency mode activated.\n\n"
            f"Destination:\n{hospital.name}\n\n"
            f"Distance: "
            f"{route.distance_km:.2f} km\n"
            f"Estimated time: "
            f"{route.duration_minutes:.1f} minutes"
        )

    # =========================================================
    # NAVIGATION ERROR
    # =========================================================

    def show_navigation_error(
        self,
        error
    ):

        self.status_label.config(
            text="⚠️ Navigation service error"
        )

        self.result_label.config(
            text=(
                "🚨 Autonomous emergency mode active\n"
                "📍 GPS location available\n"
                "⚠️ Route calculation unavailable"
            )
        )

        self.simulation_running = False

        self.start_button.config(
            state=tk.NORMAL
        )

        messagebox.showwarning(
            "Navigation Error",
            "Autonomous emergency mode is active.\n\n"
            "However, route calculation failed.\n\n"
            f"Error:\n{error}"
        )

    # =========================================================
    # VEHICLE STATUS
    # =========================================================

    def update_vehicle_status(self):

        self.vehicle_label.config(
            text=(
                f"Vehicle Speed: "
                f"{self.vehicle.speed_kmh:.1f} km/h\n"
                f"Mode: "
                f"{self.vehicle.mode.value}"
            )
        )


# =============================================================
# MAIN
# =============================================================

def main():

    root = tk.Tk()

    DriverResponseSimulation(
        root
    )

    root.mainloop()


if __name__ == "__main__":
    main()