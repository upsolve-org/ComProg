---
tags:
  - cpp/math
  - cpp/number-theory
---

[[Home|🏠 Dashboard]] ❯ **C++ Module 09: Mathematics and Number Theory**

---

# C++ Module 09: Mathematics and Number Theory

C++ has no big integers, so every sum, product and modulus must fit in a fixed type. $a \cdot b \bmod m$ with both factors near $10^9$ and $m$ near $10^9$ needs `long long`; with factors near $10^{18}$ it needs `__int128`. Everything in this module assumes **unsigned** arithmetic for bit tricks and stays modular for combinatorics.

---

## 🔎 Sieve of Eratosthenes

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<bool> composite(n + 1, false);
    vector<int> primes;
    for (int i = 2; i <= n; ++i) {
        if (composite[i]) continue;
        primes.push_back(i);
        if (1LL * i * i <= n)
            for (int multiple = i * i; multiple <= n; multiple += i) composite[multiple] = true;
    }
    cout << primes.size() << '\n';
}
```

`i * i` is written as `1LL * i * i` so $n$ up to $10^{9}$ cannot overflow the start point.

---

## 🧮 Binary Exponentiation

```cpp
#include <bits/stdc++.h>
using namespace std;

long long power(long long base, long long exponent, long long mod) {
    long long result = 1 % mod;
    for (base %= mod; exponent; exponent >>= 1, base = (__int128)base * base % mod)
        if (exponent & 1) result = (__int128)result * base % mod;
    return result;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    long long a, b, m;
    cin >> a >> b >> m;
    cout << power(a, b, m) << '\n';
}
```

`1 % mod` covers `m = 1`; the loop is $O(\log b)$.

---

## 🧱 Extended Euclid and the Modular Inverse

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

    long long a, m;
    cin >> a >> m;
    long long x, y;
    long long g = extended(a, m, x, y);
    if (g != 1) { cout << "no inverse\n"; return 0; }
    cout << ((x % m) + m) % m << '\n';
}
```

The inverse exists exactly when $\gcd(a, m) = 1$; for a prime modulus `power(a, m - 2, m)` is shorter.

---

## 🎲 Combinatorics Modulo a Prime

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    constexpr long long MOD = 1'000'000'007;
    int n;
    cin >> n;
    vector<long long> factorial(n + 1, 1), inverseFactorial(n + 1, 1);
    for (int i = 1; i <= n; ++i) factorial[i] = factorial[i - 1] * i % MOD;
    auto power = [&](long long base, long long exponent) {
        long long result = 1;
        for (base %= MOD; exponent; exponent >>= 1, base = (__int128)base * base % MOD)
            if (exponent & 1) result = (__int128)result * base % MOD;
        return result;
    };
    inverseFactorial[n] = power(factorial[n], MOD - 2);
    for (int i = n; i > 1; --i) inverseFactorial[i - 1] = inverseFactorial[i] * i % MOD;
    auto choose = [&](int a, int b) {
        return a < b ? 0LL : factorial[a] * inverseFactorial[b] % MOD * inverseFactorial[a - b] % MOD;
    };
    cout << choose(n, n / 2) << '\n';
}
```

Fermat's inverse needs $n < \text{MOD}$; beyond that, use Lucas' theorem.

---

## 🔢 Bitwise Operations

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    unsigned long long x;
    cin >> x;
    cout << popcount(x) << ' ' << (63 - countl_zero(x)) << ' ';   // countl_zero is 64 for x = 0
    x &= x - 1;                                   // clear the least set bit
    cout << bit_width(x) << '\n';
}
```

- `popcount`, `countl_zero`, `countr_zero`, `bit_width` are C++20 `<bit>`.
- `x & (x - 1)` clears the lowest set bit; `x & -x` isolates it.
- Shifts of 64 or more on `uint64_t` are $2^{64}$ wraparound, not saturation.

---

## ⏱️ Complexity Notes

- Sieve $O(n \log \log n)$; segmented sieve $O(\sqrt{n} + \text{range})$.
- Binary exponentiation $O(\log e)$.
- Extended Euclid $O(\log \min(a, b))$.
- Factorial tables $O(n)$ time and memory; each `choose` is $O(1)$.

---

## ✅ Checklist

- Every product goes through `long long` or `__int128` before the modulus.
- Modulus can be 1 — start with `1 % mod`.
- Bit loops over 64 bits use `unsigned long long`, not `int`.
- Fermat inverse used only with a prime modulus and $n < p$.

---

## Included Source Files

- `gcd_extended_euclidean.md`, `primes_and_sieve.md`
- `modular_arithmetic_and_combinatorics.md`, `bitwise_operations.md`