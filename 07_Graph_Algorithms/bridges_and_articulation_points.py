"""
Bridges and Articulation Points in Python
Tarjan's DFS Low-Link Algorithm
Time Complexity: O(V + E)
"""

import sys

sys.setrecursionlimit(300000)

def find_bridges_and_cutpoints(n, adj):
    """
    Returns:
        bridges: list of edges (u, v) whose removal disconnects the graph
        cutpoints: list of vertices whose removal disconnects the graph
    """
    tin = [-1] * (n + 1)
    low = [-1] * (n + 1)
    timer = 0
    
    bridges = []
    cutpoints = set()
    
    def dfs(u, p=-1):
        nonlocal timer
        timer += 1
        tin[u] = low[u] = timer
        children = 0
        
        for v in adj[u]:
            if v == p:
                continue
            if tin[v] != -1:
                # Back-edge
                low[u] = min(low[u], tin[v])
            else:
                # Forward tree-edge
                children += 1
                dfs(v, u)
                low[u] = min(low[u], low[v])
                
                # Bridge condition
                if low[v] > tin[u]:
                    bridges.append((min(u, v), max(u, v)))
                    
                # Articulation point condition
                if p != -1 and low[v] >= tin[u]:
                    cutpoints.add(u)
                    
        if p == -1 and children > 1:
            cutpoints.add(u)

    for i in range(1, n + 1):
        if tin[i] == -1:
            dfs(i)
            
    bridges.sort()
    return bridges, sorted(cutpoints)

TEST_CASES = [
    (
        "5 5\n1 2\n2 3\n3 1\n3 4\n4 5",
        "2\n3 4\n4 5"
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
    for _ in range(m):
        u = int(next(it))
        v = int(next(it))
        adj[u].append(v)
        adj[v].append(u)
        
    bridges, cutpoints = find_bridges_and_cutpoints(n, adj)
    out = [str(len(bridges))]
    for u, v in bridges:
        out.append(f"{u} {v}")
    sys.stdout.write("\n".join(out) + "\n")

if __name__ == "__main__":
    solve()
