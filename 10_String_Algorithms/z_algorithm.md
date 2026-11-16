---
tags:
  - cp/code
  - cp/string
---

[[ComProg/Home|🏠 Dashboard]] ❯ [[ComProg/10_String_Algorithms/README|10_String_Algorithms]] ❯ **Z Algorithm**

---

# Z Algorithm

> [!abstract] Implementation Note
> This note contains the complete, battle-tested Python implementation of **Z Algorithm**.
> Source file: `ComProg/10_String_Algorithms/z_algorithm.py`
> Run test runner: `python3 run_tests.py ComProg/10_String_Algorithms/z_algorithm.py`

---

## 🐍 Python Implementation

```python
"""
Z-Algorithm in Python
Computes Z-array in O(N):
Z[i] is the length of the longest common prefix between s and the suffix of s starting at i.
"""

import sys

def z_algorithm(s):
    """
    Computes Z-array for string s in O(N).
    """
    n = len(s)
    z = [0] * n
    z[0] = n
    l, r = 0, 0
    
    for i in range(1, n):
        if i <= r:
            z[i] = min(r - i + 1, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] - 1 > r:
            l = i
            r = i + z[i] - 1
            
    return z

def z_search(text, pattern):
    """Returns starting indices of occurrences of pattern in text using Z-algorithm."""
    m = len(pattern)
    combined = pattern + "$" + text
    z = z_algorithm(combined)
    
    matches = []
    for i in range(m + 1, len(combined)):
        if z[i] == m:
            matches.append(i - m - 1)
    return matches

TEST_CASES = [
    (
        "abacaba\naba",
        "0 4"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    text = tokens[0]
    pattern = tokens[1]
    matches = z_search(text, pattern)
    sys.stdout.write(" ".join(map(str, matches)) + "\n")

if __name__ == "__main__":
    solve()
```

---

## ⚡ Complexity & Analysis
- **Time Complexity:** See docstrings and implementation above.
- **Space Complexity:** See docstrings and implementation above.

---

⏮️ [[ComProg/10_String_Algorithms/README|Back to 10_String_Algorithms]] | 🏠 [[ComProg/Home|Dashboard]]
