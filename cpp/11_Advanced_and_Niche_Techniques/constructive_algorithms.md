# Constructive Algorithms

A constructive problem states properties of the object to build (`n` even, first and last equal, sums within a bound). The algorithm builds one object and a separate argument shows it satisfies every property.

---

## 1. The Shape of a Constructive Solution

1. Copy every stated property to a checklist.
2. Find a pattern class that trivially satisfies the hard ones (`a[i] = i` is distinct, `a[0] = a[n-1]` hits a boundary).
3. Check the checklist on your own output before printing.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;                                        // n >= 2
    vector<int> a(n);
    iota(a.begin(), a.end(), 1);                     // distinct and already valid
    if (n % 2 == 0) swap(a[n / 2 - 1], a[0]);        // fixes any parity property at the ends
    for (int i = 0; i < n; ++i) cout << a[i] << " \n"[i + 1 == n];
}
```

---

## 2. Parity and Sign Tricks

Many constructive tasks become trivial once the parity or the signs are matched:

```cpp
// Sum of `n` distinct positive values equals 0 modulo 2 -> pair positives and negatives
for (int i = 1; i <= n / 2; ++i) cout << 2 * i << ' ';
for (int i = 1; i <= n / 2; ++i) cout << -2 * i << ' ';
```

---

## 3. Printing the Object

- Print exactly `n` values; the statement rejects short output.
- Output a `'\n'` or space correctly between values (`" \n"[i + 1 == n]`).
- Print a declared-size first line when the format asks for one.

---

## 4. Validating Locally

Write a 20-line checker that recomputes the properties; run it on every small `n` before committing. Constructive bugs are found by checkers, not by eyeballing.

```cpp
void check(const vector<int> &a) {
    // distinct?
    set<int> seen(a.begin(), a.end());
    assert((int)seen.size() == (int)a.size());
    // every declared property
    assert(a[0] == a.back());
    // ...
}
```

---

## 5. Complexity Notes

- Sorting is the usual cost, $O(n \log n)$; even an $O(n)$ construction is fine unless the limits are $10^7$.
- Memory is the object size, $O(n)$.
- Any valid object is accepted by the checker, so the bound is usually loose.
- A "print any" statement still requires the exact format.