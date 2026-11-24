# Bridges and Articulation Points

An edge is a **bridge** if removing it disconnects its component; a vertex is an **articulation point** if removing it does. Both are found with DFS timestamps: `low[v]` is the smallest `tin` reachable from `v`'s subtree through one back edge.

---

## 1. Tarjan Skeleton

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;
    vector<pair<int, int>> edges(m);
    vector<vector<int>> adj(n);
    for (auto &[u, v] : edges) {
        cin >> u >> v;
        --u, --v;
        adj[u].push_back(v);
        adj[v].push_back(u);
    }
    vector<int> tin(n, -1), low(n);
    int timer = 0;
    set<pair<int, int>> bridges;
    set<int> articulation;

    function<void(int, int)> dfs = [&](int u, int parentEdge) {
        tin[u] = low[u] = timer++;
        int children = 0;
        for (int id : adj[u]) {
            auto [a, b] = edges[id];
            int v = a == u ? b : a;
            if (id == parentEdge) continue;                  // the edge we came in on, not itself
            if (tin[v] != -1) low[u] = min(low[u], tin[v]);  // back edge
            else {
                dfs(v, id);
                ++children;
                low[u] = min(low[u], low[v]);
                if (low[v] > tin[u]) bridges.insert({min(u, v), max(u, v)});
                if (parentEdge != -1 && low[v] >= tin[u]) articulation.insert(u);
            }
        }
        if (parentEdge == -1 && children > 1) articulation.insert(u);
    };
    for (int v = 0; v < n; ++v) if (tin[v] == -1) dfs(v, -1);

    cout << bridges.size() << ' ' << articulation.size() << '\n';
    for (auto [a, b] : bridges) cout << a + 1 << ' ' << b + 1 << '\n';
    for (int v : articulation) cout << v + 1 << ' ';
    cout << '\n';
}
```

**Edge ids are essential.** With parallel edges, skipping the parent *vertex* hides the second copy and wrongly reports a bridge.

---

## 2. The Two Conditions Read Exactly Like the Definition

- `low[v] > tin[u]`: nothing below `v` escapes above `u`, so this edge is the only way out — a bridge.
- `low[v] >= tin[u]` with a real parent: `v`'s subtree cannot climb over `u`, so `u` is an articulation point.
- A DFS root is an articulation point with more than one child.

---

## 3. 2-Vertex-Connected Components

A stack of visited vertices plus the same conditions splits the graph into blocks: pop until the child `v` when `low[v] >= tin[u]`. Each block is a component with no articulation points of its own.

---

## 4. Recursion Depth

The DFS can go $2 \times 10^5$ deep. Convert to an explicit stack by storing `(vertex, next edge index)`, or compile with a larger stack locally and rely on the judge's 8 MB.

---

## 5. Complexity Notes

- $O(n + m)$ with the edge list; `std::function` adds an indirect call per step.
- Memory is $O(n + m)$; the recursion holds one frame per depth.
- Bridges are undirected-only; in a directed graph the equivalent is a strongly connected component split (Tarjan/Kosaraju).