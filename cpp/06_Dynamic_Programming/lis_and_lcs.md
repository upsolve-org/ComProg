# Longest Increasing Subsequence and Longest Common Subsequence

Two canonical sequence DPs with different bounds. The LIS has an $O(n \log n)$ solution via patience sorting; the LCS is $O(nm)$ and the right target is the bit-parallel or Hunt–Szymanski variant when $nm$ grows.

---

## 1. LIS in $O(n \log n)$

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<long long> tails;
    tails.reserve(n);
    for (int i = 0, x; i < n; ++i) {
        cin >> x;
        auto it = lower_bound(tails.begin(), tails.end(), x);  // strict: lower_bound
        if (it == tails.end()) tails.push_back(x); else *it = x;
    }
    cout << tails.size() << '\n';
}
```

`tails[l]` is the smallest possible last element of an increasing run of length $l + 1$. To allow duplicates (non-decreasing runs) switch to `upper_bound`.

---

## 2. Reconstructing an LIS

Keep the predecessor and the index of the last tail:

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<long long> a(n), tails;
    for (auto &x : a) cin >> x;
    vector<int> last(n, -1), tailIndex;
    for (int i = 0; i < n; ++i) {
        auto it = lower_bound(tails.begin(), tails.end(), a[i]);
        int pos = int(it - tails.begin());
        last[i] = pos ? tailIndex[pos - 1] : -1;
        if (it == tails.end()) { tails.push_back(a[i]); tailIndex.push_back(i); }
        else { *it = a[i]; tailIndex[pos] = i; }
    }
    vector<int> answer;
    for (int i = tailIndex.back(); i != -1; i = last[i]) answer.push_back(i);
    reverse(answer.begin(), answer.end());
    for (size_t k = 0; k < answer.size(); ++k) cout << a[answer[k]] << " \n"[k + 1 == answer.size()];
}
```

---

## 3. LCS with Two Rows

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string a, b;
    cin >> a >> b;
    if (b.size() < a.size()) swap(a, b);                     // small string along the width
    int m = (int)b.size();
    vector<int> previous(m + 1, 0), current(m + 1, 0);
    for (char ca : a) {
        fill(current.begin(), current.end(), 0);
        for (int j = 1; j <= m; ++j) {
            current[j] = ca == b[j - 1] ? previous[j - 1] + 1
                                       : max(previous[j], current[j - 1]);
        }
        swap(previous, current);
    }
    cout << previous[m] << '\n';
}
```

The `swap(a, b)` puts the shorter string along the width to save memory.

---

## 4. Where These Bounds Break

- LCS with equal lengths of $10^5$: the $O(nm)$ table has $10^{10}$ cells. Use bit-parallel LCS ($O(nm / 64)$) via `bitset`.
- LIS with positions from a permutation (e.g. after sorting by one key): the same $O(n \log n)$ code applies, because the pairs collapse to one permutation.
- "Longest increasing subsequence modulo something": it is a DAG longest path once the graph is built.

---

## 5. Complexity Notes

- LIS: $O(n \log n)$ time, $\Theta(n)$ memory.
- LCS: $O(nm)$ time, $\Theta(m)$ memory in the rolling version.
- Reconstructing an LIS adds $\Theta(n)$ arrays and is $O(n)$ afterwards.