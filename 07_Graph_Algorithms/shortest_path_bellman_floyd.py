"""
Bellman-Ford & Floyd-Warshall Algorithms in Python
1. Bellman-Ford: Single-source shortest path with negative edges & cycle detection in O(V * E).
2. Floyd-Warshall: All-Pairs Shortest Path in O(V^3).
"""

import sys

def bellman_ford(edges, n, start):
    """
    edges: list of (u, v, weight)
    Returns:
        dist: Shortest distance array
        has_negative_cycle: True if a reachable negative weight cycle exists
    """
    INF = float('inf')
    dist = [INF] * (n + 1)
    dist[start] = 0
    
    # Relax edges V - 1 times
    for _ in range(n - 1):
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                
    # Check for negative weight cycles on V-th pass
    has_negative_cycle = False
    for u, v, w in edges:
        if dist[u] != INF and dist[u] + w < dist[v]:
            has_negative_cycle = True
            break
            
    return dist, has_negative_cycle

def floyd_warshall(n, adj_matrix):
    """
    Computes all-pairs shortest paths in O(V^3).
    dist[i][j] = min distance between i and j.
    """
    dist = [row[:] for row in adj_matrix]
    for k in range(1, n + 1):
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist

TEST_CASES = [
    (
        "4 4 1\n1 2 4\n1 3 5\n2 4 5\n3 2 -2",
        "0 3 5 8"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    it = iter(tokens)
    n = int(next(it))
    m = int(next(it))
    s = int(next(it))
    
    edges = []
    for _ in range(m):
        u = int(next(it))
        v = int(next(it))
        w = int(next(it))
        edges.append((u, v, w))
        
    dist, neg_cycle = bellman_ford(edges, n, s)
    res = [str(dist[i]) for i in range(1, n + 1)]
    sys.stdout.write(" ".join(res) + "\n")

if __name__ == "__main__":
    solve()
