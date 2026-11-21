---
tags:
  - cpp/two-pointers
  - cpp/sliding-window
---

[[Home|🏠 Dashboard]] ❯ **C++ Module 03: Two Pointers and Sliding Windows**

---

# C++ Module 03: Two Pointers and Sliding Windows

A window over an array is valid when its length or its aggregate obeys a rule. Move one end forward, advance the other until the rule is restored, and the total work stays linear because neither end ever moves backwards. C++20 gives you two loops and raw indices; the discipline is in the monotonicity proof.

---

## 👥 Two Pointers from Both Ends

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

    long long pairs = 0;
    int lo = 0, hi = n - 1;
    while (lo < hi) {
        long long sum = a[lo] + a[hi];
        if (sum == target) { ++pairs; ++lo; --hi; }
        else if (sum < target) ++lo;
        else --hi;
    }
    cout << pairs << '\n';
}
```

Sorted input is what makes "sum too small ⇒ move `lo`" provable.

---

## 🐛 Slow End for a Bounded Sum

Longest window with sum at most $S$; values are non-negative.

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
        while (run > limit) run -= a[slow++];   // window [slow, fast] is valid again
        best = max(best, fast - slow + 1);
    }
    cout << best << '\n';
}
```

`fast` advances once per step and `slow` only forward, so the inner `while` costs $\Theta(n)$ in total.

---

## 📏 Fixed-Size Windows

A fixed length `k` needs only the entering and leaving elements:

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    long long k;
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

---

## 🧮 Counting with a Frequency Table

The number of distinct values in the window lives in a small array when values are bounded:

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
        answer += fast - slow + 1;                // every suffix ends at fast
    }
    cout << answer << '\n';
}
```

---

## ⏱️ Complexity Notes

- Both pointers move strictly forward: $\Theta(n)$ steps and $\Theta(n)$ aggregate work.
- A `set`/`map` inside the window adds a $\log$ factor; a frequency array keeps it linear.
- Windows with negative values need a different tool: prefix sums plus `std::map` or a balanced tree.
- `std::deque` as a ring buffer is not needed here — indices into the vector are enough.

---

## ✅ Checklist

- The validity rule is monotone: shrinking a window can restore it.
- `slow` never jumps past `fast`.
- The frequency or sum state is updated on both the enter and the leave side.
- Empty windows are allowed by the statement before you assume them.

---

## Included Source Files

- `two_pointers_templates.md` — converging and slow/fast pointer skeletons.
- `sliding_window_templates.md` — fixed, variable, and frequency-carrying windows.