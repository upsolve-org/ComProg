# BFS and DFS Traversal

Both traversals visit each reachable vertex once. BFS explores by distance and therefore finds shortest paths in unweighted graphs; DFS explores by depth and is the base of every timestamp algorithm (bridges, topological sort, tree orders).

---

## 1. BFS with an Explicit Queue

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
    for (int d : distance) cout << d << ' ';
    cout << '\n';
}
```

The distance array doubles as the visited mark: a vertex is enqueued exactly once.

---

## 2. Multi-Source BFS

Seed the queue with every source and all distances start at 0; the first arrival at any cell is the nearest source.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int h, w;
    cin >> h >> w;
    vector<string> grid(h);
    for (auto &row : grid) cin >> row;
    vector<vector<int>> distance(h, vector<int>(w, -1));
    queue<pair<int, int>> frontier;
    for (int r = 0; r < h; ++r)
        for (int c = 0; c < w; ++c)
            if (grid[r][c] == 'S') { distance[r][c] = 0; frontier.push({r, c}); }
    const int dr[] = {1, -1, 0, 0}, dc[] = {0, 0, 1, -1};
    while (!frontier.empty()) {
        auto [r, c] = frontier.front();
        frontier.pop();
        for (int d = 0; d < 4; ++d) {
            int nr = r + dr[d], nc = c + dc[d];
            if (nr < 0 || nc < 0 || nr >= h || nc >= w) continue;
            if (grid[nr][nc] == '#' || distance[nr][nc] != -1) continue;
            distance[nr][nc] = distance[r][c] + 1;
            frontier.push({nr, nc});
        }
    }
    cout << distance[h - 1][w - 1] << '\n';
}
```

---

## 3. Iterative DFS

Recursive DFS on $2 \times 10^5$ vertices is close to the stack limit; the explicit vector stack below has none.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;
    vector<vector<int>> adj(n);
    for (int i = 0; i < m; ++i) { int u, v; cin >> u >> v; adj[u - 1].push_back(v - 1); }
    vector<char> seen(n, 0);
    vector<int> finish, stack{0};
    seen[0] = 1;
    while (!stack.empty()) {
        int u = stack.back();
        bool descended = false;
        for (int v : adj[u])
            if (!seen[v]) { seen[v] = 1; stack.push_back(v); descended = true; break; }
        if (!descended) { finish.push_back(u); stack.pop_back(); }
    }
    for (int v : finish) cout << v + 1 << ' ';
    cout << '\n';
}
```

`finish` is the post-order; reversing it gives a topological order on a DAG.

---

## 4. Connected Components

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
    vector<int> component(n, -1);
    int count = 0;
    queue<int> frontier;
    for (int start = 0; start < n; ++start) {
        if (component[start] != -1) continue;
        component[start] = count;
        frontier.push(start);
        while (!frontier.empty()) {
            int u = frontier.front();
            frontier.pop();
            for (int v : adj[u])
                if (component[v] == -1) { component[v] = count; frontier.push(v); }
        }
        ++count;
    }
    cout << count << '\n';
}
```

---

## 5. Complexity Notes

- $O(n + m)$ time and memory for every traversal.
- Each edge is inspected twice on an undirected graph.
- `queue` is a deque underneath; `vector` as a stack is a touch faster on modern caches.