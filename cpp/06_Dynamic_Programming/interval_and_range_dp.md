# Interval and Range DP

Interval DP builds answers on short segments first, then combines them into longer ones. The order is by **length**, never by index, because a state $(l, r)$ reads $(l, k)$ and $(k + 1, r)$, which are strictly shorter.

---

## 1. Matrix Chain Order

Minimum scalar multiplications to multiply a chain:

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<long long> dim(n + 1);
    for (auto &x : dim) cin >> x;
    vector<vector<long long>> best(n, vector<long long>(n, 0));
    for (int length = 2; length <= n; ++length)
        for (int l = 0; l + length <= n; ++l) {
            int r = l + length - 1;
            best[l][r] = LLONG_MAX;
            for (int k = l; k < r; ++k)
                best[l][r] = min(best[l][r],
                    best[l][k] + best[k + 1][r] + dim[l] * dim[k + 1] * dim[r + 1]);
        }
    cout << best[0][n - 1] << '\n';
}
```

Dimensions reach $10^9$ in some versions; all three factors are `long long` and the cost table too.

---

## 2. Palindrome Removal

Remove a whole block when the ends match, otherwise splice:

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<int> a(n);
    for (auto &x : a) cin >> x;
    vector<vector<int>> best(n, vector<int>(n));
    for (int i = 0; i < n; ++i) best[i][i] = 1;
    for (int length = 2; length <= n; ++length)
        for (int l = 0; l + length <= n; ++l) {
            int r = l + length - 1;
            best[l][r] = a[l] == a[r] ? best[l + 1][r - 1] : 1 + best[l + 1][r];
            for (int k = l; k < r; ++k) best[l][r] = min(best[l][r], best[l][k] + best[k + 1][r]);
        }
    cout << best[0][n - 1] << '\n';
}
```

---

## 3. Memory Reduction

`best[l][r]` needs no row of more than `n` cells only if the transition never jumps two lengths back. Here it does, so keep the full table; above $5000$ intervals the table exceeds memory and a different formulation is needed.

---

## 4. Common Bugs

- Iterating `l` ascending inside `r`: reads an uncomputed shorter state. Iterate by length.
- Forgetting `best[i][i] = 1` (or `0` for costs); the state then reads garbage.
- Mixing inclusive and exclusive `r` between the loop and the transition.

---

## 5. Complexity Notes

- $O(n^3)$ time, $O(n^2)$ memory.
- Knuth optimisation drops specific problems to $O(n^2)$ when the transition is monotone in the split point.
- Choice of an `int` table is safe only when the answer counts blocks, not sums.