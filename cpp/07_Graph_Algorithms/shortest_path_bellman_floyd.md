# Bellman–Ford and Floyd–Warshall

Bellman–Ford handles negative weights and detects negative cycles; Floyd–Warshall answers all-pairs shortest paths in $O(n^3)$.

---

## 1. Bellman–Ford

Relax every edge $n - 1$ times. A further improving relaxation proves a negative cycle.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;
    struct Edge { int u, v; long long w; };
    vector<Edge> edges(m);
    for (auto &[u, v, w] : edges) { cin >> u >> v >> w; --u, --v; }

    const long long INF = LLONG_MAX / 4;
    vector<long long> distance(n, INF);
    distance[0] = 0;
    for (int round = 0; round < n - 1; ++round) {
        bool changed = false;
        for (auto [u, v, w] : edges)
            if (distance[u] != INF && distance[u] + w < distance[v]) {
                distance[v] = distance[u] + w;
                changed = true;
            }
        if (!changed) break;                                // converged early
    }
    for (auto [u, v, w] : edges)
        if (distance[u] != INF && distance[u] + w < distance[v]) { cout << "negative cycle\n"; return 0; }
    for (long long d : distance) cout << (d == INF ? -1 : d) << ' ';
    cout << '\n';
}
```

`LLONG_MAX / 4` leaves room for additions without wrapping; compare against `INF` first.

---

## 2. Floyd–Warshall

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;
    const long long INF = LLONG_MAX / 4;
    vector<vector<long long>> dist(n, vector<long long>(n, INF));
    for (int i = 0; i < n; ++i) dist[i][i] = 0;
    for (int i = 0; i < m; ++i) {
        int u, v;
        long long w;
        cin >> u >> v >> w;
        --u, --v;
        dist[u][v] = min(dist[u][v], w);                     // parallel edges: keep the cheapest
    }
    for (int k = 0; k < n; ++k)
        for (int i = 0; i < n; ++i) {
            if (dist[i][k] == INF) continue;
            for (int j = 0; j < n; ++j)
                if (dist[k][j] != INF) dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]);
        }
    for (int i = 0; i < n; ++i) cout << dist[i][n - 1] << ' ';
    cout << '\n';
}
```

`k` must be the outermost loop so intermediate vertices grow monotonically.

---

## 3. Negative Cycles in Floyd–Warshall

`dist[i][i] < 0` afterwards means `i` lies on a negative cycle; set the whole row and column to a sentinel if the statement asks for it.

---

## 4. Complexity Notes

- Bellman–Ford $O(nm)$; early stopping helps but does not change the bound.
- Floyd–Warshall $O(n^3)$ time and $\Theta(n^2)$ memory; practical to $n \approx 800$–$1000$ depending on the time limit. Transpose the loops or block the matrix to use the cache.
- Binary lifting (doubling) turns a constant-weight graph's $k$-relaxation into $O(n^3 \log k)$.