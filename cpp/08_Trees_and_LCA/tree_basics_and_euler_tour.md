# Tree Basics, Diameter and Euler Tour

## 1. Tree Diameter in Two BFS Passes

The farthest vertex from any vertex lies on a diameter; the farthest from it is the other end. Both passes are BFS, so no recursion is needed.

```cpp
#include <bits/stdc++.h>
using namespace std;

pair<int, int> farthest(const vector<vector<int>> &adj, int start) {
    vector<int> distance(adj.size(), -1);
    queue<int> frontier{deque<int>({start})};
    distance[start] = 0;
    int best = start;
    while (!frontier.empty()) {
        int u = frontier.front();
        frontier.pop();
        if (distance[u] > distance[best]) best = u;
        for (int v : adj[u]) if (distance[v] == -1) { distance[v] = distance[u] + 1; frontier.push(v); }
    }
    return {best, distance[best]};
}

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
    int end = farthest(adj, 0).first;
    cout << farthest(adj, end).second << '\n';
}
```

---

## 2. Tree Centre from the Diameter

The centre is one or two vertices at the middle of a diameter path; the radius is `(diameter + 1) / 2`. Rebuild the diameter by storing parents along the second BFS and step forward.

```cpp
// after the second BFS kept `parent`, walk diameter / 2 steps from the second endpoint.
```

Edge-based and vertex-based problems differ here: for vertex centres step `diameter / 2` times.

---

## 3. Euler Tour for Subtree Ranges

Pre-order gives each subtree a contiguous `[tin, tout)` interval; a Fenwick tree over the tour then answers subtree sums.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<vector<int>> adj(n);
    for (int i = 0; i < n - 1; ++i) { int u, v; cin >> u >> v; adj[u - 1].push_back(v - 1); adj[v - 1].push_back(u - 1); }
    vector<long long> value(n);
    for (auto &x : value) cin >> x;

    vector<int> tin(n), order{0}, parent(n, -1);
    int timer = 0;
    for (size_t i = 0; i < order.size(); ++i) {
        int u = order[i];
        tin[u] = timer++;
        for (int v : adj[u]) if (v != parent[u]) { parent[v] = u; order.push_back(v); }
    }
    vector<long long> tour(n);
    for (int u = 0; u < n; ++u) tour[tin[u]] = value[u];
    for (int t : tour) cout << t << ' ';
    cout << '\n';
}
```

The full stack-free `[tin, tout)` pair uses the reversed `order`, exactly as module 07's traversal note comments.

---

## 4. `tout` from the Reversed Order

`tout[u]` is one past the largest `tin` in `u`'s subtree, which is `timer` after processing the subtree. Processing `order` backwards and taking a running maximum works:

```cpp
vector<int> tout(n);
int reach = 0;
for (int i = n - 1; i >= 0; --i) {
    int u = order[i];
    reach = max(reach, tin[u] + 1);
    tout[u] = reach;
    // reset reach when leaving a subtree? No: the parent closes later and keeps the larger reach.
}
```

---

## 5. Complexity Notes

- Both BFS passes $O(n)$; the tour $O(n)$.
- Memory $O(n)$; recursion is avoidable everywhere in this note.
- Farthest-pair works on trees only; in a general graph it is wrong.