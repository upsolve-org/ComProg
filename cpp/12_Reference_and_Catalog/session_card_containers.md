# Session Card: Containers

| Need | Container | Note |
|---|---|---|
| sequence | `vector<T>` | reserve when the size is known |
| double-ended | `deque<T>` | $O(1)$ at both ends |
| LIFO | `vector<T>` | fastest stack |
| FIFO | `queue<T>` | backed by `deque` |
| priority | `priority_queue` | `greater<>` for a min-heap |
| ordered keys | `set`/`map` | member `lower_bound`, never `std::lower_bound` |
| order statistics | PBDS `tree` | `order_of_key`, `find_by_order` |
| keyed access | `unordered_map` | splitmix64 hash |
| fixed flags | `bitset<N>` | one instruction per word |

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    priority_queue<int, vector<int>, greater<int>> small;   // min-heap
    small.push(4);
    small.push(1);
    cout << small.top() << '\n';                            // 1
}
```

- `vector<bool>` is bit-packed; `v[i]` returns a proxy, so `auto x = v[i]` copies a `bool`.
- `deque` is the right home for a monotonic window.
- `map` has no `push_back`; use `insert`/`emplace`/`operator[]`.