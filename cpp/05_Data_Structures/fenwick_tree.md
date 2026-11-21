# Fenwick Tree (Binary Indexed Tree)

A Fenwick tree stores prefix aggregates in $n$ cells where cell $i$ covers the range $(i - \text{lowbit}(i), i]$. Update walks upward by `i += i & -i`; query walks downward by `i -= i & -i`. Both are $O(\log n)$ with a tiny constant.

---

## 1. Point Add, Prefix Sum

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, q;
    cin >> n >> q;
    vector<long long> bit(n + 1, 0);
    auto add = [&](int i, long long delta) {
        for (; i <= n; i += i & -i) bit[i] += delta;
    };
    auto prefix = [&](int i) {
        long long sum = 0;
        for (; i > 0; i -= i & -i) sum += bit[i];
        return sum;
    };
    for (int i = 1; i <= n; ++i) { long long x; cin >> x; add(i, x); }
    while (q--) {
        char type;
        cin >> type;
        if (type == 'u') { int i; long long d; cin >> i >> d; add(i, d); }
        else { int l, r; cin >> l >> r; cout << prefix(r) - prefix(l - 1) << '\n'; }
    }
}
```

Range add + point query is the same code with the difference array swapped: `add(l, d); add(r + 1, -d);`.

---

## 2. Order Statistics on a Compressed Range

`k`-th smallest present value walks down the tree from the highest bit, so one lookup costs $O(\log V)$.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct Fenwick {
    vector<int> bit;
    int n, log;
    explicit Fenwick(int size) : bit(size + 1, 0), n(size), log(31 - __builtin_clz(size | 1)) {}
    void add(int i, int delta) { for (; i <= n; i += i & -i) bit[i] += delta; }
    int kth(int k) {                                 // smallest index with prefix >= k (1-indexed)
        int pos = 0;
        for (int step = 1 << log; step; step >>= 1)
            if (pos + step <= n && bit[pos + step] < k) { pos += step; k -= bit[pos]; }
        return pos + 1;
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, q;
    cin >> n >> q;
    Fenwick fenwick(n);
    for (int i = 1; i <= n; ++i) { int x; cin >> x; fenwick.add(i, x); }
    while (q--) { int k; cin >> k; cout << fenwick.kth(k) << '\n'; }
}
```

---

## 3. Pushing the Aggregate Down

Two-pass rebuilding lets a Fenwick tree propagate a value: collect the cells under each `i & -i`, then re-sum upward. That is the "range multiply then point read" trick some problems need.

---

## 4. `2 * i` Is Not the Structure

In a segment tree the children are `2 * i`; in a Fenwick tree they are implicit in the lowbit. Both sides of a Fenwick update/query start at exactly one `i` and walk, so skipping `i` itself in `i -= i & -i` is wrong.

---

## 5. Complexity Notes

- Point add and prefix: $O(\log n)$.
- `kth`: $O(\log V)$; `V` is the compressed range size, not the value range.
- Memory $O(V)$; publish `V` through compression so up to $10^9$ values still fit.
- For range min/max with negative values, use a segment tree: Fenwick's invertibility comes from subtraction.