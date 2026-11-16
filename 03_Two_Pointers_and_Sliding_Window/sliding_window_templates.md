---
tags:
  - cp/code
  - cp/two
---

[[ComProg/Home|🏠 Dashboard]] ❯ [[ComProg/03_Two_Pointers_and_Sliding_Window/README|03_Two_Pointers_and_Sliding_Window]] ❯ **Sliding Window Templates**

---

# Sliding Window Templates

> [!abstract] Implementation Note
> This note contains the complete, battle-tested Python implementation of **Sliding Window Templates**.
> Source file: `ComProg/03_Two_Pointers_and_Sliding_Window/sliding_window_templates.py`
> Run test runner: `python3 run_tests.py ComProg/03_Two_Pointers_and_Sliding_Window/sliding_window_templates.py`

---

## 🐍 Python Implementation

```python
"""
Sliding Window Templates in Python:
1. Longest subarray with sum <= S
2. Subarray with at most K distinct elements
3. Fixed-size window maximum / sum
"""

import sys
import collections

def longest_subarray_sum_at_most_s(arr, max_s):
    """
    Finds the length of the longest contiguous subarray with sum <= max_s.
    Assumes all elements arr[i] >= 0.
    Time Complexity: O(N).
    """
    left = 0
    curr_sum = 0
    max_len = 0
    for right in range(len(arr)):
        curr_sum += arr[right]
        while curr_sum > max_s and left <= right:
            curr_sum -= arr[left]
            left += 1
        if curr_sum <= max_s:
            max_len = max(max_len, right - left + 1)
    return max_len

def at_most_k_distinct(arr, k):
    """
    Counts the number of subarrays with at most k distinct values.
    Time Complexity: O(N).
    """
    counts = collections.defaultdict(int)
    left = 0
    distinct = 0
    total = 0
    for right in range(len(arr)):
        if counts[arr[right]] == 0:
            distinct += 1
        counts[arr[right]] += 1
        
        while distinct > k:
            counts[arr[left]] -= 1
            if counts[arr[left]] == 0:
                distinct -= 1
            left += 1
            
        total += (right - left + 1)
    return total

TEST_CASES = [
    (
        "5 7\n2 1 5 1 1",
        "3"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    n = int(tokens[0])
    s = int(tokens[1])
    arr = [int(x) for x in tokens[2:2+n]]
    ans = longest_subarray_sum_at_most_s(arr, s)
    sys.stdout.write(str(ans) + "\n")

if __name__ == "__main__":
    solve()
```

---

## ⚡ Complexity & Analysis
- **Time Complexity:** See docstrings and implementation above.
- **Space Complexity:** See docstrings and implementation above.

---

⏮️ [[ComProg/03_Two_Pointers_and_Sliding_Window/README|Back to 03_Two_Pointers_and_Sliding_Window]] | 🏠 [[ComProg/Home|Dashboard]]
