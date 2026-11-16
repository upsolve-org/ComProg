---
tags:
  - cp/code
  - cp/string
---

[[ComProg/Home|🏠 Dashboard]] ❯ [[ComProg/10_String_Algorithms/README|10_String_Algorithms]] ❯ **Polynomial Rolling Hash**

---

# Polynomial Rolling Hash

> [!abstract] Implementation Note
> This note contains the complete, battle-tested Python implementation of **Polynomial Rolling Hash**.
> Source file: `ComProg/10_String_Algorithms/polynomial_rolling_hash.py`
> Run test runner: `python3 run_tests.py ComProg/10_String_Algorithms/polynomial_rolling_hash.py`

---

## 🐍 Python Implementation

```python
"""
Polynomial Rolling Hash (Double Hash) in Python
- O(1) Substring Hash queries
- Double hash with two large primes to eliminate hash collisions and hacking
"""

import sys

class DoubleStringHash:
    """
    Computes double rolling hash for 1-based or 0-based substrings.
    Hash values: H1 mod M1 and H2 mod M2.
    """
    def __init__(self, s, base1=313, mod1=1_000_000_007, base2=317, mod2=1_000_000_009):
        self.n = len(s)
        self.mod1 = mod1
        self.mod2 = mod2
        
        self.h1 = [0] * (self.n + 1)
        self.h2 = [0] * (self.n + 1)
        self.p1 = [1] * (self.n + 1)
        self.p2 = [1] * (self.n + 1)
        
        for i in range(self.n):
            code = ord(s[i])
            self.h1[i + 1] = (self.h1[i] * base1 + code) % mod1
            self.h2[i + 1] = (self.h2[i] * base2 + code) % mod2
            self.p1[i + 1] = (self.p1[i] * base1) % mod1
            self.p2[i + 1] = (self.p2[i] * base2) % mod2

    def get_hash(self, l, r):
        """
        Returns (hash1, hash2) for substring s[l ... r] inclusive (0-indexed).
        """
        hash1 = (self.h1[r + 1] - self.h1[l] * self.p1[r - l + 1]) % self.mod1
        hash2 = (self.h2[r + 1] - self.h2[l] * self.p2[r - l + 1]) % self.mod2
        return hash1, hash2

    def are_equal(self, l1, r1, l2, r2):
        """Checks if s[l1 ... r1] == s[l2 ... r2] in O(1)."""
        if (r1 - l1) != (r2 - l2):
            return False
        return self.get_hash(l1, r1) == self.get_hash(l2, r2)

TEST_CASES = [
    (
        "abacaba\n2\n0 2 4 6\n1 3 4 6",
        "YES\nNO"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    it = iter(tokens)
    s = next(it)
    q = int(next(it))
    sh = DoubleStringHash(s)
    out = []
    for _ in range(q):
        l1 = int(next(it))
        r1 = int(next(it))
        l2 = int(next(it))
        r2 = int(next(it))
        out.append("YES" if sh.are_equal(l1, r1, l2, r2) else "NO")
    sys.stdout.write("\n".join(out) + "\n")

if __name__ == "__main__":
    solve()
```

---

## ⚡ Complexity & Analysis
- **Time Complexity:** See docstrings and implementation above.
- **Space Complexity:** See docstrings and implementation above.

---

⏮️ [[ComProg/10_String_Algorithms/README|Back to 10_String_Algorithms]] | 🏠 [[ComProg/Home|Dashboard]]
