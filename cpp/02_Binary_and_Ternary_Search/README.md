---
tags:
  - cpp/binary-search
---

[[Home|🏠 Dashboard]] ❯ **C++ Module 02: Binary and Ternary Search**

---

# C++ Module 02: Binary and Ternary Search

Binary search finds the boundary where a predicate flips true. Modern C++ has the halves built in — `std::partition_point`, `std::lower_bound` — so the interesting work moves to writing a predicate that is monotone, and choosing an interval that cannot overflow.

---

## 🎯 Partition Point Instead of Hand-Written Bounds

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
    int lo, hi;
    cin >> lo >> hi;
    // Elements are already sorted. Count values in [lo, hi] with two partition points.
    auto left = partition_point(a.begin(), a.end(), [lo](long long x) { return x < lo; });
    auto right = partition_point(a.begin(), a.end(), [hi](long long x) { return x <= hi; });
    cout << (right - left) << '\n';
}
```

`partition_point` returns the first element for which the predicate is false. Predicate `x < lo` is true on a prefix, so the returned iterator is the lower bound.

---

## 🔁 Binary Search on the Answer

When the answer is an integer in a known range and the check is monotone, search the range itself.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    long long cap, n;
    cin >> cap >> n;
    vector<long long> load(n);
    for (auto &x : load) cin >> x;

    auto feasible = [&](long long limit) {
        long long used = 0, machines = 1;
        for (long long l : load) {
            if (l > limit) return false;
            if (used + l > limit) { ++machines; used = 0; }
            used += l;
        }
        return machines <= cap;
    };

    long long lo = 0, hi = 0;                     // [lo, hi) with lo infeasible
    for (long long l : load) hi += l;             // the whole sum always works
    ++hi;
    while (hi - lo > 1) {
        long long mid = lo + (hi - lo) / 2;       // never lo + (hi - lo) that overflows
        (feasible(mid) ? hi : lo) = mid;
    }
    cout << hi << '\n';
}
```

`(feasible(mid) ? hi : lo) = mid;` is the compact way to keep both branches identical.

---

## 📐 Floating-Point Bisection

Fixed iteration counts beat `while (hi - lo > 1e-9)` because they cannot loop forever on denormals.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    double c;
    cin >> c;
    double lo = 0, hi = max(1.0, c);
    for (int step = 0; step < 100; ++step) {
        double mid = (lo + hi) / 2;
        (mid * mid >= c ? hi : lo) = mid;
    }
    cout << fixed << setprecision(9) << hi << '\n';
}
```

---

## 🏔️ Ternary Search on a Unimodal Function

Ternary search needs a strict unimodal shape on the interval. If that is only true on $[1, n]$, clamp the evaluated points:

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
    auto f = [&](long long i) { return -(long long)(i - 3) * (i - 3) + 5 * i; };

    int lo = 0, hi = n - 1;
    while (hi - lo > 2) {
        int m1 = lo + (hi - lo) / 3;
        int m2 = hi - (hi - lo) / 3;
        if (f(m1) < f(m2)) lo = m1 + 1; else hi = m2 - 1;
    }
    long long best = LLONG_MIN;
    for (int i = lo; i <= hi; ++i) best = max(best, f(min<long long>(i, n - 1)));
    cout << best << '\n';
}
```

---

## ⏱️ Complexity Notes

- Binary search is $\Theta(\log n)$ comparisons; each comparison is an integer or floating point operation.
- `std::set::lower_bound` is $O(\log n)$; `std::distance` on its result is $O(n)$.
- Ternary search evaluates the function $\Theta(\log_{1.5} n)$ times and then scans a small tail — keep the function cheap.
- A wrong monotonicity silently returns a plausible index; always stress the predicate.

---

## ✅ Checklist

- `mid = lo + (hi - lo) / 2`, never `(lo + hi) / 2` in 32-bit.
- Range is `[lo, hi)` with an invariant you can state aloud.
- `partition_point` and `lower_bound` are used on sorted ranges only.
- The final ternary search scan is bounded by the clamped indices.

---

## Included Source Files

- `binary_search_templates.md` — the search skeletons and their invariants.
- `ternary_search.md` — unimodality, clamping, and integer-trilogy bounds.