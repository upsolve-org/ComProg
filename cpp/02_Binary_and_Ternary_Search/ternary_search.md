# Ternary Search on Integer and Real Domains

Ternary search shrinks an interval toward the optimum of a **unimodal** function. Two failure modes dominate: a function that is not actually unimodal over the whole domain, and integer truncation that makes two probes equal.

---

## 1. Unimodality, Precisely

A sequence is unimodal if it strictly increases up to one peak and strictly decreases afterwards. `[1, 3, 5, 4, 2]` qualifies; `[1, 3, 3, 4]` does not, because of the plateau. Always check the data before trusting the technique.

---

## 2. The Interval Skeleton

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

    int lo = 0, hi = n - 1;
    while (hi - lo > 3) {
        int third = (hi - lo) / 3;
        int m1 = lo + third, m2 = hi - third;
        if (a[m1] < a[m2]) lo = m1 + 1; else hi = m2 - 1;
    }
    long long best = LLONG_MIN;
    for (int i = lo; i <= hi; ++i) best = max(best, a[i]);
    cout << best << '\n';
}
```

The remaining tail of at most four elements is scanned linearly, so no probe needs to leave `[0, n - 1]`.

---

## 3. Why Truncation Is a Bug

With `m1 = lo + (hi - lo) / 3` and `m2 = hi - (hi - lo) / 3`, a short interval can produce `m1 == m2`. Then `a[m1] < a[m2]` is never true and the search drifts left, discarding the peak.

- Guard with `hi - lo > 3` (above) or clamp: `m1 = min(m1, hi - 1)`, `m2 = max(m2, m1 + 1)`.
- Never evaluate outside `[lo, hi]` without clamping; interpolation can step out of range.

---

## 4. Real-Valued Function

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    double lo, hi;
    cin >> lo >> hi;
    auto f = [](double x) { return -(x - 3.0) * (x - 3.0) + 5.0 * x; };
    for (int step = 0; step < 200; ++step) {
        double m1 = lo + (hi - lo) / 3, m2 = hi - (hi - lo) / 3;
        (f(m1) < f(m2) ? lo : hi) = m1 == m2 ? m2 : (f(m1) < f(m2) ? m1 : m2);
    }
    cout << fixed << setprecision(10) << f((lo + hi) / 2) << '\n';
}
```

A fixed 200 iterations shrinks the interval by $(2/3)^{200}$, far below double precision.

---

## 5. Alternatives

- Ternary search is $\Theta(\log n)$ evaluations with a large constant.
- On a unimodal integer array, binary search on the derivative `a[i] <= a[i + 1]` takes $\Theta(\log n)$ with fewer evaluations and no clamping.
- On a convex-integer problem, use the wqs / Aliens trick instead.