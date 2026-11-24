# Binary Search Templates

Every binary search below carries an invariant. State it, keep it, and the loop terminates.

---

## 1. `lower_bound` / `upper_bound`

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
    sort(a.begin(), a.end());
    while (q--) {
        long long x;
        cin >> x;
        // First index with a[i] >= x, and first index with a[i] > x.
        cout << lower_bound(a.begin(), a.end(), x) - a.begin() << ' '
             << upper_bound(a.begin(), a.end(), x) - a.begin() << '\n';
    }
}
```

Occurrence count of $x$ is `upper_bound − lower_bound`.

---

## 2. `partition_point` for a Custom Predicate

Invariant: `[begin, lo)` satisfy `P`, `[hi, end)` do not.

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
    long long limit;
    cin >> limit;
    int count = partition_point(a.begin(), a.end(),
        [limit](long long x) { return x * x <= limit; }) - a.begin();
    cout << count << '\n';
}
```

Note `x * x` must stay inside `long long`; guard the input bound or use `__int128`.

---

## 3. Integer Binary Search with a Half-Open Range

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    long long n;
    cin >> n;
    // Largest b with b * b <= n. lo is known false, hi known true.
    long long lo = 0, hi = min(n, 1'000'000'000LL) + 1;
    while (hi - lo > 1) {
        long long mid = lo + (hi - lo) / 2;
        (mid * mid <= n ? lo : hi) = mid;
    }
    cout << lo << '\n';
}
```

Half-open `[lo, hi)` cannot overshoot `n` and needs no comparison after the loop.

---

## 4. The Three Classic Bugs

1. **Overflow in `(lo + hi) / 2`** — with `lo, hi` near `LLONG_MAX` it wraps. Use `lo + (hi - lo) / 2`.
2. **A non-monotone predicate** — e.g. `a[mid] == x` on an unsorted array. Sort first.
3. **Off-by-one in the update** — `lo = mid` (not `mid + 1`) whenever `mid` is still a candidate.

---

## 5. Complexity Notes

- $\Theta(\log n)$ comparisons; sorting first costs $O(n \log n)$ once.
- On `deque`, `std::lower_bound` still does only $\Theta(\log n)$ iterator steps but each step is cheap.
- On `std::set`, a `std::lower_bound` over the whole set is $O(n)$ — use `s.lower_bound(x)`.