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

Parents `1 1 2 2 3 3` describe this tree. `tin` and `tout` only have to be written once each; armed with them, subtree queries become prefix sums:

```python
tin  = [0, 1, 7, 2, 4, 8, 10]
tout = [13, 6, 12, 3, 5, 9, 11]
value = [0, 5, 2, 1, 1, 4, 3]              # value per node

flat = [0] * 14                            # 1D array indexed by slot
for node in range(7):
    flat[tin[node]] = value[node]          # node 0 lands in slot 0, node 1 in slot 1, ...

prefix = [0]
for v in flat:
    prefix.append(prefix[-1] + v)
print(prefix[tout[1] + 1] - prefix[tin[1]])   # 7: value of node 1 plus its two leaves
```

The whole tree sums to 16, and subtree 1 answers with the same two lookups as any array range.

```python
parent = [-1, 0, 0, 1, 1, 2, 2]
children = [[] for _ in parent]
for node, p in enumerate(parent):
    if p >= 0:
        children[p].append(node)

tin, tout, clock = [-1] * len(parent), [-1] * len(parent), [0]


def dfs(u):
    tin[u] = clock[0]
    clock[0] += 1
    for c in children[u]:
        dfs(c)
    tout[u] = clock[0]
    clock[0] += 1


dfs(0)
print(tin, tout)                         # [0, 1, 7, 2, 4, 8, 10] [13, 6, 12, 3, 5, 9, 11]
print(tin[3], tout[3], tin[0], tout[0])  # 2 3 0 13 : a leaf owns one slot, the root owns all 14
```

The leaves `3` and `4` fill slots `2–5` between `tin[1] = 1` and `tout[1] = 6`, so every node of subtree 1 falls inside `[1, 6]` and nothing else does. `tin` and `tout` also answer "is `x` an ancestor of `y`": `tin[x] <= tin[y] < tout[x]`.

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
