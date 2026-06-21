import unittest

from main import (
    format_punctuation,
    generate_char_level_ngrams,
    generate_word_level_ngrams,
)


class TestFormatPunctuation(unittest.TestCase):
    def test(self):
        f = format_punctuation
        tests = {
            "given_empty_text_return_empty_text": {
                "text": "",
                "chars": "any",
                "want": "",
            },
            "given_text_with_no_puntuation_return_same_text": {
                "text": "a b c d",
                "chars": ".",
                "want": "a b c d",
            },
            "given_text_with_punctuation_return_formatted_text_0": {
                "text": "a.b.c.d",
                "chars": ".",
                "want": "a . b . c . d",
            },
            "given_text_with_punctuation_return_formatted_text_1": {
                "text": "a. b. c. d",
                "chars": ".",
                "want": "a .  b .  c .  d",
            },
            "given_text_with_punctuation_return_formatted_text_2": {
                "text": "¿a.b.c.d?",
                "chars": ".¿?",
                "want": " ¿ a . b . c . d ? ",
            },
            "given_text_with_unmatched_punctuation_return_same_text": {
                "text": "a.b.c.d",
                "chars": "_",  # no matching punctuation char
                "want": "a.b.c.d",
            },
            "given_only_punctuated_text_return_formatted_text": {
                "text": ".....",
                "chars": ".",
                "want": " .  .  .  .  . ",
            },
        }
        for name, case in tests.items():
            with self.subTest(name):
                self.assertEqual(f(case["text"], case["chars"]), case["want"])


class TestGenerateCharLevelNGrams(unittest.TestCase):
    def test(self):
        f = generate_char_level_ngrams
        tests = {
            "given_empty_text_return_empty_list": {
                "text": "",
                "n": 3,  # any
                "want": [],
            },
            "given_one_char_and_unigram_return_one_unigram": {
                "text": "a",
                "n": 1,
                "want": [("a",)],
            },
            "given_one_char_and_bigram_return_empty_list": {
                "text": "a",
                "n": 2,  # no bigrams in text
                "want": [],
            },
            "given_two_chars_and_trigram_return_empty_list": {
                "text": "ab",
                "n": 3,  # no trigrams in text
                "want": [],
            },
            "given_two_chars_and_bigram_return_one_bigram": {
                "text": "ab",
                "n": 2,
                "want": [("a", "b")],
            },
            "given_text_and_n_return_ngrams_0": {
                "text": "abc",
                "n": 2,
                "want": [("a", "b"), ("b", "c")],
            },
            "given_text_and_n_return_ngrams_1": {
                "text": "a c",
                "n": 2,
                "want": [("a", "_"), ("_", "c")],
            },
            "given_text_and_n_return_ngrams_2": {
                "text": "a.b",
                "n": 2,
                "want": [("a", "."), (".", "b")],
            },
            "given_text_and_n_return_ngrams_3": {
                "text": "a _",
                "n": 2,
                "want": [("a", "_"), ("_", "_")],
            },
            "given_text_and_n_return_ngrams_4": {
                "text": "abcd",
                "n": 3,
                "want": [("a", "b", "c"), ("b", "c", "d")],
            },
        }
        for name, case in tests.items():
            with self.subTest(name):
                self.assertEqual(f(case["text"], case["n"]), case["want"])


class TestGenerateWordLevelNGrams(unittest.TestCase):
    def test(self):
        f = generate_word_level_ngrams
        tests = {
            "given_empty_text_return_empty_list": {
                "text": "",
                "n": 3,  # any
                "want": [],
            },
            "given_one_word_and_unigram_return_one_word_unigram": {
                "text": "word",
                "n": 1,
                "want": [("word",)],
            },
            "given_one_word_and_bigram_return_empty_list": {
                "text": "word",
                "n": 2,  # no bigrams in text
                "want": [],
            },
            "given_two_words_and_trigram_return_empty_list": {
                "text": "two words",
                "n": 3,  # no trigrams in text
                "want": [],
            },
            "given_two_words_and_bigram_return_one_bigram": {
                "text": "hello world",
                "n": 2,
                "want": [("hello", "world")],
            },
            "given_text_and_n_return_ngrams_0": {
                "text": "happy new year",
                "n": 2,
                "want": [("happy", "new"), ("new", "year")],
            },
            "given_text_and_n_return_ngrams_1": {
                "text": "hello world!",  # ! is puntuaction: a separate token
                "n": 2,
                "want": [("hello", "world"), ("world", "!")],
            },
            "given_text_and_n_return_ngrams_2": {
                "text": "HAPPY NEW YEAR!",  # tokens get lowecased
                "n": 3,
                "want": [("happy", "new", "year"), ("new", "year", "!")],
            },
        }
        for name, case in tests.items():
            with self.subTest(name):
                self.assertEqual(f(case["text"], case["n"]), case["want"])


if __name__ == "__main__":
    unittest.main()
