"""
GCD, LCM, and Extended Euclidean Algorithm in Python
Solves: a * x + b * y = gcd(a, b) and Linear Diophantine Equations.
"""

import sys
import math

def lcm(a, b):
    """Computes LCM using math.gcd."""
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // math.gcd(a, b)

def extgcd(a, b):
    """
    Extended Euclidean Algorithm.
    Returns (g, x, y) such that:
        a * x + b * y = g = gcd(a, b)
    Time Complexity: O(log(min(a, b)))
    """
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extgcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return g, x, y

def solve_linear_diophantine(a, b, c):
    """
    Finds one integer solution (x, y) to a * x + b * y = c.
    Returns (True, x, y) if a solution exists, or (False, None, None) otherwise.
    """
    g, x0, y0 = extgcd(abs(a), abs(b))
    if c % g != 0:
        return False, None, None
        
    factor = c // g
    x = x0 * factor * (1 if a >= 0 else -1)
    y = y0 * factor * (1 if b >= 0 else -1)
    return True, x, y

TEST_CASES = [
    (
        "3\n35 15\n10 5\n12 18",
        "5 1 -2\n5 0 1\n6 -1 1"
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
        a = int(next(it))
        b = int(next(it))
        g, x, y = extgcd(a, b)
        out.append(f"{g} {x} {y}")
    sys.stdout.write("\n".join(out) + "\n")

if __name__ == "__main__":
    solve()
