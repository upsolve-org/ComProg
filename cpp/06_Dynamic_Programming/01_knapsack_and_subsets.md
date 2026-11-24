# 0/1 Knapsack and Subset Sum

Both problems ask for a subset with a constraint. The state is either the best value at a capacity or simply "is this sum achievable", and both compressions rely on iterating capacity **downward** so an item is used once.

---

## 1. Maximum Value Knapsack

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
        for (int c = capacity; c >= weight; --c) {
            if (best[c - weight] == LLONG_MIN) continue;      // unreachable state
            best[c] = max(best[c], best[c - weight] + value);
        }
    }
    cout << *max_element(best.begin(), best.end()) << '\n';
}
```

`LLONG_MIN` is the "impossible" marker; the loop guard is `c >= weight` so `c - weight` is never negative.

---

## 2. Reachable Sums with `bitset`

When values are non-negative and the question is only *which* sums are reachable, a bitset shifts in one instruction per item.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, target;
    cin >> n >> target;
    bitset<200'001> reachable;
    reachable[0] = 1;
    for (int i = 0, x; i < n; ++i) {
        cin >> x;
        reachable |= reachable << x;                          // "or" keeps both skipping and taking
    }
    cout << reachable[target] << '\n';
}
```

The shift moves every reachable sum up by `x`; the `|=` preserves the original set, which is exactly the skip branch.

---

## 3. Counting Partitions

Number of subsets with sum $S$, modulo $10^9+7$:

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, target;
    cin >> n >> target;
    constexpr int MOD = 1'000'000'007;
    vector<int> ways(target + 1, 0);
    ways[0] = 1;
    for (int i = 0, x; i < n; ++i) {
        cin >> x;
        for (int c = target; c >= x; --c) ways[c] = (ways[c] + ways[c - x]) % MOD;
    }
    cout << ways[target] << '\n';
}
```

---

## 4. $O(n \cdot \text{sum})$ vs Meet-in-the-Middle

- Knapsack's bound is $O(n \cdot \text{capacity})$; it dies once capacity exceeds $\sim 10^7$.
- With $n \le 40$ and huge values, split into halves, enumerate all $2^{20}$ subset sums of each, sort one, and binary search. That is $O(2^{n/2} \log 2^{n/2})$.
- With $n \le 20$, a plain enumerate over $2^n$ masks is smaller than the table.

---

## 5. Complexity Notes

- Time $O(n \cdot C)$, memory $O(C)$ in the 1D form.
- The `bitset` trick is $O(n \cdot C / 64)$ by words.
- Validity of the marker relies on "skip" staying in the set; a value of 0 still shifts by 0, which merges into the same positions.