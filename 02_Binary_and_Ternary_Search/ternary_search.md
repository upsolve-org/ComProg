---
tags:
  - cp/code
  - cp/binary
---

[[ComProg/Home|🏠 Dashboard]] ❯ [[ComProg/02_Binary_and_Ternary_Search/README|02_Binary_and_Ternary_Search]] ❯ **Ternary Search**

---

# Ternary Search

> [!abstract] Implementation Note
> This note contains the complete, battle-tested Python implementation of **Ternary Search**.
> Source file: `ComProg/02_Binary_and_Ternary_Search/ternary_search.py`
> Run test runner: `python3 run_tests.py ComProg/02_Binary_and_Ternary_Search/ternary_search.py`

---

## 🐍 Python Implementation

```python
"""
Ternary Search in Python: Finding the extremum of a unimodal / convex function.
"""

def ternary_search_min_float(lo, hi, f, iterations=100):
    """
    Finds x in [lo, hi] that minimizes f(x) where f is strictly convex (U-shaped).
    """
    left, right = float(lo), float(hi)
    for _ in range(iterations):
        m1 = left + (right - left) / 3.0
        m2 = right - (right - left) / 3.0
        if f(m1) < f(m2):
            right = m2
        else:
            left = m1
    return (left + right) / 2.0

def ternary_search_min_int(lo, hi, f):
    """
    Finds integer x in [lo, hi] that minimizes discrete unimodal function f(x).
    """
    left, right = lo, hi
    while right - left > 2:
        m1 = left + (right - left) // 3
        m2 = right - (right - left) // 3
        if f(m1) < f(m2):
            right = m2
        else:
            left = m1
    
    # Check remaining candidates
    best_x = left
    best_val = f(left)
    for cand in range(left + 1, right + 1):
        v = f(cand)
        if v < best_val:
            best_val = v
            best_x = cand
    return best_x

TEST_CASES = [
    (
        "-10 10",
        "3"
    )
]

def solve():
    # Example function: f(x) = (x - 3)^2 + 5, minimum at x = 3
    import sys
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    lo, hi = int(tokens[0]), int(tokens[1])
    def f(x):
        return (x - 3) ** 2 + 5
    ans = ternary_search_min_int(lo, hi, f)
    sys.stdout.write(str(ans) + "\n")

if __name__ == "__main__":
    solve()
```

---

## ⚡ Complexity & Analysis
- **Time Complexity:** See docstrings and implementation above.
- **Space Complexity:** See docstrings and implementation above.

---

⏮️ [[ComProg/02_Binary_and_Ternary_Search/README|Back to 02_Binary_and_Ternary_Search]] | 🏠 [[ComProg/Home|Dashboard]]
