"""
Modular Arithmetic and Combinatorics in Python
Precomputed Factorials and Inverse Factorials for O(1) nCr queries modulo prime P.
"""

import sys

MOD_DEFAULT = 1_000_000_007

class Combinatorics:
    def __init__(self, max_n, mod=MOD_DEFAULT):
        self.mod = mod
        self.fact = [1] * (max_n + 1)
        self.inv_fact = [1] * (max_n + 1)
        
        # Precompute factorials
        for i in range(1, max_n + 1):
            self.fact[i] = (self.fact[i - 1] * i) % mod
            
        # Compute inverse of fact[max_n] using Fermat's Little Theorem
        self.inv_fact[max_n] = pow(self.fact[max_n], mod - 2, mod)
        
        # Work backwards for inverse factorials
        for i in range(max_n - 1, -1, -1):
            self.inv_fact[i] = (self.inv_fact[i + 1] * (i + 1)) % mod

    def nCr(self, n, r):
        """Returns n choose r modulo P in O(1)."""
        if r < 0 or r > n:
            return 0
        return (self.fact[n] * self.inv_fact[r] % self.mod * self.inv_fact[n - r]) % self.mod

    def nPr(self, n, r):
        """Returns n permutations r modulo P in O(1)."""
        if r < 0 or r > n:
            return 0
        return (self.fact[n] * self.inv_fact[n - r]) % self.mod

TEST_CASES = [
    (
        "3\n5 2\n10 3\n100 0",
        "10\n120\n1"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    it = iter(tokens)
    t = int(next(it))
    cb = Combinatorics(100000, MOD_DEFAULT)
    out = []
    for _ in range(t):
        n = int(next(it))
        r = int(next(it))
        out.append(str(cb.nCr(n, r)))
    sys.stdout.write("\n".join(out) + "\n")

if __name__ == "__main__":
    solve()
