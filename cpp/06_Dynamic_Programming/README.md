---
tags:
  - cpp/dynamic-programming
---

[[Home|🏠 Dashboard]] ❯ **C++ Module 06: Dynamic Programming**

---

# C++ Module 06: Dynamic Programming

A DP is a state space plus a transition that reads only strictly smaller states. In C++ the state is an index into a `vector`, the transition is a loop, and the base cases are the entries you write before the loop. The hard part is the ordering; the implementation is mechanical once the ordering exists.

---

## 🎒 0/1 Knapsack

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, capacity;
    cin >> n >> capacity;
    vector<long long> best(capacity + 1, LLONG_MIN);
    best[0] = 0;
    for (int i = 0; i < n; ++i) {
        int weight;
        long long value;
        cin >> weight >> value;
        for (int c = capacity; c >= weight; --c)             // descending keeps items single-use
            if (best[c - weight] != LLONG_MIN) best[c] = max(best[c], best[c - weight] + value);
    }
    cout << *max_element(best.begin(), best.end()) << '\n';
}
```

The descending capacity loop is what makes it 0/1 instead of unbounded; ascending would reuse the item.

---

## 🧱 Grid Paths with Rolling Rows

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int h, w;
    cin >> h >> w;
    constexpr int MOD = 1'000'000'007;
    vector<int> row(w, 0);
    row[0] = 1;
    for (int r = 0; r < h; ++r) {
        string line;
        cin >> line;
        for (int c = 0; c < w; ++c) {
            if (line[c] == '#' || (r == 0 && c == 0)) continue;
            long long ways = 0;
            if (c > 0) ways += row[c - 1];
            if (r > 0) ways += row[c];
            row[c] = (int)(ways % MOD);
        }
        if (r == 0) row[0] = (row[0] % MOD);
    }
    cout << row[w - 1] << '\n';
}
```

Two rows suffice because the transition only reads the current and previous row.

---

## 📈 Longest Increasing Subsequence in $O(n \log n)$

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<long long> tails;                                 // tails[l]: smallest end of a length-l+1 run
    for (int i = 0; i < n; ++i) {
        long long x;
        cin >> x;
        auto it = lower_bound(tails.begin(), tails.end(), x);
        if (it == tails.end()) tails.push_back(x); else *it = x;
    }
    cout << tails.size() << '\n';
}
```

`tails` is sorted by construction, so `lower_bound` applies. It stores ends, not a real subsequence.

---

## 🌲 Tree DP Recursion

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
    vector<int> size(n, 1);
    function<void(int)> dfs = [&](int u) {
        for (int v : children[u]) { dfs(v); size[u] += size[v]; }
    };
    dfs(0);
    for (int s : size) cout << s << ' ';
    cout << '\n';
}
```

Recursion depth equals tree height; for a path of $2 \times 10^5$ nodes, run an explicit post-order instead.

---

## 🔢 Bitmask DP

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<int> cost(n);
    for (auto &x : cost) cin >> x;
    const int full = 1 << n;
    vector<long long> best(full, LLONG_MAX);
    best[0] = 0;
    for (int mask = 0; mask < full; ++mask) {
        if (best[mask] == LLONG_MAX) continue;
        for (int i = 0; i < n; ++i)
            if (!(mask & (1 << i)))
                best[mask | (1 << i)] = min(best[mask | (1 << i)], best[mask] + cost[i]);
    }
    cout << best[full - 1] << '\n';
}
```

`n ≤ 22` is the practical bitmask ceiling; `1 << n` fits in `int` up to $n = 30$.

---

## ⏱️ Complexity Notes

- Knapsack $O(n \cdot capacity)$ memory $O(capacity)$.
- Grid paths $O(hw)$ memory $O(w)$.
- LIS $O(n \log n)$; the naive $O(n^2)$ version is the correct warm-up.
- Bitmask DP $O(2^n \cdot n)$ memory $O(2^n)$.

---

## ✅ Checklist

- The state is the smallest sufficient summary (index, remaining capacity, mask).
- Every transition reads only smaller-indexed states.
- Descending loops for 0/1 items, ascending for unbounded.
- `long long` wherever sums of values accumulate; `int` offsets only for sizes.

---

## Included Source Files

- `01_knapsack_and_subsets.md`, `grid_and_paths_dp.md`, `lis_and_lcs.md`, `interval_and_range_dp.md`
- `tree_dp.md`, `bitmask_dp.md`