# 🪙 Byte Pair Encoding (BPE)

Byte Pair Encoding (BPE) is a simple yet powerful data compression algorithm that has become the standard subword tokenization method for modern Large Language Models (such as GPT-2, GPT-3, GPT-4, and Llama).

This directory contains a complete, hand-written implementation of BPE from first principles, operating on raw UTF-8 bytes.

---

## 💡 How It Works

Traditional tokenization splits text on whitespace or punctuation, which leads to large vocabularies and an inability to handle out-of-vocabulary (OOV) words. BPE solves this by starting with character-level (or byte-level) tokens and iteratively merging the most frequent adjacent pairs.

### 1. Initialization
- The vocabulary is initialized with the 256 possible byte values ($0$ to $255$), representing all basic ASCII and raw UTF-8 byte sequences.
- Input text is converted to a list of bytes. For example, `"hello"` becomes `[104, 101, 108, 108, 111]`.

### 2. Training (Vocabulary Building)
During training, we build a dictionary of **merges**:
1. Compute the frequencies of all adjacent pairs in the current byte list.
2. Identify the most frequent pair, e.g., `(108, 108)` for `"ll"`.
3. Replace all occurrences of this pair with a new token ID (starting at $256$).
4. Record the merge rule: `(108, 108) -> 256`.
5. Repeat steps 1–4 until the target vocabulary size is reached or no more merges are possible.

### 3. Encoding (Tokenization)
To tokenize new text:
1. Convert the text to raw bytes.
2. Find all adjacent pairs.
3. Out of all current pairs, identify the one that has the **lowest merge rank** (i.e., the pair that was merged earliest during training, corresponding to the smallest token ID in our merges dictionary).
4. Merge that pair.
5. Repeat until no more merge rules can be applied.

### 4. Decoding (De-tokenization)
To reconstruct the original string:
1. Build a lookup dictionary mapping each token ID ($0$ to $V-1$) to its original byte string.
2. Map each token ID in the encoded sequence to its bytes.
3. Concatenate all bytes and decode them back into a UTF-8 string.

---

## 🛠️ Code Walkthrough

The implementation is located in [`main.py`](./main.py) and consists of the following primary functions:

- **`get_stats(ids)`**: Counts frequencies of all consecutive pairs in a sequence of token IDs.
- **`merge(ids, pair, idx)`**: Iterates through the list of IDs and replaces any occurrence of `pair` with the new token `idx`.
- **`train(text, vocab_size)`**: Learns the merge rules up to the desired `vocab_size` (starting above 256).
- **`encode(text, merges)`**: Encodes an input string into token IDs using the learned merges, prioritizing early merge rules.
- **`decode(encoding, merges)`**: Converts token IDs back to a human-readable UTF-8 string.

### Example Usage

```python
from main import train, encode, decode

text = "hello world! 🚀 こんにちは"

# Train on a sample corpus to expand vocab size to 300
merges = train(text, vocab_size=300)

# Encode text to tokens
tokens = encode(text, merges)
print("Encoded tokens:", tokens)

# Decode tokens back to string
decoded_text = decode(tokens, merges)
print("Decoded string:", decoded_text)
# Output: "hello world! 🚀 こんにちは"
```

---

## 📚 References
- [Neural Machine Translation of Rare Words with Subword Units (Sennrich et al., 2015)](https://arxiv.org/abs/1508.07909)
- [Karpathy's Let's build the GPT Tokenizer](https://github.com/karpathy/minbpe)
