---
tags:
  - cp/code
  - cp/graph
---

[[ComProg/Home|🏠 Dashboard]] ❯ [[ComProg/07_Graph_Algorithms/README|07_Graph_Algorithms]] ❯ **Shortest Path Dijkstra**

---

# Shortest Path Dijkstra

> [!abstract] Implementation Note
> This note contains the complete, battle-tested Python implementation of **Shortest Path Dijkstra**.
> Source file: `ComProg/07_Graph_Algorithms/shortest_path_dijkstra.py`
> Run test runner: `python3 run_tests.py ComProg/07_Graph_Algorithms/shortest_path_dijkstra.py`

---

## 🐍 Python Implementation

```python
"""
Dijkstra's Shortest Path Algorithm in Python
- Finds shortest paths from a single source to all vertices with non-negative edge weights.
- Path reconstruction supported.
Time Complexity: O((V + E) log V) using heapq.
"""

import sys
import heapq

def dijkstra(adj, start, n):
    """
    Computes shortest distances from 'start' to all vertices in 1 ... n.
    adj[u] = [(v, weight), ...]
    Returns (dist, parent)
    """
    INF = float('inf')
    dist = [INF] * (n + 1)
    parent = [-1] * (n + 1)
    
    dist[start] = 0
    # Min-heap stores tuples of (distance, vertex)
    heap = [(0, start)]
    
    while heap:
        d, u = heapq.heappop(heap)
        
        # Skip stale entries
        if d > dist[u]:
            continue
            
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                heapq.heappush(heap, (dist[v], v))
                
    return dist, parent

def get_path(parent, target):
    path = []
    curr = target
    while curr != -1:
        path.append(curr)
        curr = parent[curr]
    path.reverse()
    return path

TEST_CASES = [
    (
        "5 6 1\n1 2 2\n1 3 4\n2 3 1\n2 4 7\n3 5 3\n4 5 1",
        "0 2 3 7 6"
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
    
    adj = [[] for _ in range(n + 1)]
    for _ in range(m):
        u = int(next(it))
        v = int(next(it))
        w = int(next(it))
        adj[u].append((v, w))
        adj[v].append((u, w))
        
    dist, parent = dijkstra(adj, s, n)
    res = [str(dist[i]) if dist[i] != float('inf') else "-1" for i in range(1, n + 1)]
    sys.stdout.write(" ".join(res) + "\n")

if __name__ == "__main__":
    solve()
```

---

## ⚡ Complexity & Analysis
- **Time Complexity:** See docstrings and implementation above.
- **Space Complexity:** See docstrings and implementation above.

---

⏮️ [[ComProg/07_Graph_Algorithms/README|Back to 07_Graph_Algorithms]] | 🏠 [[ComProg/Home|Dashboard]]
