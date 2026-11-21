# Two Pointers Templates

## 1. Converging Pointers on Sorted Data

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    long long target;
    cin >> n >> target;
    vector<long long> a(n);
    for (auto &x : a) cin >> x;
    sort(a.begin(), a.end());
    int lo = 0, hi = n - 1;
    bool found = false;
    while (lo < hi) {
        long long sum = a[lo] + a[hi];
        if (sum == target) { found = true; break; }
        (sum < target ? lo : hi) += sum < target ? 1 : -1;
    }
    cout << (found ? "YES\n" : "NO\n");
}
```

**Invariant:** a valid pair, if any, has one index in `[lo, hi]`. Too small a sum means `lo` cannot pair with anything at or left of itself.

---

## 2. Opening Pointers (Fast/Slow)

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    long long limit;
    cin >> n >> limit;
    vector<long long> a(n);
    for (auto &x : a) cin >> x;
    long long run = 0;
    int best = 0, slow = 0;
    for (int fast = 0; fast < n; ++fast) {
        run += a[fast];
        while (run > limit) run -= a[slow++];
        best = max(best, fast - slow + 1);
    }
    cout << best << '\n';
}
```

**Invariant:** after the `while`, `[slow, fast]` is valid. `best` only reads a valid window.

---

## 3. Merge of Two Sorted Sequences

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;
    vector<long long> a(n), b(m), merged;
    for (auto &x : a) cin >> x;
    for (auto &x : b) cin >> x;
    merged.reserve(n + m);
    size_t i = 0, j = 0;
    while (i < a.size() && j < b.size())
        merged.push_back(a[i] <= b[j] ? a[i++] : b[j++]);
    merged.insert(merged.end(), a.begin() + i, a.end());
    merged.insert(merged.end(), b.begin() + j, b.end());
    for (size_t k = 0; k < merged.size(); ++k) cout << merged[k] << " \n"[k + 1 == merged.size()];
}
```

The leftover tail is copied wholesale — that is what keeps the merge linear.

---

## 4. When Two Pointers Fail

- The predicate is not monotone, e.g. "exactly $k$ distinct" with deletions plus a "keep larger" side constraint.
- Negative values with a "largest sum at least $S$" rule: prefix sums plus a multiset.
- Pair counting where each element can pair many times: sort, then binary search.

---

## 5. Large Input Safety

- Buffer output with `string` + `reserve`, not per-element `cout` under sync (see `fast_io_and_templates.md`).
- `int` indices are enough up to $2 \times 10^9$; use `long long` when the window length itself is a `long long`.
- `a[slow++]` must never follow a check that can fail for the last element; append a sentinel or bound the loop.