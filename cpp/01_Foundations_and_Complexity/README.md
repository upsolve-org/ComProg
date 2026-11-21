---
tags:
  - cpp/foundations
  - cpp/complexity
---

[[Home|🏠 Dashboard]] ❯ **C++ Module 01: Foundations & Complexity**

---

# C++ Module 01: Foundations & Complexity

Two skills gate everything after this point: estimating cost before writing code, and building array primitives that run in linear time. C++ makes both measurable — `std::chrono` times your loops, and the STL gives you the right primitives to do the work once.

---

## ⏱️ Budgets in C++20

A modern judging machine runs roughly $10^8$ to $10^9$ simple operations per second. A 2 s limit therefore tolerates $O(n \log n)$ for $n = 2 \times 10^5$ with plenty of slack, but not $O(n^2)$ past a few thousand.

| Bound | Comfortable | Borderline | Too slow |
|---|---|---|---|
| $n = 2 \times 10^5$ | $O(n \log n)$ | $O(n \sqrt n)$ | $O(n^2)$ |
| $n = 10^4$ | $O(n^2)$ | $O(n^2 \log n)$ | $O(n^3)$ |
| $n = 500$ | $O(n^3)$ | $O(n^3 \log n)$ | $O(2^n)$ |

Measure instead of guessing when the answer is close:

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    const int n = 2'000'000;
    vector<int> a(n, 1);
    auto start = chrono::steady_clock::now();
    long long sum = accumulate(a.begin(), a.end(), 0LL);
    auto elapsed = chrono::duration<double>(chrono::steady_clock::now() - start).count();
    cout << sum << " in " << elapsed * 1000 << " ms\n";
}
```

Digit separators (`2'000'000`) keep large bound constants readable.

---

## ➕ Prefix Sums

`pre[i]` holds the sum of the first $i$ elements, so a range sum is one subtraction.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, q;
    cin >> n >> q;
    vector<long long> pre(n + 1);
    for (int i = 1, x; i <= n; ++i) { cin >> x; pre[i] = pre[i - 1] + x; }
    while (q--) {
        int l, r;
        cin >> l >> r;                       // inclusive, 1-indexed
        cout << pre[r] - pre[l - 1] << '\n';
    }
}
```

Build is $\Theta(n)$, each query $\Theta(1)$. The accumulator is `long long` because the sums leave 32 bits.

---

## ⚡ Difference Arrays

A difference array turns "add $v$ to a range" into two point updates and a final prefix pass.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;
    vector<long long> diff(n + 2);
    for (int i = 0; i < m; ++i) {
        int l, r, v;
        cin >> l >> r >> v;
        diff[l] += v;
        diff[r + 1] -= v;
    }
    long long run = 0;
    for (int i = 1; i <= n; ++i) {
        run += diff[i];
        cout << run << " \n"[i == n];
    }
}
```

---

## 🧠 2D Prefix Sums

Rectangular queries use inclusion–exclusion on a 2D prefix table.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int h, w;
    cin >> h >> w;
    vector<vector<long long>> pre(h + 1, vector<long long>(w + 1));
    for (int r = 1; r <= h; ++r)
        for (int c = 1; c <= w; ++c) {
            long long x;
            cin >> x;
            pre[r][c] = x + pre[r - 1][c] + pre[r][c - 1] - pre[r - 1][c - 1];
        }
    int q;
    cin >> q;
    while (q--) {
        int r1, c1, r2, c2;
        cin >> r1 >> c1 >> r2 >> c2;
        cout << pre[r2][c2] - pre[r1 - 1][c2] - pre[r2][c1 - 1] + pre[r1 - 1][c1 - 1] << '\n';
    }
}
```

---

## 🧩 Bitset Primitives

`std::bitset` fits 64 flags into one machine word; `popcount` counts them.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    bitset<200'000> reachable;
    reachable[0] = 1;
    reachable <<= 5;                          // shift every flag five positions
    cout << reachable.count() << '\n';
}
```

One bitset shift over 200,000 flags is a handful of word operations, far cheaper than a loop.

---

## ⏱️ Complexity Notes

- Prefix build $\Theta(n)$; each range query $\Theta(1)$; memory $\Theta(n)$.
- Difference update $\Theta(1)$; the final reconstruction is $\Theta(n)$.
- 2D prefix $\Theta(hw)$; each rectangle query $\Theta(1)$.
- Fusion matters: a prefix sum inside a loop over $n$ is $O(n^2)$ overall, not $O(n)$.

---

## ✅ Checklist

- Every prefix or difference accumulator is `long long`.
- Arrays are sized `n + 2` when a `r + 1` index is written.
- The approach cost, not its constant, fits the published bound.
- One timing run before submitting when the plan is near the limit.

---

## Included Source Files

- `fast_io_and_templates.md` — the submission skeleton and its cost rules.
- `prefix_sums_and_diff_arrays.md` — full worked implementations.