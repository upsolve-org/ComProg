---
tags:
  - cp/code
  - cp/foundations
---

[[ComProg/Home|🏠 Dashboard]] ❯ [[ComProg/01_Foundations_and_Complexity/README|01_Foundations_and_Complexity]] ❯ **Practice Examples**

---

# Practice Examples

> [!abstract] Implementation Note
> This note contains the complete, battle-tested Python implementation of **Practice Examples**.
> Source file: `ComProg/01_Foundations_and_Complexity/practice_examples.py`
> Run test runner: `python3 run_tests.py ComProg/01_Foundations_and_Complexity/practice_examples.py`

---

## 🐍 Python Implementation

```python
"""
Practice Examples: Foundations & Complexity
1. Kadane's Algorithm: Maximum Subarray Sum (O(N))
2. Range Updates & Point Queries via Difference Array
"""

import sys

def max_subarray_sum(arr):
    """
    Kadane's algorithm:
    Finds the maximum sum of a contiguous subarray in O(N) time and O(1) space.
    """
    max_so_far = -float('inf')
    curr_sum = 0
    for x in arr:
        curr_sum += x
        if curr_sum > max_so_far:
            max_so_far = curr_sum
        if curr_sum < 0:
            curr_sum = 0
    return max_so_far

TEST_CASES = [
    (
        "8\n-2 1 -3 4 -1 2 1 -5 4",
        "6"
    ),
    (
        "5\n-1 -2 -3 -4 -5",
        "-1"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    n = int(tokens[0])
    arr = [int(x) for x in tokens[1:n+1]]
    ans = max_subarray_sum(arr)
    sys.stdout.write(str(ans) + "\n")

if __name__ == "__main__":
    solve()
```

---

## ⚡ Complexity & Analysis
- **Time Complexity:** See docstrings and implementation above.
- **Space Complexity:** See docstrings and implementation above.

---

⏮️ [[ComProg/01_Foundations_and_Complexity/README|Back to 01_Foundations_and_Complexity]] | 🏠 [[ComProg/Home|Dashboard]]
