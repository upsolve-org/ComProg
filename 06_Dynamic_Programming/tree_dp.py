"""
Tree Dynamic Programming in Python
*Reference: Codeforces Catalog "Dp On Trees" by AghaTizi*

1. Tree Diameter via DP
2. Maximum Independent Set on a Tree
Time Complexity: O(N)
"""

import sys

sys.setrecursionlimit(300000)

def tree_diameter(adj, n):
    """
    Computes tree diameter using bottom-up post-order DFS.
    For each node, maintains the two longest branch lengths into its children.
    """
    diameter = 0
    
    def dfs(u, p):
        nonlocal diameter
        first_max = 0
        second_max = 0
        
        for v in adj[u]:
            if v != p:
                depth_v = dfs(v, u) + 1
                if depth_v > first_max:
                    second_max = first_max
                    first_max = depth_v
                elif depth_v > second_max:
                    second_max = depth_v
                    
        diameter = max(diameter, first_max + second_max)
        return first_max

    dfs(1, 0)
    return diameter

def max_independent_set_tree(adj, weights, n):
    """
    Finds maximum weight independent set of nodes such that no two chosen nodes are adjacent.
    dp[u][0] = max weight if u is NOT chosen
    dp[u][1] = max weight if u IS chosen
    """
    dp = [[0, 0] for _ in range(n + 1)]
    
    def dfs(u, p):
        dp[u][1] = weights[u]
        dp[u][0] = 0
        for v in adj[u]:
            if v != p:
                dfs(v, u)
                dp[u][1] += dp[v][0]
                dp[u][0] += max(dp[v][0], dp[v][1])

    dfs(1, 0)
    return max(dp[1][0], dp[1][1])

TEST_CASES = [
    (
        "5\n1 2\n1 3\n3 4\n3 5",
        "3"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    it = iter(tokens)
    n = int(next(it))
    adj = [[] for _ in range(n + 1)]
    for _ in range(n - 1):
        u = int(next(it))
        v = int(next(it))
        adj[u].append(v)
        adj[v].append(u)
        
    ans = tree_diameter(adj, n)
    sys.stdout.write(str(ans) + "\n")

if __name__ == "__main__":
    solve()
