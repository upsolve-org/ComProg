---
tags:
  - cp/code
  - cp/advanced
---

[[ComProg/Home|🏠 Dashboard]] ❯ [[ComProg/11_Advanced_and_Niche_Techniques/README|11_Advanced_and_Niche_Techniques]] ❯ **Constructive Algorithms**

---

# Constructive Algorithms

> [!abstract] Implementation Note
> This note contains the complete, battle-tested Python implementation of **Constructive Algorithms**.
> Source file: `ComProg/11_Advanced_and_Niche_Techniques/constructive_algorithms.py`
> Run test runner: `python3 run_tests.py ComProg/11_Advanced_and_Niche_Techniques/constructive_algorithms.py`

---

## 🐍 Python Implementation

```python
"""
Constructive Algorithms Patterns in Python
*Reference: Codeforces Catalog "Tips on Constructive Algorithms"*
1. Gray Code Generation (adjacent binary codes differ by exactly 1 bit)
2. Beautiful Permutations (no adjacent elements with absolute difference 1)
"""

import sys

def generate_gray_code(n):
    """
    Generates n-bit Gray Code sequence of length 2^n.
    Formula: G(i) = i ^ (i >> 1)
    """
    return [i ^ (i >> 1) for i in range(1 << n)]

def beautiful_permutation(n):
    """
    Constructs a permutation of 1 ... n such that no two adjacent elements differ by 1.
    Pattern: Put all even numbers first, then all odd numbers.
    Impossible for n = 2 and n = 3.
    """
    if n == 1:
        return [1]
    if n in (2, 3):
        return []
    
    evens = list(range(2, n + 1, 2))
    odds = list(range(1, n + 1, 2))
    return evens + odds

TEST_CASES = [
    (
        "4",
        "2 4 1 3"
    ),
    (
        "3",
        "NO SOLUTION"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    n = int(tokens[0])
    res = beautiful_permutation(n)
    if not res:
        sys.stdout.write("NO SOLUTION\n")
    else:
        sys.stdout.write(" ".join(map(str, res)) + "\n")

if __name__ == "__main__":
    solve()
```

---

## ⚡ Complexity & Analysis
- **Time Complexity:** See docstrings and implementation above.
- **Space Complexity:** See docstrings and implementation above.

---

⏮️ [[ComProg/11_Advanced_and_Niche_Techniques/README|Back to 11_Advanced_and_Niche_Techniques]] | 🏠 [[ComProg/Home|Dashboard]]
