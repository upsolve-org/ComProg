# Sliding Window Templates

## 1. Fixed Length

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
    long long run = accumulate(a.begin(), a.begin() + k, 0LL), best = run;
    for (int i = k; i < n; ++i) {
        run += a[i] - a[i - k];
        best = max(best, run);
    }
    cout << best << '\n';
}
```

The entering element `a[i]` and the leaving element `a[i - k]` cancel in one step; no inner loop exists.

---

## 2. Variable Length with a Restorable Rule

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

---

## 3. Counting Subarrays with a Rule

Count windows ending at `fast` that satisfy it:

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, k;
    cin >> n >> k;
    vector<int> a(n), freq(n + 1, 0);
    for (auto &x : a) cin >> x;
    int distinct = 0;
    long long answer = 0;
    for (int fast = 0, slow = 0; fast < n; ++fast) {
        if (freq[a[fast]]++ == 0) ++distinct;
        while (distinct > k)
            if (--freq[a[slow++]] == 0) --distinct;
        answer += fast - slow + 1;
    }
    cout << answer << '\n';
}
```

Each valid suffix count is `fast - slow + 1`; summing it counts every window exactly once, at its right end.

---

## 4. Window with a Monotonic Deque

Maximum of every window of length $k$ in $O(n)$: keep indices in decreasing value order.

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
    deque<int> window;
    for (int i = 0; i < n; ++i) {
        while (!window.empty() && a[window.back()] <= a[i]) window.pop_back();
        window.push_back(i);
        if (window.front() <= i - k) window.pop_front();
        if (i + 1 >= k) cout << a[window.front()] << ' ';
    }
    cout << '\n';
}
```

`std::deque` supports $O(1)$ pop at both ends; `window.pop_front()` is legal and cheap.

---

## 5. Failure Cases

- Negative values with "sum at most $S$": the window sum is not monotone in length. Use prefix sums plus `map`.
- "At most $k$ values greater than $X$": still monotone in length, but the counter must be exact.
- Huge values: window sum as `long long`; if it can still overflow, the statement usually caps the count.

---

## 6. Complexity Notes

- Amortised $\Theta(n)$; every index enters and leaves once.
- The deque variant is $\Theta(n)$ and replaces the $O(n \log k)$ multiset version.
- Memory is $\Theta(n)$ for the data plus the frequency table or deque.