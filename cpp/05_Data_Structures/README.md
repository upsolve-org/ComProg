---
tags:
  - cpp/data-structures
---

[[Home|🏠 Dashboard]] ❯ **C++ Module 05: Data Structures**

---

# C++ Module 05: Data Structures

C++20 puts nearly every useful container in the standard library. The skill is choosing one whose **worst case** fits the limit, then using its member functions rather than generic algorithms. `std::set` and `std::map` are red-black trees; the Fenwick and segment trees you write yourself are the tool for aggregate queries on arrays.

---

## 🧵 Disjoint Set Union

Two arrays, path halving, union by size. `alpha(n)` per operation.

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
        while (parent[x] != x) x = parent[x] = parent[parent[x]];
        return x;
    }
    bool unite(int a, int b) {
        a = find(a), b = find(b);
        if (a == b) return false;
        if (size[a] < size[b]) swap(a, b);
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
        int a, b;
        cin >> a >> b;
        dsu.unite(a - 1, b - 1);
        cout << dsu.components << '\n';
    }
}
```

---

## 🌳 Fenwick Tree for Prefix Sums

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
        int l, r;
        cin >> l >> r;
        cout << prefix(r) - prefix(l - 1) << '\n';
    }
}
```

---

## 🌲 Segment tree with `std::function`-free templates

Store the aggregate on an iterative tree; much faster than recursion.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, q;
    cin >> n >> q;
    size_t base = 1;
    while (base < (size_t)n) base <<= 1;
    vector<long long> tree(2 * base, 0);
    for (int i = 0; i < n; ++i) cin >> tree[base + i];
    for (size_t i = base; i-- > 1;) tree[i] = tree[2 * i] + tree[2 * i + 1];
    auto update = [&](int pos, long long value) {
        for (size_t i = base + pos; i > 0; i >>= 1) tree[i] += value;
    };
    while (q--) {
        int pos;
        long long value;
        cin >> pos >> value;
        update(pos - 1, value);
        cout << tree[1] << '\n';
    }
}
```

---

## 🔀 Ordered Map and the Emplace Rule

`map`/`set` have no `push_back`; the insertion members are `insert`/`emplace`, and there is no reallocation because nodes are separate.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, q;
    cin >> n >> q;
    map<string, long long> balance;
    while (q--) {
        string name;
        long long delta;
        cin >> name >> delta;
        balance[name] += delta;                    // default-constructs 0 on first use
        if (balance[name] == 0) balance.erase(name);
    }
    for (const auto &[name, value] : balance) cout << name << ' ' << value << '\n';
    (void)n;
}
```

---

## 🚏 Monotonic Stack

Next strictly greater element in one pass:

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<long long> a(n), answer(n, -1);
    for (auto &x : a) cin >> x;
    vector<int> stack;
    for (int i = n; i-- > 0;) {
        while (!stack.empty() && a[stack.back()] <= a[i]) stack.pop_back();
        if (!stack.empty()) answer[i] = stack.back();
        stack.push_back(i);
    }
    for (int x : answer) cout << x + 1 << ' ';
    cout << '\n';
}
```

Use a sentinel instead of duplicating the condition; the stack never holds a value smaller than the current one.

---

## ⏱️ Complexity Notes

- DSU with path halving plus union by size: $O(\alpha(n))$ amortised.
- Fenwick: $O(\log n)$ update and prefix; memory $O(n)$.
- Segment tree: $O(\log n)$ update and range query; the iterative form recurses nowhere.
- `set`/`map` sorting is $O(\log n)$ per change; PBDS `tree` adds `order_of_key` at the same cost.

---

## ✅ Checklist

- Container choice matches the bound a worst case is needed for.
- `s.lower_bound(x)` on ordered containers, never `std::lower_bound` over them.
- No iterator kept across an `erase`.
- Recursive segment touches use the `2 * i` / `2 * i + 1` child convention only on power-of-two bases.

---

## Included Source Files

- `dsu_disjoint_set_union.md`, `fenwick_tree.md`, `segment_tree.md` — the three core structures.
- `monotonic_stack_and_queue.md`, `ordered_set_pbds.md` — order statistics and neighbors.