---
tags:
  - cpp/graphs
---

[[Home|🏠 Dashboard]] ❯ **C++ Module 07: Graph Algorithms**

---

# C++ Module 07: Graph Algorithms

Every graph problem starts with a representation and a promise about weights. Adjacency lists of `vector<vector<int>>` fit $2 \times 10^5$ edges; a flat CSR pair of arrays saves allocations when the limits are tighter. The algorithm then follows from the weight domain: unweighted means BFS, non-negative weights mean Dijkstra, anything signed means Bellman–Ford.

---

## 🗺️ BFS Distance Layer

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;
    vector<vector<int>> adj(n);
    for (int i = 0; i < m; ++i) {
        int u, v;
        cin >> u >> v;
        adj[u - 1].push_back(v - 1);
        adj[v - 1].push_back(u - 1);
    }
    vector<int> distance(n, -1);
    queue<int> frontier;
    distance[0] = 0;
    frontier.push(0);
    while (!frontier.empty()) {
        int u = frontier.front();
        frontier.pop();
        for (int v : adj[u])
            if (distance[v] == -1) { distance[v] = distance[u] + 1; frontier.push(v); }
    }
    cout << distance[n - 1] << '\n';
}
```

---

## 🔗 Topological Order and Cycle Detection

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;
    vector<vector<int>> adj(n);
    vector<int> indegree(n, 0);
    for (int i = 0; i < m; ++i) {
        int u, v;
        cin >> u >> v;
        adj[u - 1].push_back(v - 1);
        ++indegree[v - 1];
    }
    queue<int> ready;
    for (int v = 0; v < n; ++v) if (!indegree[v]) ready.push(v);
    vector<int> order;
    while (!ready.empty()) {
        int u = ready.front();
        ready.pop();
        order.push_back(u);
        for (int v : adj[u]) if (--indegree[v] == 0) ready.push(v);
    }
    if ((int)order.size() != n) { cout << "cycle\n"; return 0; }
    for (int v : order) cout << v + 1 << ' ';
    cout << '\n';
}
```

Kahn's algorithm with a queue is BFS on the condensation; the leftover count is the cycle test.

---

## 🧭 Dijkstra with a Lazy Heap

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;
    vector<vector<pair<int, long long>>> adj(n);
    for (int i = 0; i < m; ++i) {
        int u, v;
        long long w;
        cin >> u >> v >> w;
        adj[u - 1].push_back({v - 1, w});
    }
    vector<long long> distance(n, LLONG_MAX);
    priority_queue<pair<long long, int>, vector<pair<long long, int>>, greater<>> heap;
    distance[0] = 0;
    heap.push({0, 0});
    while (!heap.empty()) {
        auto [d, u] = heap.top();
        heap.pop();
        if (d != distance[u]) continue;                       // stale copy, skip it
        for (auto [v, w] : adj[u])
            if (d + w < distance[v]) { distance[v] = d + w; heap.push({distance[v], v}); }
    }
    cout << (distance[n - 1] == LLONG_MAX ? -1 : distance[n - 1]) << '\n';
}
```

`greater<>` makes `priority_queue` a min-heap; pushing the pair `(distance, vertex)` compares distances first.

---

## 🌉 Articulation Points via DFS Timestamps

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;
    vector<vector<int>> adj(n);
    for (int i = 0; i < m; ++i) {
        int u, v;
        cin >> u >> v;
        adj[u - 1].push_back(v - 1);
        adj[v - 1].push_back(u - 1);
    }
    vector<int> tin(n, -1), low(n), answer;
    int timer = 0;
    function<void(int, int)> dfs = [&](int u, int parent) {
        tin[u] = low[u] = timer++;
        int children = 0;
        for (int v : adj[u]) {
            if (v == parent) continue;
            if (tin[v] != -1) low[u] = min(low[u], tin[v]);
            else {
                dfs(v, u);
                ++children;
                low[u] = min(low[u], low[v]);
                if (parent != -1 && low[v] >= tin[u]) answer.push_back(u);
            }
        }
        if (parent == -1 && children > 1) answer.push_back(u);
    };
    dfs(0, -1);
    sort(answer.begin(), answer.end());
    answer.erase(unique(answer.begin(), answer.end()), answer.end());
    for (int v : answer) cout << v + 1 << ' ';
    if (answer.empty()) cout << "none";
    cout << '\n';
}
```

---

## 🪢 Minimum Spanning Tree (Kruskal)

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;
    vector<tuple<long long, int, int>> edges(m);
    for (auto &[w, u, v] : edges) { cin >> u >> v >> w; --u, --v; }
    sort(edges.begin(), edges.end());
    vector<int> parent(n);
    iota(parent.begin(), parent.end(), 0);
    function<int(int)> find = [&](int x) {
        while (parent[x] != x) x = parent[x] = parent[parent[x]];
        return x;
    };
    long long total = 0;
    int taken = 0;
    for (auto [w, u, v] : edges) {
        u = find(u), v = find(v);
        if (u == v) continue;
        parent[v] = u;
        total += w;
        if (++taken == n - 1) break;
    }
    cout << (taken == n - 1 ? to_string(total) : "impossible") << '\n';
}
```

---

## ⏱️ Complexity Notes

- BFS/DFS $O(n + m)$; Dijkstra $O((n + m) \log n)$ with a heap; Bellman–Ford $O(nm)$.
- Tarjan bridges/articulation points are $O(n + m)$ but recursive; explicit stacks avoid the depth limit.
- Kruskal is $O(m \log m)$ from the sort.

---

## ✅ Checklist

- 1-based input converted once at read time, then 0-based internally.
- Unreachable sentinels (`-1`, `LLONG_MAX`) handled at output.
- Non-negative weights confirmed before Dijkstra.
- Recursion depth estimated before choosing DFS.

---

## Included Source Files

- `graph_traversal_bfs_dfs.md`, `topological_sort.md`
- `shortest_path_dijkstra.md`, `shortest_path_bellman_floyd.md`
- `minimum_spanning_tree.md`, `bridges_and_articulation_points.md`