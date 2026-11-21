# Binary Lifting and LCA

Binary lifting stores the $2^k$-th ancestor of every vertex, so an LCA query becomes $\Theta(\log n)$ jumps with no recursion after the build.

---

## 1. Build the Table

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
    vector<int> depth(n), order{0};
    for (size_t i = 0; i < order.size(); ++i) {
        int u = order[i];
        for (int v : adj[u]) if (v != up[0][u]) { up[0][v] = u; depth[v] = depth[u] + 1; order.push_back(v); }
    }
    for (int k = 1; k < LOG; ++k) for (int v = 0; v < n; ++v) up[k][v] = up[k - 1][up[k - 1][v]];
    while (q--) { int a, b; cin >> a >> b; --a, --b;
        if (depth[a] < depth[b]) swap(a, b);
        for (int k = LOG; k--;) if (depth[a] - (1 << k) >= depth[b]) a = up[k][a];
        if (a != b) { for (int k = LOG; k--;) if (up[k][a] != up[k][b]) { a = up[k][a]; b = up[k][b]; } a = up[0][a]; }
        cout << a + 1 << '\n';
    }
}
```

---

## 2. Query Steps, in Order

1. Lift the deeper vertex to the shallower depth, largest power first.
2. If they meet, that is the answer.
3. Lift both together from the largest power down while their ancestors differ.
4. The answer is the parent of either.

Step 3 must stop **before** equal ancestors; jumping onto equal ones loses the LCA.

---

## 3. Application Sketch: Path Queries

The LCA splits a vertex path into two root paths. A subtree sum with a Fenwick tree over the Euler tour then answers "sum on the path `u → v`" in $O(\log n)$ per endpoint after the inclusion–exclusion `sum(u) + sum(v) - 2 · sum(lca) + value(lca)`.

---

## 4. Memory

$O(n \log n)$ integers. At $n = 2 \times 10^5$ and `LOG = 18` that is $3.6 \times 10^6$ `int`s, about 14 MB — acceptable. Swapping to `uint32_t` halves nothing; `short` breaks past 65,535.

---

## 5. Complexity Notes

- Build $O(n \log n)$, query $O(\log n)$, memory $O(n \log n)$.
- The Euler-tour + segment-tree LCA is $O(n)$ memory and $O(\log n)$ per query but needs a full tour, which is $2n$ entries.
- Offline Tarjan LCA answers all queries in near-linear time with DSU, but needs the queries up front.