"""
Topological Sort (Kahn's Algorithm via BFS) in Python.
- Returns valid linear ordering of vertices in a Directed Acyclic Graph (DAG)
- Detects if graph contains a directed cycle
Time Complexity: O(V + E)
"""

import sys
import collections

def topological_sort(adj, in_degree, n):
    """
    Kahn's Algorithm:
    Uses a queue of vertices with in-degree 0.
    Returns:
        order: List of vertices in topological order.
        has_cycle: True if a directed cycle exists, False otherwise.
    """
    dq = collections.deque()
    for i in range(1, n + 1):
        if in_degree[i] == 0:
            dq.append(i)
            
    order = []
    while dq:
        u = dq.popleft()
        order.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                dq.append(v)
                
    has_cycle = (len(order) < n)
    return order, has_cycle

TEST_CASES = [
    (
        "5 4\n1 2\n2 3\n1 4\n4 5",
        "1 2 4 3 5"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    it = iter(tokens)
    n = int(next(it))
    m = int(next(it))
    
    adj = [[] for _ in range(n + 1)]
    in_degree = [0] * (n + 1)
    
    for _ in range(m):
        u = int(next(it))
        v = int(next(it))
        adj[u].append(v)
        in_degree[v] += 1
        
    order, has_cycle = topological_sort(adj, in_degree, n)
    if has_cycle:
        sys.stdout.write("IMPOSSIBLE\n")
    else:
        sys.stdout.write(" ".join(map(str, order)) + "\n")

if __name__ == "__main__":
    solve()
