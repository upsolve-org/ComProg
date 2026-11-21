---
tags:
  - cp/graphs
  - cp/algorithms
---

[[Home|🏠 Dashboard]] ❯ **Module 07: Graph Algorithms**

---

# Module 07: Graph Algorithms

*References from [[12_Reference_and_Catalog/codeforces_catalog_full.md|Codeforces Catalog]]:*
- [Graphs category on Codeforces](https://codeforces.com/catalog)
- [Depth-first Search category](https://codeforces.com/catalog)
- [Shortest Paths category](https://codeforces.com/catalog)

Graphs represent networks of relationships between vertices and edges. Mastery of graph traversals and shortest path algorithms is essential for competitive programming.

---

## 🗺️ Graph Representation in Python

```python
# Adjacency List for V vertices (0-indexed or 1-indexed)
adj = [[] for _ in range(V + 1)]
for u, v, weight in edges:
    adj[u].append((v, weight))
    adj[v].append((u, weight)) # If undirected
```

---

## ⚡ Core Graph Algorithms Cheatsheet

| Algorithm | Problem Solved | Time Complexity | Notes |
|---|---|---|---|
| **BFS** | Shortest path on unweighted graph | $O(V + E)$ | Uses `collections.deque` |
| **DFS** | Connected components, cycle detection, bipartite check | $O(V + E)$ | Requires `sys.setrecursionlimit` or explicit stack |
| **Kahn's (BFS)** | Topological sort on DAG | $O(V + E)$ | In-degree queue; detects cycles if processed nodes $< V$ |
| **Dijkstra** | Single-source shortest path (non-negative weights) | $O((V + E) \log V)$ | Uses `heapq` |
| **Bellman-Ford** | Single-source shortest path with negative edges | $O(V \cdot E)$ | Detects negative weight cycles |
| **Floyd-Warshall** | All-pairs shortest path | $O(V^3)$ | Simple 3 nested loops; practical for $V \le 400$ |
| **Kruskal's MST** | Minimum Spanning Tree | $O(E \log E)$ | Greedy edge sorting + DSU |
| **Tarjan's Bridges** | Cut edges and articulation points | $O(V + E)$ | Low-link and discovery time arrays via DFS |

---

## 🔦 Worked Example: Drain a Priority Queue
Dijkstra settles the smallest tentative distance, then relaxes the edges leaving it; a node whose pair is stale is skipped. With `s = 0` on the graph drawn in the overview, the settles come out in the order `0, 1, 2, 3, 4, 5` with distances `0, 1, 2, 4, 6, 8`:

```python
import heapq

graph = [[(1, 1), (2, 5)], [(2, 2), (3, 3)], [(4, 1)], [(4, 2), (5, 6)], [(5, 2)], []]


def dijkstra(graph, s):
    dist = [float("inf")] * len(graph)
    dist[s] = 0
    heap = [(0, s)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue                         # stale pair: u was settled cheaper
        for v, w in graph[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (dist[v], v))
    return dist


print(dijkstra(graph, 0))                    # [0, 1, 2, 4, 6, 8]
```

The trap is edge `0–2`: the heap first sees `2` at cost 5. The better route `0 → 1 → 2` costs 3, and `2` only gets its real distance when the queue reaches `1`. Stale `(5, 2)` pairs left in the heap are dropped by the `d > dist[u]` check instead of re-settling a node.

---

## 📂 Included Source Files & Templates
- 🚶 [[07_Graph_Algorithms/graph_traversal_bfs_dfs.py|graph_traversal_bfs_dfs.py]] — BFS shortest path & bipartite 2-coloring
- ⏳ [[07_Graph_Algorithms/topological_sort.py|topological_sort.py]] — Kahn's BFS algorithm for DAG topological sort
- ⚡ [[07_Graph_Algorithms/shortest_path_dijkstra.py|shortest_path_dijkstra.py]] — Dijkstra's shortest path with `heapq`
- 🌐 [[07_Graph_Algorithms/shortest_path_bellman_floyd.py|shortest_path_bellman_floyd.py]] — Bellman-Ford & Floyd-Warshall
- 🌲 [[07_Graph_Algorithms/minimum_spanning_tree.py|minimum_spanning_tree.py]] — Kruskal's MST using DSU
- 🌉 [[07_Graph_Algorithms/bridges_and_articulation_points.py|bridges_and_articulation_points.py]] — Tarjan's bridge & cutpoint algorithm

---

⏮️ Previous: [[06_Dynamic_Programming/README|06 Dynamic Programming]] | 🏠 [[Home|Dashboard]] | ⏭️ Next: [[08_Trees_and_LCA/README|08 Trees & LCA]]
