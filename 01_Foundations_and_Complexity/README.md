---
tags:
  - cp/foundations
  - cp/complexity
---

[[Home|🏠 Dashboard]] ❯ **Module 01: Foundations & Complexity**

---

# Module 01: Foundations & Complexity

Before diving into advanced data structures and graph theory, you must develop an instinctive understanding of **Time and Space Complexity** and standard algorithmic primitives like **Prefix Sums** and **Difference Arrays**.

---

## ⏱️ Python Speed & Big-O Complexity

In competitive programming, the golden rule of thumb for time limits is usually **1.0 to 2.0 seconds**.

### Operations per Second Rule of Thumb
- **C++:** $\approx 10^8$ simple operations per second.
- **Python 3 / PyPy 3:** $\approx 10^7$ to $3 \times 10^7$ operations per second.

### Constraint to Complexity Matcher

| Constraint $N$ | Acceptable Time Complexity | Algorithms / Techniques |
|---|---|---|
| $N \le 10$ | $O(N!)$ or $O(N^2 \cdot 2^N)$ | Full permutations, TSP, brute force |
| $N \le 20$ | $O(2^N)$ or $O(N \cdot 2^N)$ | Bitmask DP, meet-in-the-middle |
| $N \le 500$ | $O(N^3)$ | Floyd-Warshall, matrix multiplication, interval DP |
| $N \le 2000$ | $O(N^2)$ | Double nested loops, 2D DP, all pairs |
| $N \le 2 \times 10^5$ | $O(N \log N)$ or $O(N)$ | Sorting, Segment Tree, DSU, Binary Search, Two Pointers |
| $N \le 10^7$ | $O(N)$ | Linear sieve, single pass, prefix sum |
| $N \le 10^9$ | $O(\sqrt{N})$ or $O(\log N)$ or $O(1)$ | Primality testing, binary search, modular math |

---

## 📊 Essential Primitives

### 1. Prefix Sums
Allows calculating the sum of elements in any range $[L, R]$ in $O(1)$ time after $O(N)$ precomputation.
$$\text{sum}(L, R) = \text{pref}[R + 1] - \text{pref}[L]$$

### 2. 2D Prefix Sums
Computes rectangular subgrid sums in $O(1)$ using the principle of inclusion-exclusion:
$$\text{Sum}(r_1, c_1, r_2, c_2) = P[r_2+1][c_2+1] - P[r_1][c_2+1] - P[r_2+1][c_1] + P[r_1][c_1]$$

### 3. Difference Arrays
Allows applying range addition updates $+V$ to an interval $[L, R]$ in $O(1)$ time, followed by a single $O(N)$ prefix scan at the end.
- `diff[L] += V`
- `diff[R + 1] -= V`

---

## 📂 Included Source Files & Templates
- ⚡ [[01_Foundations_and_Complexity/fast_io_and_templates.py|fast_io_and_templates.py]] — Bulk tokenization & fast line reading
- ➕ [[01_Foundations_and_Complexity/prefix_sums_and_diff_arrays.py|prefix_sums_and_diff_arrays.py]] — 1D/2D Prefix sums & difference array
- 💡 [[01_Foundations_and_Complexity/practice_examples.py|practice_examples.py]] — Kadane's algorithm (O(N) max subarray sum)

---

⏮️ Previous: [[00_General_Advice_and_Practice/README|00 General Advice]] | 🏠 [[Home|Dashboard]] | ⏭️ Next: [[02_Binary_and_Ternary_Search/README|02 Binary & Ternary Search]]
