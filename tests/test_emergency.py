import unittest
from backend.app.models.schemas import DriverStatus
from backend.app.services.state_manager import state_manager
from modules.driver_monitoring.driver_monitor import driver_monitor


class TestEmergencyWorkflow(unittest.TestCase):

    def test_emergency_trigger_and_cancel(self):
        state_manager.reset()
        self.assertFalse(state_manager.get_state().driver_responsive)

        # Trigger Emergency
        driver_monitor.trigger_emergency()
        self.assertEqual(state_manager.get_state().driver_status, DriverStatus.UNRESPONSIVE)
        self.assertTrue(state_manager.get_state().emergency_active)

        # Driver responds
        responded = driver_monitor.set_driver_responded()
        self.assertTrue(responded)
        self.assertTrue(state_manager.get_state().driver_responsive)
        self.assertEqual(state_manager.get_state().driver_status, DriverStatus.DRIVER_RESPONDED)

    def test_emergency_alert_service(self):
        from modules.alert.whatsapp_alert import emergency_alert_service
        emergency_alert_service.reset_session()
        self.assertFalse(emergency_alert_service.is_dispatched_for_session)

        # Phone formatting test
        self.assertEqual(emergency_alert_service._clean_phone("8073662914"), "+918073662914")
        self.assertEqual(emergency_alert_service._clean_phone("+918073662914"), "+918073662914")

        # Contact configuration
        emergency_alert_service.configure_contact("Mom", "9876543210")
        self.assertEqual(emergency_alert_service.contact_name, "Mom")
        self.assertEqual(emergency_alert_service.contact_phone, "+919876543210")

        # Message builder test
        msg, loc, hosp = emergency_alert_service._build_emergency_message()
        self.assertIn("AI DRIVER MONITORING: EMERGENCY ALERT", msg)
        self.assertIn("Mom", msg)

        # Session deduplication test
        emergency_alert_service.is_dispatched_for_session = True
        # trigger should return False when already dispatched
        result = emergency_alert_service.trigger_alert_if_unresponsive(force=False)
        self.assertFalse(result)

        # Reset session
        emergency_alert_service.reset_session()
        self.assertFalse(emergency_alert_service.is_dispatched_for_session)


if __name__ == "__main__":
    unittest.main()

