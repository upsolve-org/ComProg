# Session Card: Recursion and Stacks

The default stack is 8 MB, roughly $10^5$ to $1.5 \times 10^5$ small frames. Past that, convert to an explicit stack.

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
    vector<int> next(n, 0), stack{0}, postOrder;
    vector<char> seen(n, 0);
    seen[0] = 1;
    while (!stack.empty()) {
        int u = stack.back();
        if (next[u] < (int)adj[u].size()) {
            int v = adj[u][next[u]++];               // save the cursor per frame
            if (!seen[v]) { seen[v] = 1; stack.push_back(v); }
        } else { postOrder.push_back(u); stack.pop_back(); }
    }
    for (int v : postOrder) cout << v + 1 << ' ';
    cout << '\n';
}
```

- Save the per-frame cursor in a `next[]` array; never re-scan edges from the start.
- Tree DFS: a `parent` array is enough, given a guaranteed tree root.
- Depth-first on $2 \times 10^5$ nodes: explicit stack or a widened stack (`ulimit -s`).
- Recursive lambdas need `function<>` or `auto &&self` and cost an indirect call per step.