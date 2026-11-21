# Monotonic Stack and Monotonic Deque

A monotonic stack keeps a subsequence of indices in increasing value order, so each index can find its nearest greater or smaller neighbour in $\Theta(n)$. A monotonic deque adds a front pop, which makes it the $O(n)$ sliding-window maximum.

---

## 1. Nearest Strictly Greater to the Right

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<long long> a(n), answer(n, -1);
    for (auto &x : a) cin >> x;
    vector<int> stack;
    stack.reserve(n);
    for (int i = n; i-- > 0;) {
        while (!stack.empty() && a[stack.back()] <= a[i]) stack.pop_back();
        if (!stack.empty()) answer[i] = stack.back();
        stack.push_back(i);
    }
    for (int x : answer) cout << x + 1 << ' ';
    cout << '\n';
}
```

`<=` pops equal values, giving the *strictly* greater neighbour. `a[stack.back()` starts larger than `a[i]`; `answer[i]` is their first difference.

---

## 2. Largest Rectangle in a Histogram

The stack holds a non-decreasing run of heights; a shorter bar ends every run taller than it.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<long long> h(n + 1, 0);                          // sentinel ends the last run
    for (int i = 0; i < n; ++i) cin >> h[i];
    vector<int> stack;
    long long best = 0;
    for (int i = 0; i <= n; ++i) {
        while (!stack.empty() && h[stack.back()] >= h[i]) {
            long long top = h[stack.back()];
            stack.pop_back();
            int left = stack.empty() ? -1 : stack.back();
            best = max(best, top * (i - left - 1));
        }
        stack.push_back(i);
    }
    cout << best << '\n';
}
```

---

## 3. Sliding-Window Maximum with `std::deque`

`deque` pops at both ends in $O(1)$, which `vector` cannot do at the front.

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

---

## 4. Monotonic vs `priority_queue`

- `priority_queue` never forgets; an expired maximum stays until it reaches the top. The usual workaround is a lazy deletion pair of heaps.
- The deque literally removes expired indices, so it is $O(n)$ in the worst case, not $O(n \log n)$.

---

## 5. Complexity Notes

- Every index is pushed once and popped once: amortised $\Theta(n)$.
- Each stack or deque is $O(n)$ memory; the `vector` form can `reserve(n)`.
- One `push_back`/`pop_back` pair on `deque` is $O(1)$ but with an indirection step; medium-len problems prefer `vector` stacks.