---
tags:
  - cp/algorithms
  - cp/binary-search
---

[[Home|🏠 Dashboard]] ❯ **Module 02: Binary and Ternary Search**

---

# Module 02: Binary and Ternary Search

*References from [[12_Reference_and_Catalog/codeforces_catalog_full.md|Codeforces Catalog]]:*
- [EDU: Binary Search by pashka](https://codeforces.com/blog/entry/67568)
- [Bin search and relative error by Um_nik](https://codeforces.com/blog/entry/63085)
- [Multi-dimensional ternary search by adamant](https://codeforces.com/blog/entry/60702)

Binary Search is one of the most versatile and powerful algorithmic paradigms in competitive programming. It extends far beyond finding an element in a sorted list: its primary competitive use is **Binary Search on Answer**.

---

## 🔍 1. The Monotonicity Condition

Binary search can be applied to any predicate $P(x) \in \{0, 1\}$ (or $\{\text{False}, \text{True}\}$) as long as $P(x)$ is **monotonic**:
$$\text{False, False, False, } \dots \text{ False, True, True, True} \dots$$
Or the reverse:
$$\text{True, True, True, } \dots \text{ True, False, False, False} \dots$$

### The Invariant Loop Pattern
To avoid off-by-one errors and infinite loops:
```python
lo = min_possible
hi = max_possible
ans = -1

while lo <= hi:
    mid = (lo + hi) // 2
    if check(mid):
        ans = mid
        # To find the minimum valid answer:
        hi = mid - 1
        # (Or to find maximum valid answer: lo = mid + 1)
    else:
        lo = mid + 1
```

### Worked Example
The test array is `[1, 10, 10, 10, 20, 30]` and the predicate is `a[i] >= 10`. Wrapping it in one function makes the loop reusable for "first $\ge x$", "first $\ge$ a computed bound", and so on:

```python
a = [1, 10, 10, 10, 20, 30]


def first_at_least(a, target):
    lo, hi, ans = 0, len(a) - 1, -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] >= target:
            ans = mid        # remember it, then look further left
            hi = mid - 1
        else:
            lo = mid + 1
    return ans


print(first_at_least(a, 10), "·", a[first_at_least(a, 10)], "·", first_at_least(a, 15))
```

The trace probes `mid = 2` (holds, `ans = 2`), `mid = 0` (fails), `mid = 1` (holds, `ans = 1`), then stops with `lo = 2 > hi = 0`. Three probes settle a six-element array; the duplicate `10`s are why the boundary is `1` and not `2`.

---

## ⚡ 2. Built-in Python: `bisect`

The standard library `bisect` module is implemented in optimized C:
- `bisect.bisect_left(arr, x)`: Returns the first index where `arr[i] >= x` (C++ `std::lower_bound`).
- `bisect.bisect_right(arr, x)`: Returns the first index where `arr[i] > x` (C++ `std::upper_bound`).

---

## 📈 3. Floating-Point Binary Search

For continuous mathematical functions, avoid `while abs(hi - lo) > 1e-9` because floating-point precision loss can cause infinite loops. Instead, run a fixed number of iterations (e.g. 60–100 iterations provides $< 10^{-18}$ error):
```python
lo = 0.0
hi = 1e9
for _ in range(80):
    mid = (lo + hi) / 2.0
    if check(mid):
        hi = mid
    else:
        lo = mid
```

---

## 🏔️ 4. Ternary Search (Unimodal Functions)

Used when a function $f(x)$ is strictly increasing then strictly decreasing (or vice versa), having a single maximum (or minimum).
By evaluating two points $m_1 = lo + \frac{hi - lo}{3}$ and $m_2 = hi - \frac{hi - lo}{3}$, one third of the search space is eliminated in each iteration.

---

## 📂 Included Source Files & Templates
- 🔍 [[02_Binary_and_Ternary_Search/binary_search_templates.py|binary_search_templates.py]] — Invariant BS, `bisect`, answer predicate search
- 🏔️ [[02_Binary_and_Ternary_Search/ternary_search.py|ternary_search.py]] — Discrete & float ternary search
- 💡 [[02_Binary_and_Ternary_Search/practice_problems.py|practice_problems.py]] — Aggressive Cows (maximum minimum distance)

---

⏮️ Previous: [[01_Foundations_and_Complexity/README|01 Foundations & Complexity]] | 🏠 [[Home|Dashboard]] | ⏭️ Next: [[03_Two_Pointers_and_Sliding_Window/README|03 Two Pointers & Sliding Window]]
