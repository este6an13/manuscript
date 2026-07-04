# 🖋️ Manuscript

> **"Reclaiming understanding in an era where code generation is abundant."**

**Manuscript** is a personal notebook and codebase dedicated to collecting algorithms written entirely from first principles, by hand (typewritten). 

This repository serves as a deliberate practice space to master the intersections of **Computer Science, Mathematics, and Statistics**. By implementing these algorithms step-by-step, I want to build deep intuition for the mechanisms underlying modern software and artificial intelligence.

I'll focus on understanding the algorithms myself instead of optimizing for code style, performance (if not relevant for the algorithm), or using functional constructs. So you will see code that may look a bit clunky.

**URL:** 🌐 [https://este6an13.github.io/manuscript/](https://este6an13.github.io/manuscript/)

---

## 📚 Algorithm Directory

Here is the current index of implemented algorithms and concepts:

| Category | Algorithm | Description | Directory |
| :--- | :--- | :--- | :--- |
| **Clustering / ML** | **K-Means Clustering** | Unsupervised clustering algorithm to partition data points into K clusters based on Euclidean distance. | [`/kmeans-clustering`](./kmeans-clustering) |
| **Linear Algebra** | **Linear Algebra Utilities** | Vector and matrix operations implemented from scratch (dot/outer product, norm, transpose, matrix multiplication). | [`/linear_algebra`](./linear_algebra) |
| **Linear Algebra** | **Power Iteration & Deflation** | Iterative algorithm to compute eigenvalues and eigenvectors of a symmetric matrix. | [`/power_iteration`](./power_iteration) |
| **Linear Algebra / ML** | **Singular Value Decomposition (SVD)** | Matrix factorization method to decompose a matrix into singular vectors and singular values. | [`/singular-value-decomposition`](./singular-value-decomposition) |
| **NLP / Semantics** | **Co-occurrence Matrix & PPMI** | Constructing word co-occurrence matrices from text and computing Positive Pointwise Mutual Information (PPMI). | [`/co-occurrence-matrix`](./co-occurrence-matrix) |
| **NLP / Tokenization** | **Byte Pair Encoding (BPE)** | The subword tokenization algorithm used by GPT and other modern LLMs to compress text into token IDs. | [`/byte-pair-encoding`](./byte-pair-encoding) |
| **NLP / Tokenization** | **N-gram Tokenization** | Character-level and word-level N-gram generator to split text into sequence patterns of length N. | [`/ngram-tokenization`](./ngram-tokenization) |
| **Optimization / ML** | **Gradient Descent** | First-principles multi-variable gradient descent optimizer using custom linear algebra and geometry utilities. | [`/gradient_descent`](./gradient_descent) |
| **Geometry** | **Geometry Utilities** | Basic geometric calculations, including element-wise Euclidean distance for arbitrary dimensions, implemented from scratch. | [`/geometry`](./geometry) |

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

*Note: The "Manuscript" UI for the GitHub Pages site (in `docs/`) was entirely AI-generated. This purely aesthetic addition does not contradict the project's philosophy, as the core algorithms themselves remain strictly hand-written and studied from first principles.*

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
