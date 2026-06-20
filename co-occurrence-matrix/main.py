from math import log2
from string import punctuation


def format_punctuation(text, chars):
    for char in chars:
        text = text.replace(char, f" {char} ")
    return text


def get_words(text: str) -> list[str]:
    text = text.lower()
    text = format_punctuation(text, punctuation)
    words = text.split()
    return words


def build_vocab(text: str) -> tuple[dict[str, int], dict[int, str]]:
    words = get_words(text)
    word_to_id = {}
    id_to_word = {}
    idx = 0
    for word in words:
        if word in word_to_id:
            continue
        word_to_id[word] = idx
        id_to_word[idx] = word
        idx += 1
    return word_to_id, id_to_word


def init_matrix(N: int) -> list[list[int]]:
    matrix = [[0 for _ in range(N)] for _ in range(N)]
    return matrix


def compute_sums(matrix):
    N = len(matrix)
    Sx = [0 for _ in range(N)]  # rows sums
    Sy = [0 for _ in range(N)]  # columns sums
    S = 0  # full matrix sum
    for x in range(N):
        for y in range(N):
            Sxy = matrix[x][y]
            Sx[x] += Sxy
            Sy[y] += Sxy
            S += Sxy
    return Sx, Sy, S


def pmi(Pxy: float, Px: float, Py: float) -> float:
    if Pxy == 0 or Px == 0 or Py == 0:
        return 0
    return log2(Pxy / (Px * Py))  # log(0) is undefined


def ppmi(pmi: float) -> float:
    return max(0, pmi)


# PPMI: Positive Pointwise Mutual Information
def compute_ppmi_matrix(matrix: list[list[int]]) -> list[list[float]]:
    N = len(matrix)
    ppmi_matrix = init_matrix(N)
    Sx, Sy, S = compute_sums(matrix)
    if S == 0:
        return ppmi_matrix  # prevent dividing by zero
    for x in range(N):
        for y in range(N):
            Sxy = matrix[x][y]  # count of co-occurrences of (x, y)
            Pxy = Sxy / S  # probability of (x, y) co-occurence
            Px = Sx[x] / S
            Py = Sy[y] / S
            ppmi_matrix[x][y] = ppmi(pmi(Pxy, Px, Py))
    return ppmi_matrix


def build_co_occurrence_matrix(text, window_size=1):
    word_to_id, _ = build_vocab(text)
    N = len(word_to_id)
    matrix = init_matrix(N)
    words = get_words(text)
    W = len(words)
    for i in range(W):
        window = (
            words[max(i - window_size, 0) : i]  # max to prevent having negative indexes
            + words[
                i + 1 : min(i + 1 + window_size, W)
            ]  # min to prevent having out-of-bound indexes
        )
        word = words[i]
        word_id = word_to_id[word]
        for co_occurrent_word in window:
            co_occurrent_word_id = word_to_id[co_occurrent_word]
            matrix[word_id][co_occurrent_word_id] += 1
    return matrix


if __name__ == "__init__":
    text = """Sitting alone in a café without distractions only gets better when there is something to write on. Not with a keyboard. You must use your single hand to write, not two. Ideally, with a pen on paper."""
    # text = "a b c d"

    vocab = build_vocab(text)
    print(vocab)

    raw_matrix = build_co_occurrence_matrix(text, 2)
    ppmi_matrix = compute_ppmi_matrix(raw_matrix)
    print(raw_matrix)
    print(ppmi_matrix)
