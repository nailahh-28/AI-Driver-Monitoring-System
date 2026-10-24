import unittest
from modules.hospital.hospital_finder import HospitalFinder


class TestHospitalFinder(unittest.TestCase):

    def test_hospital_finder_fallback(self):
        finder = HospitalFinder()
        hospital = finder.find_nearest_hospital(12.971820, 77.594003)
        self.assertIsNotNone(hospital)
        self.assertNotEqual(hospital.name, "")
        self.assertGreaterEqual(hospital.distance_km, 0.0)

    def test_hospital_distance_sorting(self):
        finder = HospitalFinder()
        hospital = finder.find_nearest_hospital(12.968155, 77.595042)
        self.assertIsNotNone(hospital)
        self.assertLess(hospital.distance_km, 0.5)


if __name__ == "__main__":
    unittest.main()
