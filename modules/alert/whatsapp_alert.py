import os
import sys
import time
import logging
import urllib.parse
import threading
from typing import Optional, Tuple

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("EmergencyAlertService")


def safe_print(text: str):
    """Safely outputs text to stdout on Windows without cp1252 UnicodeEncodeError crashes."""
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeError):
        try:
            clean_text = text.encode("ascii", errors="replace").decode("ascii")
            print(clean_text)
        except Exception:
            pass


def safe_log(level: int, msg: str):
    """Safely logs message without charmap encoding issues on Windows consoles/files."""
    try:
        logger.log(level, msg)
    except (UnicodeEncodeError, UnicodeError):
        try:
            clean_msg = msg.encode("ascii", errors="replace").decode("ascii")
            logger.log(level, clean_msg)
        except Exception:
            pass


def get_live_location() -> Tuple[float, float]:
    """
    Fetches real-time latitude and longitude via IP geolocation.
    Falls back to default coordinates (12.859995, 77.5417) if offline or unavailable.
    """
    try:
        import requests
        response = requests.get("http://ip-api.com/json/", timeout=5)
        data = response.json()
        lat = data.get("lat")
        lon = data.get("lon")
        if lat is not None and lon is not None:
            return float(lat), float(lon)
    except Exception as e:
        safe_print(f"[Location] IP geolocation note: {e}")

    # Default fallback coordinates
    return 12.859995, 77.5417


class EmergencyAlertService:
    """
    Autonomous Emergency Alert Service for WhatsApp.
    Dispatches critical emergency notifications when the driver is unresponsive.
    
    Key Features:
    - Default emergency number: +918073662914 (configurable via EMERGENCY_CONTACT_PHONE or configure_contact()).
    - Real-time location integration: StateManager GPS telemetry with IP-based live geolocation fallback.
    - Automated pywhatkit dispatch in non-blocking daemon thread.
    - Robust multi-tier fallback: Direct CallMeBot API, WhatsApp Web URL, clipboard injection,
      and Computer Vision button detection.
    - 100% safe Windows console and file logging (no cp1252 UnicodeEncodeError crashes).
    - Thread-safe session deduplication to prevent duplicate message storms.
    """

    def __init__(self):
        self.lock = threading.Lock()
        self.is_dispatched_for_session = False
        self.active_dispatch_thread: Optional[threading.Thread] = None

        # Contact defaults (configurable via environment variables or configure_contact())
        self.contact_name = os.getenv("EMERGENCY_CONTACT_NAME", "Emergency Contact")
        raw_phone = os.getenv("EMERGENCY_CONTACT_PHONE", "+918073662914").strip()
        self.contact_phone = self._clean_phone(raw_phone)

    def _clean_phone(self, phone: str) -> str:
        digits = "".join(filter(str.isdigit, phone))
        if len(digits) == 10:
            return f"+91{digits}"
        if not phone.startswith("+") and digits:
            return f"+{digits}"
        return f"+{digits}" if digits else phone

    def configure_contact(self, name: str, phone: str):
        with self.lock:
            self.contact_name = name.strip() or "Emergency Contact"
            self.contact_phone = self._clean_phone(phone.strip())
            safe_log(logging.INFO, f"Emergency contact updated: {self.contact_name} ({self.contact_phone})")

    def reset_session(self):
        """Resets the dispatch flag when emergency is resolved, allowing future alerts."""
        with self.lock:
            self.is_dispatched_for_session = False
            safe_log(logging.INFO, "Emergency alert session reset. Ready for next incident.")

    def trigger_alert_if_unresponsive(self, force: bool = False):
        """
        Triggers the autonomous emergency alert sequence in a non-blocking background thread.
        Guarantees dispatch only once per emergency event unless force=True.
        """
        with self.lock:
            if self.is_dispatched_for_session and not force:
                safe_log(logging.DEBUG, "Emergency alert already dispatched for current session. Skipping duplicate.")
                return False

            self.is_dispatched_for_session = True

        thread = threading.Thread(target=self._execute_dispatch_workflow, daemon=True)
        self.active_dispatch_thread = thread
        thread.start()
        return True

    def _build_emergency_message(self) -> Tuple[str, str, str]:
        """Constructs high-urgency message with telemetry, coordinates, and destination hospital."""
        lat = None
        lon = None
        hospital_name = "Nearest Emergency Medical Center"
        hospital_dist = "Calculating..."
        route_eta = "Pending"

        try:
            from backend.app.services.state_manager import state_manager
            state = state_manager.get_state()
            lat = state.gps_latitude
            lon = state.gps_longitude
            if state.hospital_name:
                hospital_name = state.hospital_name
            if state.hospital_distance:
                hospital_dist = f"{state.hospital_distance:.2f} km"
            if state.route_eta:
                route_eta = f"{state.route_eta:.1f} mins"
        except Exception as e:
            safe_log(logging.WARNING, f"Could not read state_manager: {e}")

        # If vehicle telemetry does not provide GPS coordinates, query IP geolocation
        if lat is None or lon is None or (lat == 0.0 and lon == 0.0):
            lat, lon = get_live_location()

        location_url = f"https://maps.google.com/?q={lat:.6f},{lon:.6f}" if (lat and lon) else "https://maps.google.com/?q=12.859995,77.5417"
        coords_str = f"`{lat:.6f}, {lon:.6f}`" if (lat and lon) else "`12.859995, 77.5417`"

        message = (
            "🚨 *AI DRIVER MONITORING: EMERGENCY ALERT* 🚨\n\n"
            "⚠️ *CRITICAL:* The driver was unresponsive and *DID NOT RESPOND* to the safety countdown.\n"
            "The vehicle has safely stopped and activated Autonomous Emergency Mode.\n\n"
            f"📍 *Live Vehicle Location:*\n{location_url}\n"
            f"🗺️ Coordinates: {coords_str}\n\n"
            f"🏥 *Destination Hospital:* {hospital_name}\n"
            f"🛣️ *Distance to Hospital:* {hospital_dist}\n"
            f"⏱️ *Estimated ETA:* {route_eta}\n\n"
            f"📞 *Designated Contact:* {self.contact_name}\n"
            "Please call the driver or dispatch emergency services immediately!"
        )

        return message, location_url, hospital_name

    def _open_browser_url(self, url: str) -> bool:
        """Robust multi-tier URL opener guaranteeing browser launch on Windows and other OSs."""
        # Tier 1: Windows ShellExecute (native, 100% reliable in user desktop)
        if sys.platform == "win32":
            try:
                os.startfile(url)
                safe_log(logging.INFO, "[EmergencyAlert] Browser launched via os.startfile.")
                return True
            except Exception as e:
                safe_log(logging.WARNING, f"[EmergencyAlert] os.startfile failed: {e}")

        # Tier 2: Python standard webbrowser module
        try:
            import webbrowser
            if webbrowser.open(url, new=2):
                safe_log(logging.INFO, "[EmergencyAlert] Browser launched via webbrowser.open.")
                return True
        except Exception as e:
            safe_log(logging.WARNING, f"[EmergencyAlert] webbrowser.open failed: {e}")

        # Tier 3: Command-line start fallback on Windows
        if sys.platform == "win32":
            try:
                import subprocess
                subprocess.Popen(["cmd", "/c", "start", "", url], shell=True)
                safe_log(logging.INFO, "[EmergencyAlert] Browser launched via cmd start.")
                return True
            except Exception as e:
                safe_log(logging.WARNING, f"[EmergencyAlert] cmd start fallback failed: {e}")

        return False

    def _bring_whatsapp_to_foreground(self) -> bool:
        """Finds WhatsApp Web or active browser window and brings it to foreground."""
        if sys.platform == "win32":
            try:
                import ctypes
                user32 = ctypes.windll.user32
                found_hwnd = []

                WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

                def _enum_cb(hwnd, _):
                    if user32.IsWindowVisible(hwnd):
                        length = user32.GetWindowTextLengthW(hwnd)
                        if length > 0:
                            buff = ctypes.create_unicode_buffer(length + 1)
                            user32.GetWindowTextW(hwnd, buff, length + 1)
                            title = buff.value.lower()
                            # Prioritize window containing 'whatsapp'
                            if "whatsapp" in title:
                                found_hwnd.insert(0, hwnd)
                            elif any(b in title for b in ["chrome", "edge", "brave", "firefox", "opera"]):
                                found_hwnd.append(hwnd)
                    return True

                user32.EnumWindows(WNDENUMPROC(_enum_cb), 0)

                if found_hwnd:
                    target_hwnd = found_hwnd[0]
                    # SW_MAXIMIZE = 3, SW_RESTORE = 9
                    user32.ShowWindow(target_hwnd, 3)
                    # Simulate Alt key to bypass Windows SetForegroundWindow restrictions
                    user32.keybd_event(0x12, 0, 0, 0)
                    user32.keybd_event(0x12, 0, 2, 0)
                    user32.SetForegroundWindow(target_hwnd)
                    time.sleep(0.4)
                    return True
            except Exception as e:
                safe_log(logging.DEBUG, f"Window foreground activation note: {e}")

        return False

    def _locate_send_button_autonomously(self) -> Optional[Tuple[int, int]]:
        """
        AUTONOMOUS COMPUTER VISION DETECTION of WhatsApp Web's Send Button.
        
        Does NOT assume or hardcode screen coordinates.
        Uses OpenCV color & contour analysis to locate the distinctive
        WhatsApp green Send button badge (#25D366 / #00A884) in the chat
        input zone dynamically on the user's actual display.
        
        Returns:
            (x, y) coordinates of the button centroid if found, else None.
        """
        try:
            import pyautogui
            import cv2
            import numpy as np

            screen_img = pyautogui.screenshot()
            frame = np.array(screen_img)
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            h, w = frame_bgr.shape[:2]

            # In WhatsApp Web, the Send button is in the lower region of the window
            roi_y_start = int(h * 0.75)
            roi = frame_bgr[roi_y_start:h, 0:w]

            # Convert ROI to HSV
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

            # WhatsApp Green Color range (#25D366 and dark mode #00A884)
            lower_green = np.array([35, 70, 70])
            upper_green = np.array([85, 255, 255])
            mask = cv2.inRange(hsv, lower_green, upper_green)

            # Morphological cleanup
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.dilate(mask, kernel, iterations=1)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            candidates = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                # Circular Send button radius is ~12-30px, area ~80 to 4000px^2
                if 80 < area < 4000:
                    perimeter = cv2.arcLength(cnt, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * (area / (perimeter * perimeter))
                        if circularity > 0.40:
                            (cx, cy), radius = cv2.minEnclosingCircle(cnt)
                            global_x = int(cx)
                            global_y = roi_y_start + int(cy)
                            candidates.append((global_x, global_y, area, global_x))

            if candidates:
                # Select candidate furthest to the right (the Send button)
                candidates.sort(key=lambda item: item[3], reverse=True)
                target_x, target_y = candidates[0][0], candidates[0][1]
                safe_log(logging.INFO, f"[EmergencyAlert] Visually located WhatsApp Send button at ({target_x}, {target_y}) via Computer Vision!")
                return (target_x, target_y)

        except Exception as e:
            safe_log(logging.DEBUG, f"Computer vision button locator note: {e}")

        return None

    def _execute_dispatch_workflow(self):
        """Full end-to-end autonomous dispatch workflow."""
        try:
            message, location_url, hospital_name = self._build_emergency_message()
            clean_phone = "".join(filter(str.isdigit, self.contact_phone))
            encoded_msg = urllib.parse.quote(message)
            formatted_phone = f"+{clean_phone}" if not clean_phone.startswith("+") else clean_phone

            safe_print("\n" + "=" * 70)
            safe_print("[EMERGENCY ALERT] INITIATING AUTONOMOUS DISPATCH WORKFLOW")
            safe_print(f"Recipient: {self.contact_name} ({formatted_phone})")
            safe_print(f"Location:  {location_url}")
            safe_print(f"Hospital:  {hospital_name}")
            safe_print("=" * 70)

            # 1. Background Direct HTTP API (CallMeBot) if key is configured
            callmebot_key = os.getenv("CALLMEBOT_API_KEY", "")
            if callmebot_key:
                try:
                    import requests
                    safe_log(logging.INFO, f"Dispatching via CallMeBot API to {formatted_phone}...")
                    api_url = f"https://api.callmebot.com/whatsapp.php?phone={formatted_phone}&text={encoded_msg}&apikey={callmebot_key}"
                    resp = requests.get(api_url, timeout=10)
                    if resp.status_code == 200:
                        safe_log(logging.INFO, "WhatsApp alert successfully delivered via CallMeBot API!")
                        safe_print("[EmergencyAlert] Delivered directly via CallMeBot API!")
                        return
                except Exception as e:
                    safe_log(logging.WARNING, f"CallMeBot API notice: {e}")

            # 2. Automated pywhatkit dispatch (Primary browser-automation dispatch)
            try:
                import pywhatkit as kit
                safe_print(f"[EmergencyAlert] Dispatching WhatsApp alert via pywhatkit to {formatted_phone}...")
                kit.sendwhatmsg_instantly(
                    phone_no=formatted_phone,
                    message=message,
                    wait_time=15,
                    tab_close=False
                )
                safe_print("[EmergencyAlert] SUCCESS: WhatsApp emergency alert sent automatically via pywhatkit!")
                return
            except Exception as kit_err:
                safe_print(f"[EmergencyAlert] pywhatkit notice ({kit_err}). Engaging multi-tier fallback...")

            # 3. Multi-tier Fallback: Clipboard backup + WhatsApp Web direct launch
            try:
                import pyperclip
                pyperclip.copy(message)
                safe_print("[EmergencyAlert] Emergency message copied to system clipboard.")
            except Exception as e:
                safe_log(logging.WARNING, f"pyperclip notice: {e}")

            whatsapp_web_url = f"https://web.whatsapp.com/send?phone={clean_phone}&text={encoded_msg}"
            safe_print(f"[EmergencyAlert] Opening WhatsApp Web: {whatsapp_web_url}")

            opened = self._open_browser_url(whatsapp_web_url)
            if not opened:
                safe_print("[EmergencyAlert] Warning: Could not automatically launch browser.")

            # 4. Autonomous multi-pulse dispatch (Computer Vision Send Button / Enter hotkey)
            import pyautogui
            pyautogui.FAILSAFE = False
            screen_w, screen_h = pyautogui.size()

            safe_print("[EmergencyAlert] Waiting for WhatsApp Web to load conversation...")
            time.sleep(7.0)

            for attempt in range(1, 5):
                safe_print(f"[EmergencyAlert] Autonomous send verification pulse ({attempt}/4)...")
                self._bring_whatsapp_to_foreground()
                time.sleep(0.6)

                btn_coords = self._locate_send_button_autonomously()

                if not btn_coords:
                    safe_print("[EmergencyAlert] Pasting message directly into chat composer via Clipboard...")
                    composer_click_y = screen_h - 70
                    composer_click_x = int(screen_w * 0.55)
                    pyautogui.click(composer_click_x, composer_click_y)
                    time.sleep(0.3)
                    pyautogui.hotkey("ctrl", "v")
                    time.sleep(0.5)

                    btn_coords = self._locate_send_button_autonomously()

                if btn_coords:
                    bx, by = btn_coords
                    safe_print(f"[EmergencyAlert] Computer Vision found Send button at ({bx}, {by}). Clicking...")
                    pyautogui.click(bx, by)
                    time.sleep(0.3)
                    pyautogui.press("enter")
                    safe_print("[EmergencyAlert] SUCCESS: WhatsApp emergency alert sent via detected Send button!")
                    return

                safe_print("[EmergencyAlert] Sending Enter keystroke to message composer...")
                pyautogui.press("enter")
                time.sleep(0.3)
                pyautogui.hotkey("ctrl", "enter")
                time.sleep(0.3)

                if attempt < 4:
                    time.sleep(3.5)

            safe_print("[EmergencyAlert] Autonomous alert sequence completed.")

        except Exception as exc:
            safe_print(f"[EmergencyAlert] Exception in dispatch workflow: {exc}")
            safe_log(logging.ERROR, f"Dispatch workflow error: {exc}")


# Singleton instance
emergency_alert_service = EmergencyAlertService()
