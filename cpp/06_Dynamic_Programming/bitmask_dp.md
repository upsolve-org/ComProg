# Bitmask DP

Bitmask DP is the tool when $n \le 22$: the set of already-chosen items is the state, an integer mask. Every submask is visited once, and the answer is in the full mask. Above $n = 22$ the $2^n$ table stops fitting.

---

## 1. Assigning Items to Desks

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;                                                // n <= 20
    vector<vector<long long>> cost(n, vector<long long>(n));
    for (auto &row : cost) for (auto &x : row) cin >> x;

    const int full = 1 << n;
    vector<long long> best(full, LLONG_MAX);
    best[0] = 0;
    for (int mask = 0; mask < full; ++mask) {
        if (best[mask] == LLONG_MAX) continue;
        int worker = popcount((unsigned)mask);
        if (worker == n) continue;
        for (int job = 0; job < n; ++job)
            if (!(mask >> job & 1))
                best[mask | 1 << job] = min(best[mask | 1 << job], best[mask] + cost[worker][job]);
    }
    cout << best[full - 1] << '\n';
}
```

`popcount` from `<bits>` (C++20) counts the set bits, so the next worker is the popcount itself.

---

## 2. Enumerating Submasks

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int mask;
    cin >> mask;
    vector<int> sums(1 << 20, 0);
    for (int sub = mask; sub; sub = (sub - 1) & mask) sums[sub] = sub;
    for (auto value : {mask, 0}) sums[value] = value;
    cout << sums[mask & -mask] << '\n';
}
```

`sub = (sub - 1) & mask` visits every submask exactly once, descending. The total over all masks is $O(3^n)$.

---

## 3. Representatives of a Set

Least set bit and its index (C++20):

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    unsigned mask;
    cin >> mask;
    for (unsigned rest = mask; rest; rest &= rest - 1)
        cout << countr_zero(rest) << ' ';
    cout << '\n';
}
```

`rest &= rest - 1` clears the least set bit, so the loop runs once per set bit instead of once per bit.

---

## 4. Bitset Tables for Large $n$

When only reachability is needed, `std::bitset<1 << 22>` holds the whole table in $2^{22}$ bits (512 KB) instead of $32$ MB of `bool` padding.

---

## 5. Complexity Notes

- $O(2^n \cdot n)$ states and transitions; $O(2^n)$ memory.
- Submask enumeration over the full mask is $O(3^n)$ and is the limit around `n = 16`.
- `unsigned` masks avoid sign issues with `1 << 31`; use `unsigned long long` past 32 bits.