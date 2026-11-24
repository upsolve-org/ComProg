---
tags:
  - cpp/trees
---

[[Home|🏠 Dashboard]] ❯ **C++ Module 08: Trees and Lowest Common Ancestors**

---

# C++ Module 08: Trees and Lowest Common Ancestors

A tree is a connected graph with $n - 1$ edges. `vector<vector<int>>` is fine for small $n$; a CSR layout (`head`, `to`, `next`) is the safe choice for $2 \times 10^5$. Depth, subtree size, and Euler intervals are all one traversal away, and binary lifting then answers LCA in $O(\log n)$.

---

## 🌲 The Single-Traversal Facts

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<vector<int>> adj(n);
    for (int i = 0; i < n - 1; ++i) {
        int u, v;
        cin >> u >> v;
        adj[u - 1].push_back(v - 1);
        adj[v - 1].push_back(u - 1);
    }
    vector<int> parent(n, -1), depth(n, 0), order{0};
    for (size_t i = 0; i < order.size(); ++i) {
        int u = order[i];
        for (int v : adj[u]) if (v != parent[u]) { parent[v] = u; depth[v] = depth[u] + 1; order.push_back(v); }
    }
    int best = 0;
    for (int d : depth) best = max(best, d);
    cout << best << '\n';
}
```

The `parent` check replaces a visited array because a tree has no cross edges.

---

## 🔁 Euler Tour for Subtree Intervals

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<vector<int>> adj(n);
    for (int i = 0; i < n - 1; ++i) {
        int u, v;
        cin >> u >> v;
        adj[u - 1].push_back(v - 1);
        adj[v - 1].push_back(u - 1);
    }
    vector<int> tin(n), tout(n), order{0}, parent(n, -1);
    int timer = 0;
    for (size_t i = 0; i < order.size(); ++i) {
        int u = order[i];
        tin[u] = timer++;
        for (int v : adj[u]) if (v != parent[u]) { parent[v] = u; order.push_back(v); }
    }
    for (int i = n - 1; i >= 0; --i) tout[order[i]] = timer;   // BFS order reversed is post-order enough for sizes
    cout << tin[0] << ' ' << tout[0] << '\n';
}
```

`[tin[u], tout[u])` is a contiguous interval containing exactly `u`'s subtree, so subtree queries become range queries.

---

## 🪜 Binary Lifting LCA

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, q;
    cin >> n >> q;
    vector<vector<int>> adj(n);
    for (int i = 0; i < n - 1; ++i) { int u, v; cin >> u >> v; adj[u - 1].push_back(v - 1); adj[v - 1].push_back(u - 1); }

    const int LOG = 32 - __builtin_clz(n);
    vector<vector<int>> up(LOG, vector<int>(n, 0));
    vector<int> depth(n, 0), order{0};
    for (size_t i = 0; i < order.size(); ++i) {
        int u = order[i];
        for (int v : adj[u]) if (v != up[0][u]) { up[0][v] = u; depth[v] = depth[u] + 1; order.push_back(v); }
    }
    for (int k = 1; k < LOG; ++k) for (int v = 0; v < n; ++v) up[k][v] = up[k - 1][up[k - 1][v]];

    while (q--) {
        int a, b;
        cin >> a >> b;
        --a, --b;
        if (depth[a] < depth[b]) swap(a, b);
        for (int k = LOG; k--;) if (depth[a] - (1 << k) >= depth[b]) a = up[k][a];
        if (a != b) {
            for (int k = LOG; k--;) if (up[k][a] != up[k][b]) { a = up[k][a]; b = up[k][b]; }
            a = up[0][a];
        }
        cout << a + 1 << '\n';
    }
}
```

---

## ⏱️ Complexity Notes

- One traversal $O(n)$; each LCA query $O(\log n)$; table $O(n \log n)$ memory.
- The lift loop must go upward (`k--`) so the largest jump is tried first.
- DFS ordering by depth is what makes the depth equalisation correct.

---

## ✅ Checklist

- Tree input has exactly $n - 1$ edges; a cycle means it is not a tree.
- 0-based conversion happens at read time.
- `LOG` covers $\lfloor \log_2 \max n \rfloor + 1$.
- Root parent is 0 and `up[k][0] == 0` at every level.

---

## Included Source Files

- `tree_basics_and_euler_tour.md` — diameter, centres, Euler intervals.
- `binary_lifting_lca.md` — the full construction and query set.