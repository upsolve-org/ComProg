"""
Grid & Paths DP in Python:
1. Unique Paths with Obstacles modulo 10^9 + 7
2. Minimum Path Sum in a Grid
"""

import sys

MOD = 1_000_000_007

def unique_paths_with_obstacles(grid):
    """
    Given an R x C grid where 1 represents an obstacle and 0 represents free space,
    returns the number of paths from top-left (0, 0) to bottom-right (R-1, C-1)
    moving only right and down, modulo 10^9 + 7.
    Space Complexity: O(C).
    """
    R = len(grid)
    C = len(grid[0]) if R > 0 else 0
    if R == 0 or C == 0 or grid[0][0] == 1 or grid[R - 1][C - 1] == 1:
        return 0
        
    dp = [0] * C
    dp[0] = 1
    
    for r in range(R):
        for c in range(C):
            if grid[r][c] == 1:
                dp[c] = 0
            elif c > 0:
                dp[c] = (dp[c] + dp[c - 1]) % MOD
                
    return dp[C - 1]

def min_path_sum(grid):
    """
    Returns the minimum sum path from top-left to bottom-right.
    """
    R = len(grid)
    C = len(grid[0])
    dp = [float('inf')] * C
    dp[0] = 0
    
    for r in range(R):
        dp[0] += grid[r][0]
        for c in range(1, C):
            dp[c] = min(dp[c], dp[c - 1]) + grid[r][c]
            
    return dp[C - 1]

TEST_CASES = [
    (
        "3 3\n0 0 0\n0 1 0\n0 0 0",
        "2"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    it = iter(tokens)
    r = int(next(it))
    c = int(next(it))
    grid = [[int(next(it)) for _ in range(c)] for _ in range(r)]
    ans = unique_paths_with_obstacles(grid)
    sys.stdout.write(str(ans) + "\n")

if __name__ == "__main__":
    solve()
