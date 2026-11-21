# Prefix Sums and Difference Arrays

Both techniques trade one $\Theta(n)$ precomputation for a family of $\Theta(1)$ range operations. They are the first tools of every fast solution and the backbone of later problems such as 2D counting and range add with a sum query.

---

## 1. Prefix Sums with 1-Based Indexing

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, q;
    cin >> n >> q;
    vector<long long> pre(n + 1, 0);
    for (int i = 1, x; i <= n; ++i) { cin >> x; pre[i] = pre[i - 1] + x; }
    while (q--) {
        int l, r;
        cin >> l >> r;
        cout << pre[r] - pre[l - 1] << '\n';
    }
}
```

Why 1-based: `pre[l - 1]` stays valid for $l = 1$ instead of needing a branch.

**Pitfall.** `pre` must be `long long`; with $2 \times 10^5$ values of $10^9$ the largest prefix is $2 \times 10^{14}$.

---

## 2. Difference Arrays for Range Addition

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;
    vector<long long> diff(n + 2, 0);
    for (int i = 0; i < m; ++i) {
        int l, r;
        long long v;
        cin >> l >> r >> v;
        diff[l] += v;
        diff[r + 1] -= v;                       // r + 1 is why the vector is n + 2 long
    }
    long long run = 0;
    for (int i = 1; i <= n; ++i) {
        run += diff[i];
        cout << run << " \n"[i == n];
    }
}
```

---

## 3. Prefix Minimum and XOR

The same scan works for any associative operator.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<long long> preMin(n + 1), preXor(n + 1);
    preMin[0] = LLONG_MAX;
    for (int i = 1, x; i <= n; ++i) {
        cin >> x;
        preMin[i] = min(preMin[i - 1], (long long)x);
        preXor[i] = preXor[i - 1] ^ x;
    }
    int l, r;
    cin >> l >> r;
    cout << preMin[r] << ' ' << (preXor[r] ^ preXor[l - 1]) << '\n';
}
```

XOR needs an **inverse**: `preXor[r] ^ preXor[l - 1]` cancels the outer part, which is why it works and `min` does not.

---

## 4. 2D Prefix Sums

Inclusion–exclusion on rectangles:

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int h, w;
    cin >> h >> w;
    vector<vector<long long>> pre(h + 1, vector<long long>(w + 1, 0));
    for (int r = 1; r <= h; ++r)
        for (int c = 1; c <= w; ++c) {
            long long x;
            cin >> x;
            pre[r][c] = x + pre[r - 1][c] + pre[r][c - 1] - pre[r - 1][c - 1];
        }
    int r1, c1, r2, c2;
    cin >> r1 >> c1 >> r2 >> c2;
    cout << pre[r2][c2] - pre[r1 - 1][c2] - pre[r2][c1 - 1] + pre[r1 - 1][c1 - 1] << '\n';
}
```

The corners of the query rectangle must be normalised so `r1 ≤ r2` and `c1 ≤ c2`.

---

## 5. Complexity Notes

- Prefix build $\Theta(n)$, query $\Theta(1)$, memory $\Theta(n)$.
- Difference updates $\Theta(1)$ each, final reconstruction $\Theta(n)$.
- 2D prefix: build $\Theta(hw)$, query $\Theta(1)$, memory $\Theta(hw)$.
- Where the values can be negative, prefix maximum needs a monotone variant (segment tree) because it is not invertible.