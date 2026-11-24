# Minimum Spanning Tree

An MST connects all vertices with $n - 1$ edges of minimum total weight. Kruskal sorts the edges and applies DSU; Prim grows one component from a start vertex with a heap.

---

## 1. Kruskal with DSU

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
    sort(edges.begin(), edges.end());                        // by weight first

    vector<int> parent(n), size(n, 1);
    iota(parent.begin(), parent.end(), 0);
    auto find = [&](int x) {
        while (parent[x] != x) x = parent[x] = parent[parent[x]];
        return x;
    };
    long long total = 0;
    int taken = 0;
    for (auto [w, u, v] : edges) {
        int a = find(u), b = find(v);
        if (a == b) continue;                                // closes a cycle
        if (size[a] < size[b]) swap(a, b);
        parent[b] = a;
        size[a] += size[b];
        total += w;
        if (++taken == n - 1) break;
    }
    cout << (taken == n - 1 ? to_string(total) : string("impossible")) << '\n';
}
```

Three-way comparison on the tuple sorts by weight, then by endpoints — deterministic and duplicate-safe.

---

## 2. Prim with a Lazy Heap

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;
    vector<vector<pair<long long, int>>> adj(n);
    for (int i = 0; i < m; ++i) {
        int u, v;
        long long w;
        cin >> u >> v >> w;
        adj[u - 1].push_back({w, v - 1});
        adj[v - 1].push_back({w, u - 1});
    }
    vector<char> used(n, 0);
    priority_queue<pair<long long, int>, vector<pair<long long, int>>, greater<>> heap;
    heap.push({0, 0});
    long long total = 0;
    int taken = 0;
    while (!heap.empty() && taken < n) {
        auto [w, u] = heap.top();
        heap.pop();
        if (used[u]) continue;
        used[u] = 1;
        total += w;
        ++taken;
        for (auto [nw, v] : adj[u]) if (!used[v]) heap.push({nw, v});
    }
    cout << (taken == n ? to_string(total) : string("impossible")) << '\n';
}
```

---

## 3. The Cut Property

For any cut, the lightest edge crossing it belongs to some MST. Kruskal is that edge for the growing prefix of the sort; Prim takes it for the cut between used and unused vertices. That proof is what makes both correct.

---

## 4. Variants

- Maximum spanning tree: negate weights or sort descending.
- Second-best MST: build the MST, then for every non-tree edge consider swapping it with the heaviest edge on its tree path (needs binary lifting).
- "MST of a grid": implicit edges from neighbouring cells.

---

## 5. Complexity Notes

- Kruskal $O(m \log m)$; Prim $O((n + m) \log n)$; Borůvka $O(m \log n)$ parallel-friendly.
- Dense graphs favour an $O(n^2)$ Prim without a heap.
- The answer fits `long long`; $2 \times 10^5$ edges of $10^9$ sum past $2^{31}-1$.