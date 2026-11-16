---
tags:
  - cp/code
  - cp/mathematics
---

[[ComProg/Home|🏠 Dashboard]] ❯ [[ComProg/09_Mathematics_and_Number_Theory/README|09_Mathematics_and_Number_Theory]] ❯ **Primes And Sieve**

---

# Primes And Sieve

> [!abstract] Implementation Note
> This note contains the complete, battle-tested Python implementation of **Primes And Sieve**.
> Source file: `ComProg/09_Mathematics_and_Number_Theory/primes_and_sieve.py`
> Run test runner: `python3 run_tests.py ComProg/09_Mathematics_and_Number_Theory/primes_and_sieve.py`

---

## 🐍 Python Implementation

```python
"""
Primes, Sieves, and Prime Factorization in Python
1. Trial division primality check in O(sqrt(N))
2. Sieve of Eratosthenes in O(N log log N)
3. Smallest Prime Factor (SPF) Linear Sieve for O(log N) factorization
"""

import sys
import math

def is_prime(n):
    """Checks if n is prime in O(sqrt(N))."""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    # Check 6k +- 1
    d = 5
    while d * d <= n:
        if n % d == 0 or n % (d + 2) == 0:
            return False
        d += 6
    return True

def sieve(limit):
    """Returns list of primes up to limit."""
    is_p = bytearray([1]) * (limit + 1)
    is_p[0] = is_p[1] = 0
    for i in range(2, math.isqrt(limit) + 1):
        if is_p[i]:
            is_p[i*i : limit + 1 : i] = bytearray([0]) * len(is_p[i*i : limit + 1 : i])
    return [i for i, val in enumerate(is_p) if val]

class PrimeFactorizerSPF:
    """Precomputes SPF up to limit to factorize numbers in O(log N)."""
    def __init__(self, limit):
        self.spf = list(range(limit + 1))
        for i in range(2, math.isqrt(limit) + 1):
            if self.spf[i] == i:
                for j in range(i * i, limit + 1, i):
                    if self.spf[j] == j:
                        self.spf[j] = i

    def factorize(self, x):
        """Returns list of prime factors of x in O(log x)."""
        factors = []
        while x > 1:
            factors.append(self.spf[x])
            x //= self.spf[x]
        return factors

TEST_CASES = [
    (
        "5\n2\n4\n17\n1\n1000000007",
        "YES\nNO\nYES\nNO\nYES"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    it = iter(tokens)
    t = int(next(it))
    out = []
    for _ in range(t):
        n = int(next(it))
        out.append("YES" if is_prime(n) else "NO")
    sys.stdout.write("\n".join(out) + "\n")

if __name__ == "__main__":
    solve()
```

---

## ⚡ Complexity & Analysis
- **Time Complexity:** See docstrings and implementation above.
- **Space Complexity:** See docstrings and implementation above.

---

⏮️ [[ComProg/09_Mathematics_and_Number_Theory/README|Back to 09_Mathematics_and_Number_Theory]] | 🏠 [[ComProg/Home|Dashboard]]
