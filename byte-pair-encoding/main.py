def get_stats(ids):
    stats = {}
    for i in range(len(ids) - 1):
        pair = (ids[i], ids[i + 1])
        if stats.get(pair) is None:
            stats[pair] = 1
        else:
            stats[pair] += 1
    return stats


def merge(ids, pair, idx):
    new_ids = []
    i = 0
    while i < len(ids):
        if i + 1 == len(ids):
            new_ids.append(ids[i])
            break
        curr = (ids[i], ids[i + 1])
        if curr == pair:
            new_ids.append(idx)
            i += 2
        else:
            new_ids.append(ids[i])
            i += 1
    return new_ids


def train(text, vocab_size):
    num_merges = vocab_size - 256  # num of merged to make to reach vocab size
    merges = {}
    encoding = list(text.encode("utf-8"))
    token = 256
    for _ in range(num_merges):
        stats = get_stats(encoding)
        if len(stats) == 0:  # if we get one token: [256] for example
            break
        most_freq_pair = max(stats, key=stats.get)
        freq = stats[most_freq_pair]
        if freq == 0:
            continue
        encoding = merge(encoding, most_freq_pair, token)
        merges[most_freq_pair] = token
        token += 1
    return merges


def encode(text, merges):
    encoding = list(text.encode("utf-8"))
    while len(encoding) >= 2:
        stats = get_stats(encoding)
        # find the lowest merge rank
        # the pair that was merged earliest during training,
        # which has the smallest token ID
        min_rank = float("inf")
        min_p = None
        # find the pair p in stats that minimizes merges.get(p, float('inf'))
        for p, _ in stats.items():
            rank = merges.get(p, float("inf"))
            if rank <= min_rank:
                min_rank = rank
                min_p = p
        best_pair = min_p
        if min_rank == float("inf"):
            break
        encoding = merge(encoding, best_pair, merges[best_pair])
    return encoding


def decode(encoding, merges):
    vocab = {i: bytes([i]) for i in range(256)}
    sorted_merges = sorted(merges.items(), key=lambda item: item[1])
    for pair, idx in sorted_merges:
        vocab[idx] = (
            vocab[pair[0]] + vocab[pair[1]]
        )  # (97, 98): 256 -> vocab[256] -> b'\x97\x98'
    bytes_arr = []
    for idx in encoding:
        bytes_arr.append(
            vocab.get(idx, b"*")
        )  # deliberate placeholder for this particular exercise
    bytes_str = b"".join(bytes_arr)
    text = bytes_str.decode("utf-8", errors="replace")
    return text


if __name__ == "__main__":
    # ids = [1, 2, 3]
    # stats = get_stats(ids)
    # print(stats)

    # ids = [1, 2, 3, 1, 2, 3]
    # merged = merge(ids, (1, 2), 9)
    # print(merged)

    # text = "hello"
    # _bytes = list(text.encode("utf-8"))
    # print(_bytes)

    text = "hello world! 🚀 こんにちは"
    merges = train(text, 300)
    encoding = encode(text, merges)
    print(encoding)

    decoding = decode(encoding, merges)
    print(decoding)
