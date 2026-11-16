"""
Prefix Sums & Difference Arrays in Python
1D and 2D implementations for O(1) range queries and O(1) range updates.
"""

import sys

class PrefixSum1D:
    def __init__(self, arr):
        n = len(arr)
        # 1-indexed prefix sum array: pref[i] = sum(arr[0 ... i-1])
        self.pref = [0] * (n + 1)
        for i in range(n):
            self.pref[i + 1] = self.pref[i] + arr[i]

    def query(self, left, right):
        """Returns sum of arr[left ... right] inclusive (0-indexed)."""
        if left > right:
            return 0
        return self.pref[right + 1] - self.pref[left]

class DifferenceArray1D:
    def __init__(self, n):
        self.n = n
        self.diff = [0] * (n + 1)

    def add(self, left, right, val):
        """Adds val to arr[left ... right] inclusive (0-indexed)."""
        self.diff[left] += val
        if right + 1 <= self.n:
            self.diff[right + 1] -= val

    def build(self):
        """Reconstructs the final array after all range additions in O(N)."""
        res = [0] * self.n
        curr = 0
        for i in range(self.n):
            curr += self.diff[i]
            res[i] = curr
        return res

class PrefixSum2D:
    def __init__(self, grid):
        R = len(grid)
        C = len(grid[0]) if R > 0 else 0
        self.pref = [[0] * (C + 1) for _ in range(R + 1)]
        for r in range(R):
            for c in range(C):
                self.pref[r + 1][c + 1] = (
                    grid[r][c]
                    + self.pref[r][c + 1]
                    + self.pref[r + 1][c]
                    - self.pref[r][c]
                )

    def query(self, r1, c1, r2, c2):
        """Returns sum of rectangle from (r1, c1) to (r2, c2) inclusive."""
        return (
            self.pref[r2 + 1][c2 + 1]
            - self.pref[r1][c2 + 1]
            - self.pref[r2 + 1][c1]
            + self.pref[r1][c1]
        )

# Test cases for run_tests.py
TEST_CASES = [
    (
        "5 3\n1 2 3 4 5\n0 2\n1 3\n0 4",
        "6\n9\n15"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    it = iter(tokens)
    n = int(next(it))
    q = int(next(it))
    arr = [int(next(it)) for _ in range(n)]
    
    ps = PrefixSum1D(arr)
    ans = []
    for _ in range(q):
        l = int(next(it))
        r = int(next(it))
        ans.append(str(ps.query(l, r)))
    sys.stdout.write("\n".join(ans) + "\n")

if __name__ == "__main__":
    solve()
