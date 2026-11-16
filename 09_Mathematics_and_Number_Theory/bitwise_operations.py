"""
Bitwise Operations and Linear Basis (XOR Basis) in Python
1. Bitwise primitives: bit counting, lowest set bit, submask enumeration
2. Linear Basis over GF(2): Maximum XOR subset, subset XOR queries
"""

import sys

def get_kth_bit(x, k):
    return (x >> k) & 1

def set_kth_bit(x, k):
    return x | (1 << k)

def clear_kth_bit(x, k):
    return x & ~(1 << k)

def toggle_kth_bit(x, k):
    return x ^ (1 << k)

def lowest_set_bit(x):
    """Returns the value of the lowest set bit (e.g. 12 -> 4)."""
    return x & (-x)

class LinearBasisXOR:
    """
    Linear Basis over GF(2) for numbers up to 2^BITS.
    Answers:
    - Maximum XOR sum of any subset
    - Can a value X be represented as XOR sum of a subset?
    """
    def __init__(self, bits=60):
        self.bits = bits
        self.basis = [0] * bits
        self.size = 0

    def insert(self, mask):
        """Inserts a number into the basis. Returns True if basis expanded."""
        for i in range(self.bits - 1, -1, -1):
            if not ((mask >> i) & 1):
                continue
            if not self.basis[i]:
                self.basis[i] = mask
                self.size += 1
                return True
            mask ^= self.basis[i]
        return False

    def max_xor(self):
        """Returns the maximum possible XOR sum of any subset."""
        ans = 0
        for i in range(self.bits - 1, -1, -1):
            if (ans ^ self.basis[i]) > ans:
                ans ^= self.basis[i]
        return ans

TEST_CASES = [
    (
        "3\n1 2 4",
        "7"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    it = iter(tokens)
    n = int(next(it))
    basis = LinearBasisXOR(30)
    for _ in range(n):
        x = int(next(it))
        basis.insert(x)
    sys.stdout.write(str(basis.max_xor()) + "\n")

if __name__ == "__main__":
    solve()
