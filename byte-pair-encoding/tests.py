import unittest

from main import decode, encode, get_stats, merge, train


class TestGetStats(unittest.TestCase):
    def test(self):
        tests = {
            "given_empty_list_return_empty_stats": {"ids": [], "want": {}},
            "given_one_token_list_return_empty_stats": {"ids": [1], "want": {}},
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


class TestTrain(unittest.TestCase):
    def test(self):
        tests = {
            "given_vocab_size_256_return_empty_merges": {
                "text": "any text",
                "vocab_size": 256,
                "want": {},
            },
            "given_empty_text_return empty_merges": {
                "text": "",
                "vocab_size": 10000,
                "want": {},
            },
            "given_one_token_text_return_empty_merges": {
                "text": "a",  # 97
                "vocab_size": 10000,
                "want": {},  # no pairs to generate merges
            },
            "given_one_pair_text_return_merges_with_one_entry": {
                "text": "aa",
                "vocab_size": 10000,  # no matter vocab size, stopping cond. is [256]
                "want": {(97, 97): 256},
            },
            "given_some_text_return_merges_0": {
                "text": "aaa",
                "vocab_size": 10000,
                "want": {(97, 97): 256, (256, 97): 257},
            },
            "given_some_text_return_merges_1": {
                "text": "abc",
                "vocab_size": 10000,
                "want": {(97, 98): 256, (256, 99): 257},
            },
            "given_some_text_return_merges_2": {
                "text": "abcd",
                "vocab_size": 10000,
                "want": {(97, 98): 256, (256, 99): 257, (257, 100): 258},
            },
        }
        for name, case in tests.items():
            with self.subTest(name):
                self.assertEqual(train(case["text"], case["vocab_size"]), case["want"])


class TestEncode(unittest.TestCase):
    def test(self):
        tests = {
            "given_empty_text_return_empty_encoding": {
                "text": "",
                "merges": {(1, 2): 256, (256, 3): 257},  # any merges
                "want": [],
            },
            "given_one_token_text_return_one_token_encoding": {
                "text": "a",
                "merges": {(1, 2): 256, (256, 3): 257},  # any merges
                "want": [97],
            },
            "given_text_with_token_pair_not_in_merges_return_initial_encoding": {
                "text": "aa",  # (97, 97) not in merges
                "merges": {(1, 2): 256, (256, 3): 257},
                "want": [97, 97],  # merges table is not used to encode
            },
            "given_any_text_with_pairs_not_in_merges_return_initial_encoding": {
                "text": "abcde",
                "merges": {(1, 2): 256, (256, 3): 257},
                "want": [97, 98, 99, 100, 101],  # merges table is not used to encode
            },
            "given_text_with_some_pair_in_merges_return_encoding_using_merges_table": {
                "text": "abc",  # [97, 98, 99]
                "merges": {(1, 2): 256, (98, 99): 257},
                "want": [97, 257],  # (98, 99) -> 257
            },
            "given_a_correct_merges_table_return_last_token_0": {
                "text": "abc",
                "merges": {(97, 98): 256, (256, 99): 257},  # a correct merges table
                "want": [257],  # return last token
            },
            "given_a_correct_merges_table_return_last_token_1": {
                "text": "adbc",  # [97, 100, 98, 00]
                "merges": {
                    (97, 100): 256,
                    (256, 98): 257,
                    (257, 99): 258,
                },  # a correct merges table
                "want": [258],  # return last token
            },
        }
        for name, case in tests.items():
            with self.subTest(name):
                self.assertEqual(encode(case["text"], case["merges"]), case["want"])


class TestDecode(unittest.TestCase):
    def test(self):
        vocab = {i: bytes([i]) for i in range(256)}
        print(vocab[0] + vocab[1])
        tests = {
            "given_empty_merges_return_vocab_decoding_0": {
                "encoding": [97, 98, 99],
                "merges": {},
                "want": "abc",
            },
            "given_empty_merges_return_vocab_decoding_1": {
                "encoding": [32],  # space
                "merges": {},
                "want": " ",
            },
            "given_empty_merges_return_vocab_decoding_2": {
                "encoding": [48, 49, 50],
                "merges": {},
                "want": "012",
            },
            "given_empty_merges_return_vocab_decoding_3": {
                "encoding": [0, 1],
                "merges": {},
                "want": "\x00\x01",  # utf-8 decoding of 0, 1 tokens
            },
            "given_tokens_outside_vocab_and_merges_return_placeholders": {
                "encoding": [256, 257],
                "merges": {},  # vocab goes up to 256
                "want": "**",
            },
            "given_tokens_in_merges_return_decoding_0": {
                "encoding": [257],
                "merges": {(97, 98): 256, (256, 99): 257},
                "want": "abc",  # \x97\x98 (256) + \x99
            },
            "given_tokens_in_merges_return_decoding_1": {
                "encoding": [240, 159, 154, 128],
                "merges": {(240, 159): 256, (256, 154): 257, (257, 128): 258},
                "want": "🚀",
            },
        }
        for name, case in tests.items():
            with self.subTest(name):
                self.assertEqual(decode(case["encoding"], case["merges"]), case["want"])


if __name__ == "__main__":
    unittest.main()
