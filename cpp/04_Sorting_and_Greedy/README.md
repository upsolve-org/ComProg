---
tags:
  - cpp/sorting
  - cpp/greedy
---

[[Home|🏠 Dashboard]] ❯ **C++ Module 04: Sorting and Greedy Algorithms**

---

# C++ Module 04: Sorting and Greedy Algorithms

`std::sort` is introsort: quicksort with a median-of-three pivot, a heapsort fallback at $2\log_2 n$ depth, and insertion sort under 16 elements. It is $\Theta(n \log n)$ in the worst case and the right tool for ordering. Greedy then turns a sorted order into a local decision, and the proof that the local decision is globally right is the actual content.

---

## 🔑 Custom Comparators Are Not Strictly Less

A comparator must return `true` exactly when `a` must come **before** `b`. Returning `a.x <= b.x` is the classic crash.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<pair<int, string>> people(n);
    for (auto &[age, name] : people) cin >> age >> name;
    sort(people.begin(), people.end(), [](const auto &a, const auto &b) {
        if (a.first != b.first) return a.first > b.first;      // older first
        return a.second < b.second;                            // ties by name
    });
    for (const auto &[age, name] : people) cout << age << ' ' << name << '\n';
}
```

---

## 🧮 Stable Sort Keeps the Original Order

`std::stable_sort` preserves input order among equal keys, so you sort by the secondary key first and the primary key last.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<string> names(n);
    vector<int> heights(n);
    for (int i = 0; i < n; ++i) cin >> names[i] >> heights[i];
    vector<size_t> order(n);
    iota(order.begin(), order.end(), 0);
    stable_sort(order.begin(), order.end(),
        [&](size_t a, size_t b) { return heights[a] < heights[b]; });
    for (size_t i : order) cout << names[i] << '\n';
}
```

Below `-O2`, `std::sort` degrades beyond about 17 stable keys (equal groups become quadratic); use `stable_sort` when many keys tie.

---

## 🤝 Greedy by Earliest Finish

Select the most non-overlapping intervals: sort by end, take the first that starts at or after the last accepted end.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<pair<long long, long long>> events(n);
    for (auto &[end, start] : events) cin >> start >> end;      // stored (end, start)
    sort(events.begin(), events.end());
    long long last = LLONG_MIN;
    int taken = 0;
    for (auto [end, start] : events)
        if (start >= last) { last = end; ++taken; }
    cout << taken << '\n';
}
```

**Exchange argument.** Any optimal solution's first interval $e$ can be swapped for the earliest-finishing interval $g$ without losing feasibility, because $g$ ends no later. Induction repeats the swap.

---

## 📉 Exchange Argument Checklist

1. Name the greedy choice in one sentence.
2. Compare it with the first choice of an optimal solution.
3. Show the swap keeps the solution feasible and no shorter.
4. Show the cost is $O(n \log n)$ (usually the sort) and the answer fits `long long`.

---

## 🗜️ Coordinate Compression

Sort and `unique` before mapping values into an array index:

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
    vector<long long> values = a;
    sort(values.begin(), values.end());
    values.erase(unique(values.begin(), values.end()), values.end());
    for (long long x : a)
        cout << int(lower_bound(values.begin(), values.end(), x) - values.begin()) << ' ';
    cout << '\n';
}
```

---

## 🧹 Stable Partition, Not `remove_if` on a Live Container

`std::remove_if` returns the new logical end; the container still holds the moved-out tail.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    vector<int> v = {1, 2, 3, 4, 5, 6};
    v.erase(remove_if(v.begin(), v.end(), [](int x) { return x % 2 == 0; }), v.end());
    for (int x : v) cout << x << ' ';
    cout << '\n';
}
```

---

## ⏱️ Complexity Notes

- `std::sort` and `std::stable_sort` are $O(n \log n)$; both allocate nothing for `sort`.
- `std::nth_element` is $O(n)$ on average and enough when only the median is needed.
- Counting sort is $O(n + V)$ and wins when $V$ is small; radix sort is $O(n \cdot \text{digits})$.
- A comparator with a hidden `unordered_map` lookup multiplies the sort by the hash cost.

---

## ✅ Checklist

- Comparator is a strict `bool` of the form "before", never `<=`.
- `stable_sort` when ties must keep order.
- Greedy choice and its exchange argument are written down.
- Sorted-array `end` values use `long long` when times can exceed $2^{31}-1$.

---

## Included Source Files

- `sorting_and_custom_keys.md` — comparator patterns and compression.
- `greedy_templates.md` — exchange arguments worked through.