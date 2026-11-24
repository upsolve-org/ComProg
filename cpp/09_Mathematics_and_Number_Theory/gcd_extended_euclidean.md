# Greatest Common Divisor and Extended Euclid

`std::gcd` in `<numeric>` is the fast, constexpr Euclidean loop. The extended version additionally produces the Bézout coefficients, which the modular inverse and the linear Diophantine solver both need.

---

## 1. Plain `std::gcd`

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    long long a, b;
    cin >> a >> b;
    cout << gcd(llabs(a), llabs(b)) << '\n';       // infers long long from the arguments
}
```

`std::gcd` returns non-negative values and handles zero as `gcd(0, x) = x`.

---

## 2. Extended Euclid

Solves $a x + b y = \gcd(a, b)$:

```cpp
#include <bits/stdc++.h>
using namespace std;

long long extended(long long a, long long b, long long &x, long long &y) {
    if (!b) { x = 1, y = 0; return a; }
    long long x1, y1;
    long long g = extended(b, a % b, x1, y1);
    x = y1;
    y = x1 - (a / b) * y1;
    return g;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    long long a, b;
    cin >> a >> b;
    long long x, y;
    cout << extended(a, b, x, y) << ' ' << x << ' ' << y << '\n';
    // a * x + b * y equals the returned gcd.
}
```

The `x1 - (a / b) * y1` term can leave `long long` only when the inputs are near $10^{18}$; then use `__int128` for the coefficient.

---

## 3. Modular Inverse

```cpp
long long inverse(long long a, long long m) {
    long long x, y;
    if (extended(a, m, x, y) != 1) return -1;      // not coprime
    return (x % m + m) % m;                        // normalise into [0, m)
}
```

---

## 4. Linear Diophantine Solution

With $g = \gcd(a, b)$ dividing $c$, the general solution is `x = x0 * (c / g) + k * (b / g)`, `y = y0 * (c / g) - k * (a / g)`. Shift `k` to get a target sign or the smallest positive `x`.

---

## 5. Complexity Notes

- Euclid is $O(\log \min(a, b))$; the extended form has the same bound.
- `std::gcd` on `int` uses binary gcd internally on some standard libraries and beats the naive `%` loop.
- All coefficients fit `long long` when `m ≤ 10^9`; nightmarish $10^{18}$ moduli want a Montgomery or Barrett wrapper.