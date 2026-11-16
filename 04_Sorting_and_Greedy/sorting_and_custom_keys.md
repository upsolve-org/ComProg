---
tags:
  - cp/code
  - cp/sorting
---

[[ComProg/Home|🏠 Dashboard]] ❯ [[ComProg/04_Sorting_and_Greedy/README|04_Sorting_and_Greedy]] ❯ **Sorting And Custom Keys**

---

# Sorting And Custom Keys

> [!abstract] Implementation Note
> This note contains the complete, battle-tested Python implementation of **Sorting And Custom Keys**.
> Source file: `ComProg/04_Sorting_and_Greedy/sorting_and_custom_keys.py`
> Run test runner: `python3 run_tests.py ComProg/04_Sorting_and_Greedy/sorting_and_custom_keys.py`

---

## 🐍 Python Implementation

```python
"""
Sorting Techniques & Coordinate Compression in Python.
"""

from functools import cmp_to_key

def coordinate_compression(arr):
    """
    Compresses an array of large numbers into contiguous 0-based ranks.
    Returns:
        compressed_arr: Array of ranks [0 ... K-1]
        unique_sorted: The sorted unique values for decompressing
    Time Complexity: O(N log N)
    """
    unique_sorted = sorted(set(arr))
    val_to_rank = {val: idx for idx, val in enumerate(unique_sorted)}
    compressed = [val_to_rank[x] for x in arr]
    return compressed, unique_sorted

def sort_largest_concatenated_number(numbers):
    """
    Given non-negative integers, arrange them such that they form the largest number.
    e.g. [3, 30, 34, 5, 9] -> "9534330"
    Uses custom comparator with cmp_to_key.
    """
    def compare(s1, s2):
        if s1 + s2 > s2 + s1:
            return -1  # s1 comes first
        elif s1 + s2 < s2 + s1:
            return 1   # s2 comes first
        else:
            return 0

    str_nums = [str(x) for x in numbers]
    str_nums.sort(key=cmp_to_key(compare))
    
    # Edge case: all zeros
    if str_nums[0] == "0":
        return "0"
    return "".join(str_nums)

TEST_CASES = [
    (
        "5\n3 30 34 5 9",
        "9534330"
    )
]

def solve():
    import sys
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    n = int(tokens[0])
    nums = [int(x) for x in tokens[1:1+n]]
    ans = sort_largest_concatenated_number(nums)
    sys.stdout.write(ans + "\n")

if __name__ == "__main__":
    solve()
```

---

## ⚡ Complexity & Analysis
- **Time Complexity:** See docstrings and implementation above.
- **Space Complexity:** See docstrings and implementation above.

---

⏮️ [[ComProg/04_Sorting_and_Greedy/README|Back to 04_Sorting_and_Greedy]] | 🏠 [[ComProg/Home|Dashboard]]
