# Shortest Paths with Dijkstra

Dijkstra settles vertices in non-decreasing distance order. It needs **non-negative** weights; one negative edge can make it finalise a vertex too early.

---

## 1. The Lazy-Heap Form

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
        if (d != distance[u]) continue;
        for (auto [v, w] : adj[u])
            if (d + w < distance[v]) { distance[v] = d + w; heap.push({distance[v], v}); }
    }
    cout << (distance[n - 1] == LLONG_MAX ? -1 : distance[n - 1]) << '\n';
}
```

Stale entries are the price of not implementing a decrease-key; each edge can add at most one entry, so the heap holds $O(m)$ items.

---

## 2. 0/1 BFS with a Deque

Weights 0 and 1 only: push 0-edges to the front and 1-edges to the back, and the deque stays ordered.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;
    vector<vector<pair<int, int>>> adj(n);
    for (int i = 0; i < m; ++i) {
        int u, v, w;
        cin >> u >> v >> w;
        adj[u - 1].push_back({v - 1, w});
    }
    vector<int> distance(n, INT_MAX);
    deque<int> frontier{0};
    distance[0] = 0;
    while (!frontier.empty()) {
        int u = frontier.front();
        frontier.pop_front();
        for (auto [v, w] : adj[u]) {
            if (distance[u] + w >= distance[v]) continue;
            distance[v] = distance[u] + w;
            if (w == 0) frontier.push_front(v); else frontier.push_back(v);
        }
    }
    cout << (distance[n - 1] == INT_MAX ? -1 : distance[n - 1]) << '\n';
}
```

---

## 3. Path Reconstruction

```cpp
vector<int> parent(n, -1);          // set when relaxing: parent[v] = u
// afterwards, from n - 1 walk back while (v != 0) with step O(path length)
```

---

## 4. Why Negative Weights Fail

Take `s → a` weight 5 and `s → b` weight 1, `a → b` weight −10. Dijkstra pops `b` at 1, finalises it, then discovers `b` at −9. Any negative edge means Bellman–Ford.

---

## 5. Complexity Notes

- $O((n + m) \log n)$ with the binary heap.
- A Fibonacci heap hits $O(n \log n + m)$ but is missing from the STL.
- 0/1 BFS is $O(n + m)$; a deque push is $O(1)$ at both ends.
- Distances are `long long` whenever the weight sum can pass $2^{31}-1$.