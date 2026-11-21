# Session Card: Algorithms

| Need | Call |
|---|---|
| sort | `std::sort` / `ranges::sort` (strict comparator) |
| stable order | `std::stable_sort` |
| k-th element | `std::nth_element` |
| binary search | `lower_bound`, `upper_bound`, `partition_point` |
| heap | `push_heap` / `pop_heap` on a `vector` |
| permutation | `next_permutation` |
| gcd | `std::gcd` from `<numeric>` |
| bit counts | `popcount`, `countr_zero` from `<bit>` |
| fold | `accumulate` (use `0LL` as the start) |

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    vector<int> v{1, 2, 3};
    do { for (int x : v) cout << x << ' '; cout << '\n'; } while (next_permutation(v.begin(), v.end()));
    cout << accumulate(v.begin(), v.end(), 0LL) << '\n';
}
```

- A comparator returns "a comes strictly before b"; `<=` is wrong.
- `accumulate`'s third argument sets the type: `0` accumulates in `int`.
- `next_permutation` starts from a sorted range.
- `ranges::` versions take the range, not a begin/end pair.