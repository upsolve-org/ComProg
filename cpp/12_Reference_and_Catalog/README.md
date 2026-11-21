---
tags:
  - cpp/reference
---

[[Home|🏠 Dashboard]] ❯ **C++ Module 12: Reference Library**

---

# C++ Module 12: Reference Library

This module is the lookup table: the catalog's topic map, the C++20 facilities worth memorising, and the complexity of every structure in the course. Skim it before a contest; you will not read it during one.

---

## 📚 Catalog Topic Map

- General advice: [How to read problems](https://codeforces.com/blog/entry/62730), [finding observations](https://codeforces.com/blog/entry/99291)
- Data structures: [DSU](https://codeforces.com/blog/entry/75428), [segment tree](https://codeforces.com/blog/entry/78762), [PBDS](https://codeforces.com/blog/entry/11080)
- Graphs: [Dijkstra](https://codeforces.com/blog/entry/3607), [bridges](https://codeforces.com/blog/entry/71146)
- Strings: [KMP](https://codeforces.com/blog/entry/12209), [Z-algorithm](https://codeforces.com/blog/entry/3107)

---

## 🧰 Standard Facilities Worth Knowing Cold

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    vector<int> v{3, 1, 4, 1, 5};
    ranges::sort(v);                                 // in-place, no begin/end pair
    cout << ranges::count(v, 1) << '\n';
    cout << *ranges::lower_bound(v, 4) << '\n';      // 4
    cout << accumulate(v.begin(), v.end(), 0) << '\n';
    cout << max_element(v.begin(), v.end()) - v.begin() << '\n';
    cout << popcount(13u) << ' ' << bit_width(13u) << '\n';
}
```

| Need | Call |
|---|---|
| binary search | `lower_bound`, `upper_bound`, `partition_point` |
| heap | `priority_queue<T, vector<T>, greater<>>` for min |
| order statistics | PBDS `tree` + `tree_order_statistics_node_update` |
| hashing | `unordered_map<K, V, SplitMix64>` |
| bit counts | `popcount`, `countr_zero`, `bit_ceil` |

---

## 📊 Complexity Reference

| Structure | Insert | Query | Memory |
|---|---|---|---|
| `vector` push | amortised $O(1)$ | index $O(1)$ | $O(n)$ |
| `set`/`map` | $O(\log n)$ | $O(\log n)$ | $O(n)$ |
| PBDS `tree` | $O(\log n)$ | rank $O(\log n)$ | $O(n)$ |
| Fenwick | $O(\log n)$ | prefix $O(\log n)$ | $O(n)$ |
| Segment tree | $O(\log n)$ | range $O(\log n)$ | $O(n)$ |
| DSU | $O(\alpha(n))$ | find $O(\alpha(n))$ | $O(n)$ |
| `unordered_map` | $O(1)$ expected | $O(1)$ expected | $O(n)$ |

Expected `unordered_map` bounds are only safe with a mixed hash.

---

## 🚩 UB Checklist

- Signed overflow: `int x = 2e9; x * 2` is UB, not a wraparound.
- Out-of-bounds `v[i]` and `s[i]` in release builds are unchecked.
- Shifts by 64 on a 64-bit type.
- Reading an uninitialised variable.
- Dereferencing `end()` from `find`, `lower_bound`, or an empty container.
- Comparing iterators from different containers.

---

## 🧪 Local Verification Commands

```sh
g++ -std=gnu++20 -O2 -Wall -Wextra main.cpp -o main
g++ -std=gnu++20 -O1 -g -fsanitize=address,undefined main.cpp -o main_san
g++ -std=gnu++20 -O2 -D_GLIBCXX_DEBUG main.cpp -o main_debug
```

Run `main_san` and `main_debug` against the samples and a stress generator before the fast `main`.

---

## ✅ Pre-Submission List

- Constraints re-read and cost fits.
- `long long` on every accumulator.
- Arrays over-sized by at least 2.
- Sample and stress pass on sanitised builds.
- Output format matches exactly (counts, one per line, no trailing text).

---

## Included Source Files

- `codeforces_catalog_full.md` — the full archived catalog index.

---

## 🗂️ Session Cards

Every structure above has a one-page card in this module's folder, kept short on purpose so it can be re-read in the fifteen minutes before a round:

- `session_card_io.md`, `session_card_containers.md`, `session_card_algorithms.md`
- `session_card_numbers.md`, `session_card_output.md`, `session_card_test_cases.md`
- `session_card_debugging.md`, `session_card_wa_causes.md`, `session_card_stress.md`
- `session_card_recursion.md`, `session_card_fast_hash.md`, `codeforces_catalog_full.md`