import unittest
from math import sqrt

from utils import euclidean_distance


class TestCalculateEuclideanDistance(unittest.TestCase):
    def test(self):
        f = euclidean_distance
        tests = {
            "given_equal_points_return_zero": {"p": [1.0], "q": [1.0], "want": 0.0},
            "given_empty_points_raise_error": {"p": [], "q": [], "error": "zero"},
            "given_different_length_points_raise_error": {
                "p": [1.0],
                "q": [1.0, 2.0],
                "error": "dimension",
            },
            "given_points_return_distance_0": {"p": [1.0], "q": [2.0], "want": 1.0},
            "given_points_return_distance_1": {
                "p": [0.0, 0.0],
                "q": [1.0, 1.0],
                "want": sqrt(2),  # hypotenuse of unit triangle
            },
        }
        for name, case in tests.items():
            if "error" in case:
                with self.assertRaisesRegex(ValueError, case["error"]):
                    f(case["p"], case["q"])
                continue
            with self.subTest(name):
                self.assertEqual(f(case["p"], case["q"]), case["want"])


if __name__ == "__main__":
    unittest.main()
