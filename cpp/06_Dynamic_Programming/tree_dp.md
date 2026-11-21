# Tree DP

Tree DP folds the answer over children during a post-order. Every node's state is computed after all of its children's states, so recursion or an explicit reverse BFS order both work.

---

## 1. Subtree Sizes and Counts

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<vector<int>> children(n);
    for (int v = 1; v < n; ++v) { int p; cin >> p; children[p - 1].push_back(v); }
    vector<int> order, size(n, 1);
    size_t head = 0;
    order.push_back(0);
    while (head < order.size()) {                            // BFS order
        for (int v : children[order[head]]) order.push_back(v);
        ++head;
    }
    for (size_t i = order.size(); i-- > 1;) {                // reverse BFS: children before parents
        int u = order[i];
        for (int p = 0; p < n; ++p) {
            if (find(children[p].begin(), children[p].end(), u) != children[p].end()) {
                size[p] += size[u];
                break;
            }
        }
    }
    for (int s : size) cout << s << ' ';
    cout << '\n';
}
```

The quadratic `find` here is fine for small inputs; the parent array makes it $O(1)$.

---

## 2. Parent Array Version with Explicit Reverse Order

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<int> parent(n, -1), order{0};
    for (int v = 1; v < n; ++v) { cin >> parent[v]; --parent[v]; order.push_back(v); }
    vector<int> size(n, 1), depth(n, 0);
    for (int v = 1; v < n; ++v) depth[v] = depth[parent[v]] + 1;   // parents precede children in input
    for (int i = n - 1; i > 0; --i) size[parent[order[i]]] += size[order[i]];
    int best = 0;
    for (int v = 0; v < n; ++v) best = max(best, size[v] + depth[v]);
    cout << best << '\n';
}
```

The parent always has a smaller index, so the input order is already a valid topological order.

---

## 3. Taking and Skipping a Node

The classic "maximum independent set on a tree": keep `take[u]` and `skip[u]`.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<long long> weight(n);
    for (auto &x : weight) cin >> x;
    vector<vector<int>> children(n);
    for (int v = 1; v < n; ++v) { int p; cin >> p; children[p - 1].push_back(v); }

    vector<array<long long, 2>> dp(n);
    function<void(int)> dfs = [&](int u) {
        dp[u][1] = weight[u];
        for (int v : children[u]) {
            dfs(v);
            dp[u][0] += max(dp[v][0], dp[v][1]);
            dp[u][1] += dp[v][0];
        }
    };
    dfs(0);
    cout << max(dp[0][0], dp[0][1]) << '\n';
}
```

`dp[u][0]` sums each child's best of both; `dp[u][1]` may only take children that are skipped.

---

## 4. Rerooting

When the answer is asked for every root, compute the up/down contributions once from node 0, then swap the child into place before descending. The two-pass shape keeps the total $O(n)$ instead of $O(n^2)$.

---

## 5. Complexity Notes

- Every edge is visited once per pass: $O(n)$.
- Recursion depth is the tree height; a path tree needs an explicit order past $\sim 10^5$ nodes.
- `vector<vector<int>>` adjacency costs one allocation per node; a flat CSR layout avoids that.