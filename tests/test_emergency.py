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

    def test_driver_cannot_respond_when_no_emergency(self):
        state_manager.reset()
        responded = driver_monitor.set_driver_responded()
        self.assertFalse(responded)


if __name__ == "__main__":
    unittest.main()
