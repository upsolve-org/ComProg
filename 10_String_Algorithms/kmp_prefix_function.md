---
tags:
  - cp/code
  - cp/string
---

[[ComProg/Home|🏠 Dashboard]] ❯ [[ComProg/10_String_Algorithms/README|10_String_Algorithms]] ❯ **Kmp Prefix Function**

---

# Kmp Prefix Function

> [!abstract] Implementation Note
> This note contains the complete, battle-tested Python implementation of **Kmp Prefix Function**.
> Source file: `ComProg/10_String_Algorithms/kmp_prefix_function.py`
> Run test runner: `python3 run_tests.py ComProg/10_String_Algorithms/kmp_prefix_function.py`

---

## 🐍 Python Implementation

```python
"""
Knuth-Morris-Pratt (KMP) Prefix Function in Python
- Computes prefix function pi in O(N)
- Searches all pattern occurrences in O(|T| + |P|)
"""

import sys

def prefix_function(s):
    """
    Computes pi array where pi[i] is the length of the longest proper prefix
    of s[0 ... i] that is also a suffix of s[0 ... i].
    Time Complexity: O(N).
    """
    n = len(s)
    pi = [0] * n
    for i in range(1, n):
        j = pi[i - 1]
        while j > 0 and s[i] != s[j]:
            j = pi[j - 1]
        if s[i] == s[j]:
            j += 1
        pi[i] = j
    return pi

def kmp_search(text, pattern):
    """
    Returns list of 0-based starting indices where pattern occurs in text.
    Time Complexity: O(|text| + |pattern|).
    """
    if not pattern or not text:
        return []
        
    combined = pattern + "#" + text
    pi = prefix_function(combined)
    m = len(pattern)
    
    matches = []
    for i in range(m + 1, len(combined)):
        if pi[i] == m:
            matches.append(i - 2 * m)
            
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
    matches = kmp_search(text, pattern)
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
