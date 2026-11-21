# Sorting and Custom Keys

## 1. The Strict Weak Ordering Rule

Given comparator `cmp`:

- `cmp(a, a)` must be `false`.
- `cmp(a, b)` and `cmp(b, a)` cannot both be `true`.
- `cmp(a, b)` and `cmp(b, c)` imply `cmp(a, c)`.

`<=` breaks rule 1 and can read past the end, producing garbage or a crash.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct Player {
    int rating;
    string name;
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<Player> players(n);
    for (auto &p : players) cin >> p.rating >> p.name;
    sort(players.begin(), players.end(), [](const Player &a, const Player &b) {
        if (a.rating != b.rating) return a.rating > b.rating;   // strict: >
        return a.name < b.name;
    });
    for (const auto &p : players) cout << p.rating << ' ' << p.name << '\n';
}
```

---

## 2. A Comparator Needs a Locale or Global State

`sort` with a lambda capturing by reference is fine; capturing by value copies the whole array per call.

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
    auto byAbs = [](long long x, long long y) {                 // stateless, no capture
        return make_pair(llabs(x), x) < make_pair(llabs(y), y);
    };
    sort(a.begin(), a.end(), byAbs);
    for (long long x : a) cout << x << ' ';
    cout << '\n';
}
```

`std::pair` already has a lexicographic `operator<`, which is the shortest correct comparator for two keys.

---

## 3. Stable Sort and Order of Keys

With `std::stable_sort`, apply keys from least significant to most significant. The last pass decides the final order.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<int> group(n), score(n);
    for (auto &x : group) cin >> x;
    for (auto &x : score) cin >> x;
    vector<size_t> order(n);
    iota(order.begin(), order.end(), 0);
    stable_sort(order.begin(), order.end(), [&](size_t a, size_t b) { return score[a] > score[b]; });
    stable_sort(order.begin(), order.end(), [&](size_t a, size_t b) { return group[a] < group[b]; });
    for (size_t i : order) cout << group[i] << ' ' << score[i] << '\n';
}
```

---

## 4. `nth_element` for a Single Order Statistic

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, k;
    cin >> n >> k;
    vector<long long> a(n);
    for (auto &x : a) cin >> x;
    nth_element(a.begin(), a.begin() + k, a.end());   // a[k] is now the (k+1)-th smallest
    cout << a[k] << '\n';
}
```

`nth_element` is $O(n)$ average and touches nothing else; the remaining order is unspecified.

---

## 5. Coordinate Compression

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
    for (long long x : a) cout << lower_bound(values.begin(), values.end(), x) - values.begin() << ' ';
    cout << '\n';
}
```

Compression shrinks the value range so a Fenwick tree of size `n` can index it.

---

## 6. Complexity Notes

- Comparison sorts are $\Omega(n \log n)$; anything claiming faster on arbitrary keys is not comparison based.
- Sorting $10^6$ `int`s takes tens of milliseconds; sorting with a heap-allocating comparator key is an order slower.
- `qsort` on C structs skips template inlining; `std::sort` on a lambda is faster.