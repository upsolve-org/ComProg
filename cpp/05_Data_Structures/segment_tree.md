# Segment Tree

A segment tree is an array of aggregates over a tree-shaped range decomposition. Build is $\Theta(n)$, point update and range query are $O(\log n)$, and it stores the aggregate at every node so any **non-invertible** combine works (`min`, `max`, `gcd`).

---

## 1. Iterative Min Tree

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, q;
    cin >> n >> q;
    size_t base = 1;
    while (base < (size_t)n) base <<= 1;                     // power of two
    vector<long long> tree(2 * base, LLONG_MAX);
    for (int i = 0; i < n; ++i) cin >> tree[base + i];
    for (size_t i = base; i-- > 1;) tree[i] = min(tree[2 * i], tree[2 * i + 1]);
    auto query = [&](size_t l, size_t r) {                   // [l, r)
        long long best = LLONG_MAX;
        for (l += base, r += base; l < r; l >>= 1, r >>= 1) {
            if (l & 1) best = min(best, tree[l++]);
            if (r & 1) best = min(best, tree[--r]);
        }
        return best;
    };
    while (q--) {
        int l, r;
        cin >> l >> r;
        cout << query(l - 1, r) << '\n';
    }
}
```

The `l & 1` / `r & 1` tests climb only the nodes that actually cover the query.

---

## 2. Recursive Form with a Lambda

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, q;
    cin >> n >> q;
    vector<long long> a(n), tree(4 * n, 0);
    for (auto &x : a) cin >> x;

    auto build = [&](auto &&self, int node, int lo, int hi) -> void {
        if (lo + 1 == hi) { tree[node] = a[lo]; return; }
        int mid = (lo + hi) / 2;
        self(self, 2 * node, lo, mid);
        self(self, 2 * node + 1, mid, hi);
        tree[node] = max(tree[2 * node], tree[2 * node + 1]);
    };
    build(build, 1, 0, n);

    auto query = [&](auto &&self, int node, int lo, int hi, int l, int r) -> long long {
        if (r <= lo || hi <= l) return LLONG_MIN;
        if (l <= lo && hi <= r) return tree[node];
        int mid = (lo + hi) / 2;
        return max(self(self, 2 * node, lo, mid, l, r), self(self, 2 * node + 1, mid, hi, l, r));
    };

    while (q--) {
        int l, r;
        cin >> l >> r;
        cout << query(query, 1, 0, n, l - 1, r) << '\n';
    }
}
```

A recursive lambda needs `auto &&self` as its first parameter to call itself; `4 * n` nodes cover any `n` down to 1.

---

## 3. Lazy Propagation Skeleton

Range add plus range max: store a `lazy` add per node and push it down before descending.

```cpp
#include <bits/stdc++.h>
using namespace std;

int n;
vector<long long> tree, lazy;
auto apply = [](int node, long long delta) { tree[node] += delta; lazy[node] += delta; };
```

---

## 4. Where Segment Trees Lose to Fenwick

- Prefix-only aggregates with an invertible operator (`+`, `^`): Fenwick is $O(n)$ memory and far fewer operations.
- Offline "next smaller" lookups: a monotonic stack.
- Point queries after range adds: difference array plus prefix, or a Fenwick.

---

## 5. Complexity Notes

- Build $O(n)$; update and query $O(\log n)$; memory $O(n)$ (or $O(2^{\lceil \log n \rceil + 1})$ for the power-of-two base).
- Recursive touches cost about 20 function calls per query; the iterative version about half.
- Lazy propagation keeps range updates $O(\log n)$ but needs the operator to distribute over the combine.