# Disjoint Set Union

DSU maintains a partition of $\{0, \dots, n-1\}$ under two operations: `find(x)` (the representative of `x`'s set) and `unite(a, b)`. Used for Kruskal, connectivity, and cycle detection, its optimisations cut the cost to $O(\alpha(n))$, effectively a constant below 5 for any real $n$.

---

## 1. Path Halving and Union by Size

```cpp
#include <bits/stdc++.h>
using namespace std;

struct DSU {
    vector<int> parent, size;
    int components;
    explicit DSU(int n) : parent(n), size(n, 1), components(n) {
        iota(parent.begin(), parent.end(), 0);
    }
    int find(int x) {
        while (parent[x] != x) x = parent[x] = parent[parent[x]];  // halve the path
        return x;
    }
    bool unite(int a, int b) {
        a = find(a), b = find(b);
        if (a == b) return false;
        if (size[a] < size[b]) swap(a, b);                          // smaller set hangs under larger
        parent[b] = a;
        size[a] += size[b];
        --components;
        return true;
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, q;
    cin >> n >> q;
    DSU dsu(n);
    while (q--) {
        int type, a, b;
        cin >> type >> a >> b;
        if (type == 1) dsu.unite(a - 1, b - 1);
        else cout << (dsu.find(a - 1) == dsu.find(b - 1) ? "YES\n" : "NO\n");
    }
}
```

---

## 2. Why Not a Plain Tree

Without union by size a chain `0 ← 1 ← 2 ← …` forms and `find` degrades to $O(n)$. Without path halving the chain persists across queries. Both together amortise to $O(\alpha(n))$.

---

## 3. Rollback DSU

A DSU **without** path compression (only union by size) can be rolled back, so it composes with DFS in offline problems.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct RollbackDSU {
    vector<int> parent, size;
    vector<pair<int, int>> history;                  // (child, parent)
    explicit RollbackDSU(int n) : parent(n), size(n, 1) { iota(parent.begin(), parent.end(), 0); }
    int find(int x) const { while (parent[x] != x) x = parent[x]; return x; }
    void unite(int a, int b) {
        a = find(a), b = find(b);
        if (a == b) { history.push_back({-1, -1}); return; }
        if (size[a] < size[b]) swap(a, b);
        history.push_back({b, a});
        parent[b] = a;
        size[a] += size[b];
    }
    void rollback() {
        auto [child, par] = history.back();
        history.pop_back();
        if (child == -1) return;
        parent[child] = child;
        size[par] -= size[child];
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    RollbackDSU dsu(3);
    dsu.unite(0, 1);
    dsu.unite(1, 2);
    cout << dsu.find(0) << ' ' << dsu.find(2) << '\n';   // same root
    dsu.rollback();
    dsu.rollback();
    cout << (dsu.find(0) == dsu.find(1)) << '\n';        // 0, separate again
}
```

---

## 4. DSU on Intervals ("Next Unused Cell")

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, q;
    cin >> n >> q;
    vector<int> next(n + 1);
    iota(next.begin(), next.end(), 0);               // next[i] is the smallest unused at or after i
    while (q--) {
        int l, r;
        cin >> l >> r;
        vector<int> used;
        for (int i = l; i <= r; i = next[i] + 1) { if (next[i] != i) continue; used.push_back(i); }
        for (int i : used) next[i] = i + 1;
        for (int i : used) cout << i << ' ';
        cout << '\n';
    }
}
```

---

## 5. Complexity Notes

- Amortised $O(\alpha(n))$; memory $O(n)$.
- Union by rank/size alone is $O(\log n)$ worst case, still fine layered under another structure.
- Rollback DSU drops to $O(\log n)$ per operation and does not compress.