"""
Knapsack & Subset Sum DP in Python
1. 0/1 Knapsack (Space-optimized 1D array iterating backwards)
2. Unbounded Knapsack (Iterating forwards)
3. Subset Sum (Boolean reachability)
"""

import sys

def knapsack_01(weights, values, capacity):
    """
    Given N items with weights and values, find maximum value fitting in capacity.
    Each item can be used at most once.
    Space Optimization: 1D array of size capacity + 1.
    Iterating weight BACKWARDS prevents using the same item multiple times.
    Time Complexity: O(N * W), Space Complexity: O(W).
    """
    dp = [0] * (capacity + 1)
    
    for w, v in zip(weights, values):
        # Iterate backwards from capacity down to w
        for cap in range(capacity, w - 1, -1):
            dp[cap] = max(dp[cap], dp[cap - w] + v)
            
    return dp[capacity]

def unbounded_knapsack(weights, values, capacity):
    """
    Each item can be used unlimited times.
    Iterating weight FORWARDS allows reusing the current item.
    Time Complexity: O(N * W), Space: O(W).
    """
    dp = [0] * (capacity + 1)
    
    for cap in range(1, capacity + 1):
        for w, v in zip(weights, values):
            if cap >= w:
                dp[cap] = max(dp[cap], dp[cap - w] + v)
                
    return dp[capacity]

def can_form_subset_sum(nums, target_sum):
    """
    Determines if there is a subset of nums with sum equal to target_sum.
    Can be represented with boolean array or bitset.
    """
    dp = [False] * (target_sum + 1)
    dp[0] = True
    
    for x in nums:
        for s in range(target_sum, x - 1, -1):
            if dp[s - x]:
                dp[s] = True
                
    return dp[target_sum]

TEST_CASES = [
    (
        "4 7\n1 3 4 5\n1 4 5 7",
        "9"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    it = iter(tokens)
    n = int(next(it))
    w_cap = int(next(it))
    weights = [int(next(it)) for _ in range(n)]
    values = [int(next(it)) for _ in range(n)]
    ans = knapsack_01(weights, values, w_cap)
    sys.stdout.write(str(ans) + "\n")

if __name__ == "__main__":
    solve()
