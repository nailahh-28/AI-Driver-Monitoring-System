import unittest
from modules.gps.gps_service import GpsService


class TestGpsService(unittest.TestCase):

    def test_haversine_distance_known_points(self):
        gps = GpsService()
        # Distance between Bangalore center (12.9716, 77.5946) and MG Road (12.9756, 77.6066) ~ 1.3 km
        dist = gps.haversine_distance(12.9716, 77.5946, 12.9756, 77.6066)
        self.assertTrue(1.0 < dist < 2.0)

    def test_carla_to_gps_conversion(self):
        gps = GpsService(ref_lat=12.971820, ref_lng=77.594003)
        lat, lng = gps.carla_to_gps(0.0, 0.0)
        self.assertEqual(lat, 12.971820)
        self.assertEqual(lng, 77.594003)

        lat_north, lng_north = gps.carla_to_gps(0.0, 111.0)
        self.assertGreater(lat_north, lat)


if __name__ == "__main__":
    unittest.main()
