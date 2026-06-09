# 🖋️ Manuscript

> **"In the age of AI, code is cheap, but comprehension is priceless."**

**Manuscript** is a personal notebook and codebase dedicated to collecting algorithms written entirely from first principles, by hand (typewritten). 

This repository serves as a deliberate practice space to master the intersections of **Computer Science, Mathematics, and Statistics**. By implementing these algorithms step-by-step, I want to build deep intuition for the mechanisms underlying modern software and artificial intelligence.

I'll focus on understanding the algorithms myself instead of optimizing for code style, performance (if not relevant for the algorithm), or using functional constructs. So you will see code that may look a bit clunky.

---

## 📚 Algorithm Directory

Here is the current index of implemented algorithms and concepts:

| Category | Algorithm | Description | Directory |
| :--- | :--- | :--- | :--- |
| **NLP / Tokenization** | **Byte Pair Encoding (BPE)** | The subword tokenization algorithm used by GPT and other modern LLMs to compress text into token IDs. | [`/byte-pair-encoding`](./byte-pair-encoding) |

---

## 🗂️ Repository Structure

Each algorithm is self-contained in its own directory:

```text
manuscript/
├── byte-pair-encoding/        # Example Algorithm folder
│   ├── main.py                # Core implementation
│   ├── tests.py               # Verification/Tests (currently empty is OK)
│   └── README.md              # Algorithm-specific documentation
├── CLAUDE.md                  # AI Assistant guidelines (critical for repo philosophy)
└── README.md                  # This repository index
```

---

## 🧭 Philosophy & Guidelines

1. **First Principles**: No high-level frameworks for core logic. I implement the math and logic directly.
2. **Focus on Comprehension, Not Polish**: I focus on understanding the algorithms myself instead of optimizing for code style, performance (if not relevant for the algorithm), or using functional constructs. So the code may look a bit clunky—and that is perfectly fine.
3. **Typewritten by Hand**: I type out the code manually, line-by-line, to build muscle memory and active reasoning at every step.
4. **Learning with AI, Not Copying**: I use LLMs to iterate, ask questions, learn, and refine the code. The AI is here to help me learn, but **not to write the code for me**. For details on this relationship, see my [CLAUDE.md](./CLAUDE.md) guidelines (copied from the [Stanford CS336 AI Agent Guidelines](https://github.com/stanford-cs336/assignment1-basics/blob/main/CLAUDE.md)).

---

## 🛠️ How to Explore

To run any implementation:
1. Navigate to the algorithm's directory.
2. Run the main script using Python:
   ```bash
   python main.py
   ```
3. Run tests (if implemented) using `unittest` or `pytest`:
   ```bash
   python -m unittest tests.py
   ```
