# Topological Sort

A topological order lists vertices so every edge points forward. It exists exactly when the digraph has no cycle, and it is the scheduling order of every DAG DP.

---

## 1. Kahn's Algorithm with a Queue

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
    order.reserve(n);
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

If fewer than `n` vertices come out, the remaining ones sit on a cycle.

---

## 2. Lexicographically Smallest Order

Swap the queue for `priority_queue<int, vector<int>, greater<int>>`.

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
    priority_queue<int, vector<int>, greater<int>> ready;
    for (int v = 0; v < n; ++v) if (!indegree[v]) ready.push(v);
    while (!ready.empty()) {
        int u = ready.top();
        ready.pop();
        cout << u + 1 << ' ';
        for (int v : adj[u]) if (--indegree[v] == 0) ready.push(v);
    }
    cout << '\n';
}
```

The greedy "smallest ready vertex" is correct because every ready vertex is free to go now, and the smallest one can only be helped by going first.

---

## 3. DFS Post-Order Variant

Reverse post-order of a DFS is a topological order. It needs a recursion or the explicit finish stack from the traversal note, and it does not detect cycles by itself (a back edge does).

---

## 4. DP on the Order

Once you have `order`, relax over it in that order:

```cpp
// longest path in a DAG, after building `order`
vector<long long> best(n, LLONG_MIN);
best[order[0]] = 0;
for (int u : order)
    for (int v : adj[u])
        if (best[u] != LLONG_MIN) best[v] = max(best[v], best[u] + weight(u, v));
```

---

## 5. Complexity Notes

- $O(n + m)$ with a queue; the priority version adds a log per vertex.
- A DAG with multiple sources supports several valid answers; the statement says which.
- Cycles make the order partial; output the smallest set with an order and say so.