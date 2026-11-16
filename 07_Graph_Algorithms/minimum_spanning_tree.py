"""
Minimum Spanning Tree (MST) in Python
1. Kruskal's Algorithm using Disjoint Set Union (DSU) in O(E log E)
2. Prim's Algorithm using heapq in O(E log V)
"""

import sys

class DSU:
    def __init__(self, n):
        self.parent = list(range(n + 1))
        self.size = [1] * (n + 1)

    def find(self, x):
        while x != self.parent[x]:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        root_a = self.find(a)
        root_b = self.find(b)
        if root_a == root_b:
            return False
        if self.size[root_a] < self.size[root_b]:
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a
        self.size[root_a] += self.size[root_b]
        return True

def kruskal_mst(n, edges):
    """
    edges: list of (u, v, weight)
    Returns:
        total_weight: Cost of MST
        mst_edges: Edges included in MST
    """
    edges.sort(key=lambda e: e[2])
    dsu = DSU(n)
    
    total_weight = 0
    mst_edges = []
    
    for u, v, w in edges:
        if dsu.union(u, v):
            total_weight += w
            mst_edges.append((u, v, w))
            if len(mst_edges) == n - 1:
                break
                
    if len(mst_edges) < n - 1:
        return -1, []  # Graph is disconnected
        
    return total_weight, mst_edges

TEST_CASES = [
    (
        "4 5\n1 2 1\n1 3 4\n2 3 2\n2 4 5\n3 4 3",
        "6"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    it = iter(tokens)
    n = int(next(it))
    m = int(next(it))
    edges = []
    for _ in range(m):
        u = int(next(it))
        v = int(next(it))
        w = int(next(it))
        edges.append((u, v, w))
        
    cost, mst = kruskal_mst(n, edges)
    sys.stdout.write(str(cost) + "\n")

if __name__ == "__main__":
    solve()
