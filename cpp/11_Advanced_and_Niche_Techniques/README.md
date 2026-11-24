---
tags:
  - cpp/advanced
---

[[Home|🏠 Dashboard]] ❯ **C++ Module 11: Advanced and Niche Techniques**

---

# C++ Module 11: Advanced and Niche Techniques

Three techniques that solve otherwise-hard problems and one that only needs a proof. Constructive algorithms build an object satisfying stated properties, Mo's algorithm answers offline range queries in $O((n + q)\sqrt n)$, and Nim reduces to an XOR.

---

## 🧱 A Constructive Parity Split

Split $n$ numbers into two groups of equal size with at least one odd number in the first.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<long long> a(n);
    for (auto &x : a) cin >> x;
    ranges::sort(a);
    // Pairs the sorted values, sends the larger of each pair to group B.
    vector<long long> groupA, groupB;
    for (int i = 0; i < n; i += 2) {
        groupA.push_back(a[i]);
        if (i + 1 < n) groupB.push_back(a[i + 1]);
    }
    if (n % 2) groupB.push_back(groupA.back()), groupA.pop_back();
    for (long long x : groupA) cout << x << ' ';
    cout << '\n';
    for (long long x : groupB) cout << x << ' ';
    cout << '\n';
}
```

`std::ranges::sort` sorts `<` in place; with duplicates the sorted pairs also differ by at most one value, which the caller validates.

---

## 🌀 Mo's Algorithm

Offline queries on a static array: sort them by block of `l` (odd blocks reversed), then move both ends and maintain the aggregate.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, q;
    cin >> n >> q;
    vector<long long> a(n);
    for (auto &x : a) cin >> x;
    struct Query { int l, r, id; };
    vector<Query> queries(q);
    for (int i = 0; i < q; ++i) { cin >> queries[i].l >> queries[i].r; --queries[i].l; queries[i].id = i; }
    int block = max(1, (int)(n / sqrt(q)));
    sort(queries.begin(), queries.end(), [block](const Query &x, const Query &y) {
        int bx = x.l / block, by = y.l / block;
        if (bx != by) return bx < by;
        return bx % 2 ? x.r > y.r : x.r < y.r;           // snake order keeps r moving forward
    });
    vector<long long> answer(q);
    vector<int> freq(1'000'001, 0);
    long long distinct = 0;
    int l = 0, r = -1;
    auto add = [&](int i) { if (freq[a[i]]++ == 0) ++distinct; };
    auto remove = [&](int i) { if (--freq[a[i]] == 0) --distinct; };
    for (const auto &query : queries) {
        while (l > query.l) add(--l);
        while (r < query.r) add(++r);
        while (l < query.l) remove(l++);
        while (r > query.r) remove(r--);
        answer[query.id] = distinct;
    }
    for (long long x : answer) cout << x << '\n';
}
```

---

## 🎲 Nim: XOR of Pile Sizes

First player wins exactly when the XOR is non-zero.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    long long xorSum = 0;
    for (int i = 0, x; i < n; ++i) { cin >> x; xorSum ^= x; }
    cout << (xorSum ? "First" : "Second") << '\n';
}
```

---

## 🧮 Coordinate Compression Helper

```cpp
vector<int> compress(vector<long long> values) {
    vector<long long> sorted = values;
    ranges::sort(sorted);
    sorted.erase(unique(sorted.begin(), sorted.end()), sorted.end());
    vector<int> result(values.size());
    for (size_t i = 0; i < values.size(); ++i)
        result[i] = int(lower_bound(sorted.begin(), sorted.end(), values[i]) - sorted.begin());
    return result;
}
```

---

## ⏱️ Complexity Notes

- Constructive solutions: usually $O(n \log n)$ from the sort; the proof of the invariant is the deliverable.
- Mo's: $O((n + q) \sqrt n)$ moves; `q` per block and a block of `n / sqrt(q)` size.
- Nim: $O(n)$; the proof is the mirror strategy (any non-zero XOR can be zeroed by one pile).
- Screw sorting the queries: without the snake order the right end resets per block and doubles the moves.

---

## ✅ Checklist

- Constructive: every stated property checked on your own output before printing.
- Mo's: the aggregate has an easy $O(1)$ add that is exactly reversible on remove.
- Nim: zero piles are allowed and change nothing.
- Value range small enough for a plain frequency array; otherwise compress first.

---

## Included Source Files

- `constructive_algorithms.md`, `mo_algorithm_and_sqrt_decomp.md`, `game_theory_nim.md`