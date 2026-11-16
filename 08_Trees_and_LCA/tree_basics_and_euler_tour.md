---
tags:
  - cp/code
  - cp/trees
---

[[ComProg/Home|🏠 Dashboard]] ❯ [[ComProg/08_Trees_and_LCA/README|08_Trees_and_LCA]] ❯ **Tree Basics And Euler Tour**

---

# Tree Basics And Euler Tour

> [!abstract] Implementation Note
> This note contains the complete, battle-tested Python implementation of **Tree Basics And Euler Tour**.
> Source file: `ComProg/08_Trees_and_LCA/tree_basics_and_euler_tour.py`
> Run test runner: `python3 run_tests.py ComProg/08_Trees_and_LCA/tree_basics_and_euler_tour.py`

---

## 🐍 Python Implementation

```python
"""
Euler Tour Technique (Tree Flattening) in Python
Maps tree subtrees into contiguous 1D intervals [tin[u], tout[u]].
Allows subtree sum queries and subtree updates via Fenwick Tree or Segment Tree.
Time Complexity: O(N) precomputation.
"""

import sys

sys.setrecursionlimit(300000)

class EulerTourTree:
    def __init__(self, n, adj, root=1):
        self.n = n
        self.adj = adj
        self.root = root
        
        self.tin = [0] * (n + 1)
        self.tout = [0] * (n + 1)
        self.depth = [0] * (n + 1)
        self.flat_order = []
        self.timer = 0
        
        self._dfs(root, 0, 0)

    def _dfs(self, u, p, d):
        self.timer += 1
        self.tin[u] = self.timer
        self.depth[u] = d
        self.flat_order.append(u)
        
        for v in self.adj[u]:
            if v != p:
                self._dfs(v, u, d + 1)
                
        self.tout[u] = self.timer

    def subtree_range(self, u):
        """Returns 1-based [left, right] interval of u's subtree in Euler tour."""
        return self.tin[u], self.tout[u]

    def is_ancestor(self, u, v):
        """Returns True if u is an ancestor of v."""
        return self.tin[u] <= self.tin[v] and self.tout[u] >= self.tout[v]

TEST_CASES = [
    (
        "5\n1 2\n1 3\n3 4\n3 5\n3",
        "3 5"
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
        
    query_node = int(next(it))
    tree = EulerTourTree(n, adj, root=1)
    l, r = tree.subtree_range(query_node)
    # Range width matches subtree size
    sys.stdout.write(f"{l} {r}\n")

if __name__ == "__main__":
    solve()
```

---

## ⚡ Complexity & Analysis
- **Time Complexity:** See docstrings and implementation above.
- **Space Complexity:** See docstrings and implementation above.

---

⏮️ [[ComProg/08_Trees_and_LCA/README|Back to 08_Trees_and_LCA]] | 🏠 [[ComProg/Home|Dashboard]]
