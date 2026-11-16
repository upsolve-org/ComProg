"""
Interval & Range DP in Python
Example: Matrix Chain Multiplication / Optimal Stone Merging
Time Complexity: O(N^3)
"""

import sys

def matrix_chain_multiplication(dims):
    """
    Given dimensions of N matrices where matrix i has dimensions dims[i] x dims[i+1],
    computes the minimum number of scalar multiplications required.
    dp[l][r] = min(dp[l][k] + dp[k+1][r] + dims[l] * dims[k+1] * dims[r+1]) for k in [l, r-1]
    """
    n = len(dims) - 1
    dp = [[0] * n for _ in range(n)]
    
    # length from 2 to n
    for length in range(2, n + 1):
        for l in range(n - length + 1):
            r = l + length - 1
            dp[l][r] = float('inf')
            for k in range(l, r):
                cost = dp[l][k] + dp[k + 1][r] + dims[l] * dims[k + 1] * dims[r + 1]
                if cost < dp[l][r]:
                    dp[l][r] = cost
                    
    return dp[0][n - 1]

TEST_CASES = [
    (
        "4\n10 20 30 40 30",
        "30000"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    it = iter(tokens)
    n = int(next(it))
    dims = [int(next(it)) for _ in range(n + 1)]
    ans = matrix_chain_multiplication(dims)
    sys.stdout.write(str(ans) + "\n")

if __name__ == "__main__":
    solve()
