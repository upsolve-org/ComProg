"""
Graph Traversal in Python:
1. Breadth-First Search (BFS): Shortest path in unweighted graphs
2. Depth-First Search (DFS): Connected components & cycle detection
3. Bipartite Checking (2-Coloring)
"""

import sys
import collections

sys.setrecursionlimit(300000)

def bfs_shortest_path(adj, start, target, n):
    """
    Returns shortest distance from start to target in unweighted graph,
    or -1 if unreachable. Also reconstructs path.
    Time Complexity: O(V + E).
    """
    dist = [-1] * (n + 1)
    parent = [-1] * (n + 1)
    
    dq = collections.deque([start])
    dist[start] = 0
    
    while dq:
        u = dq.popleft()
        if u == target:
            break
        for v in adj[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                parent[v] = u
                dq.append(v)
                
    if dist[target] == -1:
        return -1, []
        
    # Reconstruct path
    path = []
    curr = target
    while curr != -1:
        path.append(curr)
        curr = parent[curr]
    path.reverse()
    
    return dist[target], path

def is_bipartite(adj, n):
    """
    Checks if an undirected graph can be 2-colored such that no two adjacent
    nodes have the same color.
    """
    color = [-1] * (n + 1)
    
    for i in range(1, n + 1):
        if color[i] == -1:
            dq = collections.deque([i])
            color[i] = 0
            while dq:
                u = dq.popleft()
                for v in adj[u]:
                    if color[v] == -1:
                        color[v] = 1 - color[u]
                        dq.append(v)
                    elif color[v] == color[u]:
                        return False
    return True

TEST_CASES = [
    (
        "5 5 1 5\n1 2\n2 3\n3 5\n1 4\n4 5",
        "2\n1 4 5"
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
    t = int(next(it))
    
    adj = [[] for _ in range(n + 1)]
    for _ in range(m):
        u = int(next(it))
        v = int(next(it))
        adj[u].append(v)
        adj[v].append(u)
        
    d, path = bfs_shortest_path(adj, s, t, n)
    sys.stdout.write(f"{d}\n{' '.join(map(str, path))}\n")

if __name__ == "__main__":
    solve()
