from string import punctuation


def format_punctuation(text, chars):
    for char in chars:
        text = text.replace(char, f" {char} ")
    return text


def generate_char_level_ngrams(text: str, n: int):
    joint_text = "_".join(text.lower().split())
    tokens = []
    L = len(joint_text)
    # n=3; 'abcd'; last iter starts from idx 1 (4-3+1, and -1 is 1); that is 'b' to capture 'bcd'
    for i in range(L - n + 1):
        tokens.append(tuple(joint_text[i : i + n]))  # 'abc' -> ('a', 'b', 'c')
    return tokens


def generate_word_level_ngrams(text: str, n: int):
    text = format_punctuation(text, punctuation)  # "!"#$%&'()*+,-./:;<=>?
    split_text = text.lower().split()
    tokens = []
    L = len(split_text)
    for i in range(L - n + 1):
        tokens.append(tuple(split_text[i : i + n]))  # ['the', 'cat'] -> ('the', 'cat')
    return tokens


def generate_ngrams(text: str, n: int, level="char") -> list[tuple[str, ...]]:
    if n <= 0:
        raise ValueError("n must be greater than 0")
    match level:
        case "char":
            return generate_char_level_ngrams(text, n)
        case "word":
            return generate_word_level_ngrams(text, n)
        case _:
            raise ValueError("wrong level")


if __name__ == "__main__":
    text = """Sitting alone in a café without distractions only gets better when there is something to write on. Not with a keyboard. You must use your single hand to write, not two. Ideally, with a pen on paper."""

    # ngrams = generate_ngrams(text, 1, "word")

    ngrams = generate_ngrams(text, 2, "word")

    # ngrams = generate_ngrams(text, 3, "char")

    # ngrams = generate_ngrams(text, 4, "char")

    # ngrams = generate_ngrams(text, 5, "char")

    print(ngrams)
    print(len(ngrams))
