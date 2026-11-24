# Session Card: Common WA Causes

| Symptom | Usual cause | Fix |
|---|---|---|
| WA on the smallest tests | base case missing or wrong | write the `n = 1` case by hand |
| WA only on negative values | sentinel too small / `0` initialised min | `LLONG_MAX` or a real bound |
| WA only on ties | comparator not strict | `<`, then a second key |
| WA on the max constraint | 32-bit accumulator | `long long` |
| WA after many tests | state not cleared between tests | rebuild each structure per test |
| WA on "print any" | format mismatch | copy the required separators |
| RE on $n = 1$ | `v[1]` or `r - 1` on an empty range | bound the index |
| TLE only on the stress | wrong asymptotics, not constant | change the algorithm |

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int tests;
    cin >> tests;
    while (tests--) {
        int n;
        cin >> n;
        vector<long long> a(n);                       // rebuilt per test: no stale state
        for (auto &x : a) cin >> x;
        sort(a.begin(), a.end());
        cout << a.back() - a.front() << '\n';
    }
}
```

Reading the test count first and rebuilding inside the loop prevents cross-test contamination.