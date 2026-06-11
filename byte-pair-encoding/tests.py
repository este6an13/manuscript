import unittest

from main import get_stats, merge


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
            "given_single_valued_list_return_one_pair": {
                "ids": [1, 1, 1, 1, 1],
                "want": {(1, 1): 4},
            },
        }
        for name, case in tests.items():
            with self.subTest(name):
                self.assertEqual(get_stats(case["ids"]), case["want"])


class TestMerge(unittest.TestCase):
    def test(self):
        tests = {
            "given_empty_ids_return_empty": {
                "ids": [],
                "pair": (1, 2),
                "idx": 0,
                "want": [],
            },
            "given_one_id_return_one_id": {
                "ids": [1],
                "pair": (1, 2),
                "idx": 0,
                "want": [1],
            },
            "given_one_pair_return_one_id": {
                "ids": [1, 2],
                "pair": (1, 2),
                "idx": 0,
                "want": [0],
            },
            "given_pairs_return_merged_list": {
                "ids": [1, 2, 1, 2],
                "pair": (2, 1),
                "idx": 0,
                "want": [1, 0, 2],
            },
            "given_unmatched_pair_return_ids": {
                "ids": [1, 2, 3],
                "pair": (0, 0),
                "idx": 0,
                "want": [1, 2, 3],
            },
        }
        for name, case in tests.items():
            with self.subTest(name):
                self.assertEqual(
                    merge(case["ids"], case["pair"], case["idx"]), case["want"]
                )


if __name__ == "__main__":
    unittest.main()
