import unittest

from main import get_stats


class TestGetStats(unittest.TestCase):
    def test(self):
        tests = {
            "given_empty_list_return_empty_stats": {"ids": [], "want": {}},
            "given_list_return_stats_0": {
                "ids": [1, 2, 3],
                "want": {(1, 2): 1, (2, 3): 1},
            },
            "given_list_return_stats_1": {
                "ids": [1, 2, 1, 2],
                "want": {(1, 2): 2, (2, 1): 1},
            },
        }
        for name, case in tests.items():
            with self.subTest(name):
                self.assertEqual(get_stats(case["ids"]), case["want"])


if __name__ == "__main__":
    unittest.main()
