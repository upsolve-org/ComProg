"""
Bitmask Dynamic Programming in Python
1. Traveling Salesperson Problem (Hamiltonian Path) in O(N^2 * 2^N)
2. Submask Enumeration in O(3^N)
"""

import sys

def traveling_salesperson(cost_matrix):
    """
    Finds the minimum cost to visit all N cities starting at city 0 and ending at city 0.
    dp[mask][u] = min cost to visit subset 'mask' ending at city u.
    Time Complexity: O(N^2 * 2^N).
    """
    n = len(cost_matrix)
    INF = float('inf')
    num_states = 1 << n
    
    dp = [[INF] * n for _ in range(num_states)]
    dp[1][0] = 0  # Starting at city 0 with mask 1 (00...001)
    
    for mask in range(num_states):
        for u in range(n):
            if dp[mask][u] == INF:
                continue
            for v in range(n):
                # If city v is not yet visited
                if not (mask & (1 << v)):
                    nxt_mask = mask | (1 << v)
                    cost = dp[mask][u] + cost_matrix[u][v]
                    if cost < dp[nxt_mask][v]:
                        dp[nxt_mask][v] = cost
                        
    # Close cycle back to 0
    full_mask = num_states - 1
    ans = INF
    for u in range(1, n):
        ans = min(ans, dp[full_mask][u] + cost_matrix[u][0])
        
    return ans

def iterate_all_submasks(mask):
    """
    Efficiently iterates through all submasks of a given mask in decreasing order.
    Total time over all masks is O(3^N).
    """
    submask = mask
    submasks = []
    while submask > 0:
        submasks.append(submask)
        submask = (submask - 1) & mask
    submasks.append(0)
    return submasks

TEST_CASES = [
    (
        "4\n0 10 15 20\n10 0 35 25\n15 35 0 30\n20 25 30 0",
        "80"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    it = iter(tokens)
    n = int(next(it))
    matrix = [[int(next(it)) for _ in range(n)] for _ in range(n)]
    ans = traveling_salesperson(matrix)
    sys.stdout.write(str(ans) + "\n")

if __name__ == "__main__":
    solve()
