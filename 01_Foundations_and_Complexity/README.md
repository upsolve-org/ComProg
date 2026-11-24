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

Worked example on `3 1 4 1 5`, the first array of the overview visualizer. The pref table is `0 3 4 8 9 14`, so `sum(1, 3) = pref[4] - pref[1] = 9 - 3 = 6`:

```python
def build(a):
    pref = [0] * (len(a) + 1)
    for i, x in enumerate(a):
        pref[i + 1] = pref[i] + x
    return pref


pref = build([3, 1, 4, 1, 5])
print([pref[r + 1] - pref[l] for l in range(5) for r in range(l, 5)])
# [3, 4, 8, 9, 14, 1, 5, 6, 11, 4, 5, 10, 1, 6, 5] : all 15 range sums, two lookups each
```

Both queries are built once, so `Q` ranges cost $O(N + Q)$ instead of $O(NQ)$.

### 2. 2D Prefix Sums
Computes rectangular subgrid sums in $O(1)$ using the principle of inclusion-exclusion:
$$\text{Sum}(r_1, c_1, r_2, c_2) = P[r_2+1][c_2+1] - P[r_1][c_2+1] - P[r_2+1][c_1] + P[r_1][c_1]$$

### 3. Difference Arrays
Allows applying range addition updates $+V$ to an interval $[L, R]$ in $O(1)$ time, followed by a single $O(N)$ prefix scan at the end.
- `diff[L] += V`
- `diff[R + 1] -= V`

Three updates on a zero array of length 5, then one sweep. Each update is two writes; the sweep turns the markers into the real values:

```python
n = 5
diff = [0] * (n + 1)

for l, r, v in [(1, 3, 2), (0, 1, 5), (2, 4, 1)]:
    diff[l] += v
    diff[r + 1] -= v
print(diff)                       # [5, 2, -4, 0, -2, -1] : markers only

values, running = [], 0
for i in range(n):
    running += diff[i]
    values.append(running)
print(values)                     # [5, 7, 3, 3, 1]
```

Without the difference array the same three updates touch `2 + 2 + 3 = 7` positions; here they cost six writes.

---

## 📂 Included Source Files & Templates
- ⚡ [[01_Foundations_and_Complexity/fast_io_and_templates.py|fast_io_and_templates.py]] — Bulk tokenization & fast line reading
- ➕ [[01_Foundations_and_Complexity/prefix_sums_and_diff_arrays.py|prefix_sums_and_diff_arrays.py]] — 1D/2D Prefix sums & difference array
- 💡 [[01_Foundations_and_Complexity/practice_examples.py|practice_examples.py]] — Kadane's algorithm (O(N) max subarray sum)

---

⏮️ Previous: [[00_General_Advice_and_Practice/README|00 General Advice]] | 🏠 [[Home|Dashboard]] | ⏭️ Next: [[02_Binary_and_Ternary_Search/README|02 Binary & Ternary Search]]
