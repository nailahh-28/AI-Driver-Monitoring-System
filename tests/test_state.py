import unittest
from backend.app.models.schemas import DriverStatus
from backend.app.services.state_manager import state_manager


class TestStateManager(unittest.TestCase):

    def test_state_manager_update_and_reset(self):
        state_manager.reset()
        initial_state = state_manager.get_state()
        self.assertEqual(initial_state.vehicle_speed, 60.0)
        self.assertEqual(initial_state.driver_status, DriverStatus.NORMAL)

        state_manager.update_state(vehicle_speed=42.5, driver_status=DriverStatus.DROWSY)
        updated = state_manager.get_state()
        self.assertEqual(updated.vehicle_speed, 42.5)
        self.assertEqual(updated.driver_status, DriverStatus.DROWSY)
        self.assertGreaterEqual(len(updated.speed_history), 1)

        state_manager.reset()
        reset_state = state_manager.get_state()
        self.assertEqual(reset_state.vehicle_speed, 60.0)
        self.assertEqual(reset_state.driver_status, DriverStatus.NORMAL)
        self.assertEqual(len(reset_state.speed_history), 0)


if __name__ == "__main__":
    unittest.main()
