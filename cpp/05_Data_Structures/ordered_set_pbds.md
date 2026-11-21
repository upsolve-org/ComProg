# Ordered Set with Policy-Based Data Structures

`std::set` orders elements but cannot tell you a rank. GNU libstdc++ ships a balanced tree that can, through `__gnu_pbds::tree`. It is available on Codeforces' GNU compiler and costs one extra include.

---

## 1. The Type

```cpp
#include <bits/stdc++.h>
using namespace std;
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>
using namespace __gnu_pbds;

template <class T>
using ordered_set = tree<T, null_type, less<T>, rb_tree_tag, tree_order_statistics_node_update>;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    ordered_set<long long> values;
    for (int i = 0; i < n; ++i) { long long x; cin >> x; values.insert(x); }
    // Number of values strictly less than x:
    long long x;
    cin >> x;
    cout << values.order_of_key(x) << '\n';
    // k-th smallest (0-indexed):
    int k;
    cin >> k;
    cout << *values.find_by_order(k) << '\n';
}
```

`order_of_key(x)` counts keys `< x`; `find_by_order(k)` returns the iterator to the $k$-th key.

---

## 2. Duplicates

The tree is a set. To keep multiplicities pair the value with an index:

```cpp
#include <bits/stdc++.h>
using namespace std;
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>
using namespace __gnu_pbds;

template <class T>
using ordered_set = tree<T, null_type, less<T>, rb_tree_tag, tree_order_statistics_node_update>;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, counter = 0;
    cin >> n;
    ordered_set<pair<long long, int>> values;              // (value, insertion id)
    long long answer = 0;
    for (int i = 0, x; i < n; ++i) {
        cin >> x;
        answer += (long long)i - values.order_of_key({x, INT_MIN});
        values.insert({x, ++counter});
    }
    cout << answer << '\n';                                // inversions
}
```

`{x, INT_MIN}` counts every pair with value `< x` regardless of id.

---

## 3. Erase by Key

`erase` accepts a key or an iterator:

```cpp
values.erase({x, counter});      // exact key
values.erase(values.find({x, counter}));
```

---

## 4. Limitations

- Not available with libc++ (clang on macOS) — Codeforces uses GNU libstdc++.
- `find_by_order` is $O(\log n)$ but dereferencing is not `const`; store values not movable objects.
- Memory per node is the same as `std::set` plus the subtree counters.
- The alias must be declared before `main`; the node update type is `tree_order_statistics_node_update`.

---

## 5. Complexity Notes

- Insert, erase, order statistic: $O(\log n)$ all.
- The `tree` keeps exact ranks, so it beats a Fenwick tree when the value range is $10^{18}$ and compression is unnecessary.
- Compress to `vector` + Fenwick when a stable, portable build is needed.