---
tags:
  - cp/trees
  - cp/graphs
---

[[Home|🏠 Dashboard]] ❯ **Module 08: Trees and Lowest Common Ancestor (LCA)**

---

# Module 08: Trees and Lowest Common Ancestor (LCA)

*References from [[12_Reference_and_Catalog/codeforces_catalog_full.md|Codeforces Catalog]]:*
- [Trees category on Codeforces](https://codeforces.com/catalog)
- [Binary Lifting, No Memory Wasted by Urbanowicz](https://codeforces.com/blog/entry/74847)

A tree is an undirected connected acyclic graph with $N$ vertices and $N - 1$ edges. Trees possess special topological properties that enable extremely efficient queries.

---

## 🌲 Core Tree Techniques

### 1. Euler Tour Technique (Tree Flattening)
By recording the entry and exit timestamps during a single DFS traversal (`tin[u]` and `tout[u]`), the entire subtree of node $u$ maps to a contiguous 1D range:
$$[\text{tin}[u], \text{tout}[u]]$$
- Subtree sum updates or queries reduce to standard 1D Fenwick or Segment Tree operations!

### 2. Binary Lifting & Lowest Common Ancestor (LCA)
- Precomputes an ancestor table:
  $$\text{up}[k][u] = 2^k\text{-th ancestor of node } u$$
- Table size: $O(N \log N)$, preprocessing time: $O(N \log N)$.
- Supports:
  - $K$-th ancestor query in $O(\log N)$.
  - Lowest Common Ancestor (LCA) of nodes $u$ and $v$ in $O(\log N)$.
  - Distance between $u$ and $v$: $\text{depth}[u] + \text{depth}[v] - 2 \cdot \text{depth}[\text{LCA}(u, v)]$.

---

## 📂 Included Source Files & Templates
- 📜 [[08_Trees_and_LCA/tree_basics_and_euler_tour.py|tree_basics_and_euler_tour.py]] — Euler Tour tree flattening for subtree range queries
- 🪜 [[08_Trees_and_LCA/binary_lifting_lca.py|binary_lifting_lca.py]] — Binary lifting table for LCA and tree distance in $O(\log N)$

---

⏮️ Previous: [[07_Graph_Algorithms/README|07 Graph Algorithms]] | 🏠 [[Home|Dashboard]] | ⏭️ Next: [[09_Mathematics_and_Number_Theory/README|09 Math & Number Theory]]
