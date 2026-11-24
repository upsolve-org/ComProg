# Mo's Algorithm and Sqrt Decomposition

Mo's algorithm answers $q$ offline range queries by ordering them so both ends move as little as possible: sort by block of `l`, and reverse `r` on odd blocks. Total moves are $O((n + q) \sqrt n)$.

---

## 1. The Snake Order

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
        return bx % 2 ? x.r > y.r : x.r < y.r;
    });

    vector<int> freq(1'000'001, 0);
    vector<long long> answer(q);
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
    for (long long value : answer) cout << value << '\n';
}
```

`sqrt(q)` rather than `sqrt(n)` keeps the block size tied to the number of queries.

---

## 2. Mo with Updates

Chronological time becomes a third key: sort by `(l block, r block, time)`, then apply and roll back updates while walking. The bound turns into $O(n^{5/3})$.

```cpp
struct Update { int pos, value; };
// state: l, r, and the index of the last applied update; move time up/down with apply/rollback
```

---

## 3. Sqrt Decomposition of the Array

The non-offline cousin: store each block's sum, and a range sum touches whole blocks in $O(1)$ and partial blocks in $O(B)$ — $O(\sqrt n)$ per query.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, q;
    cin >> n >> q;
    int block = max(1, (int)sqrt(n));
    vector<long long> a(n), blockSum((n + block - 1) / block, 0);
    for (int i = 0; i < n; ++i) { cin >> a[i]; blockSum[i / block] += a[i]; }
    while (q--) {
        int l, r;
        cin >> l >> r;
        --l;
        long long sum = 0;
        for (; l < r && l % block; ++l) sum += a[l];        // partial head
        for (; r - l >= block; sum += blockSum[l / block], l += block);   // whole blocks
        for (; l < r; ++l) sum += a[l];                     // partial tail
        cout << sum << '\n';
    }
}
```

---

## 4. When Mo's Fails

- Online queries with updates interleaved need a segment tree with lazy propagation.
- Very large `n` and few queries: a Fenwick tree over sorted positions is cheaper.
- Only a maximum is asked: a sparse table.

---

## 5. Complexity Notes

- Mo's: $O((n + q) \sqrt n)$ moves; each move is one add or remove.
- `n / sqrt(q)` block: $q$ queries per block, $\sqrt q$ blocks.
- Sqrt array decomposition: $O(\sqrt n)$ per query, $O(1)$ per update.