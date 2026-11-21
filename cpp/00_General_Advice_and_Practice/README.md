---
tags:
  - cpp/general-advice
  - cpp/strategy
---

[[Home|��� Dashboard]] ❯ **C++ Module 00: General Advice and Practice Philosophy**

---

# C++ Module 00: General Advice and Practice Philosophy

Competitive programming is a discipline of reading precisely, choosing an approach that fits the limits, and implementing it without undefined behaviour. C++20 gives you the closest control over machine cost of any mainstream language; the price is that the compiler assumes you already know the rules. This module sets the standard the remaining twelve modules follow.

---

## 📏 Read the Statement Like a Contract

- Copy the constraints before writing anything: $n \le 2 \times 10^5$, $|a_i| \le 10^9$, $\sum n \le 2 \times 10^5$.
- Turn each bound into a required complexity, then into a data structure. $n \le 2 \times 10^5$ means $O(n \log n)$ at worst; $|a_i| \le 10^9$ with sums means `long long`.
- Enumerate edge cases in the constraints themselves: $n = 1$, empty graph, all values equal, maximum answer.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    long long n;
    cin >> n;
    // The statement says n <= 2 * 10^5, so an O(n log n) plan is already viable.
    // Nothing here assumes a faster bound than the paper one.
    vector<long long> a(n);
    for (auto &x : a) cin >> x;
    sort(a.begin(), a.end());
    cout << a.front() << ' ' << a.back() << '\n';
}
```

---

## 🧭 Pick the Algorithm from the Bound

| Constraint | Budget | Reach for |
|---|---|---|
| $n \le 20$ | $O(2^n n)$ | bitmask enumeration, meet-in-the-middle |
| $n \le 400$ | $O(n^3)$ | Floyd–Warshall, interval DP |
| $n \le 5 \times 10^3$ | $O(n^2)$ | DP, pairwise checks |
| $n \le 2 \times 10^5$ | $O(n \log n)$ | sorting, `std::set`, binary lifting, DSU |
| $n \le 10^6$ | $O(n)$ | two pointers, prefix sums |
| $n \le 10^9$ or $10^{18}$ | $O(\log n)$ | binary search on the answer, matrix power |

The compiler will not tell you when you overspent the budget. Only the time limit will.

---

## 🧪 Practice Loop That Actually Transfers

1. Solve a problem on paper first: state the invariant, then the steps that preserve it.
2. Implement from the paper, not from the submitted sample.
3. Write a brute-force checker with `#ifdef LOCAL` and stress it against your solution on random small inputs.
4. Only then submit, and read the verdict literally: WA is a logic bug, TLE is a cost bug, RE is usually out-of-bounds or deep recursion.

```cpp
#include <bits/stdc++.h>
using namespace std;

long long solveFast(const vector<long long> &a) {  // candidate
    long long best = LLONG_MIN, run = 0;
    for (long long x : a) { run = max(x, run + x); best = max(best, run); }
    return best;
}

#ifdef LOCAL
long long solveSlow(const vector<long long> &a) {
    long long best = LLONG_MIN;
    for (size_t i = 0; i < a.size(); ++i)
        for (size_t j = i; j < a.size(); ++j) {
            long long s = 0;
            for (size_t k = i; k <= j; ++k) s += a[k];
            best = max(best, s);
        }
    return best;
}

int main() {
    mt19937_64 rng(12345);
    for (int round = 0; round < 2000; ++round) {
        int n = 1 + rng() % 12;
        vector<long long> a(n);
        for (auto &x : a) x = (long long)(rng() % 21) - 10;
        if (solveFast(a) != solveSlow(a)) { cout << "mismatch\n"; return 1; }
    }
    cout << "stress ok\n";
}
#endif
```

---

## 🧱 Write Code the Compiler and the Judge Both Like

- `#include <bits/stdc++.h>` and the two I/O lines once at the top; then `return 0;` implicitly from `main`.
- Function-local parameters named `long long` for accumulators of values up to $10^9$.
- Index with `size_t` or `int` consistently; never mix signed and unsigned in comparisons.
- Reserve vectors when the size is known: `v.reserve(n)`.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<int> a;
    a.reserve(n);                    // one allocation instead of log(n) growth steps
    for (int i = 0; i < n; ++i) { int x; cin >> x; a.push_back(x); }
    long long total = 0;             // 10^5 values of 10^9 overflow 32 bits
    for (int x : a) total += x;
    cout << total << '\n';
}
```

---

## ⚠️ What C++ Judges Punish

- Undefined behaviour that happens to work locally: out-of-bounds reads, signed overflow, uninitialised variables.
- Floating comparison where an integer answer was asked for.
- `endl` inside loops, `cin` without `tie(nullptr)`.
- Recursion deeper than a few hundred thousand frames.

---

## ⏱️ Complexity Notes

- Reading $n$ values is $\Theta(n)$ no matter what follows.
- A single sort is $O(n \log n)$; sorting inside a loop over $n$ turns $O(n \log n)$ into $O(n^2 \log n)$.
- Every rule in this module has a cost or a UB-removal reason behind it, never style taste.

---

## 🔁 Worked Example: the Overflow Trap

Summing $10^5$ values of $10^9$ gives $10^{14}$, which does not fit in `int`. The fix is a `long long` accumulator, not a cast at the print site.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    long long total = 0;
    for (int i = 0, x; i < n; ++i) { cin >> x; total += x; }  // accumulate in 64 bits
    cout << total << '\n';
}
```

---

## ✅ Checklist Before Submitting

- Bound to complexity checked against the constraints.
- Every accumulator that can exceed $2^{31}-1$ is `long long`.
- Array sizes are `n + 5` when the problem is 1-indexed.
- Edge cases from the constraint list are tried.
- Stress test passed under `-fsanitize=undefined,address` when available.

---

## Included Source Files

- `cpp_cp_guide.md` — the C++ competitive-programming survival guide.
- `codeforces_platform_guide.md` — the platform, its submission flow, and its hacks.