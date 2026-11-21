# Modular Arithmetic and Combinatorics

## 1. Modular Multiplication Without Overflow

```cpp
long long multiply(long long a, long long b, long long m) {
    return (__int128)a * b % m;                       // safe for any 64-bit a, b, m
}
```

`a * b % m` with $a, b \sim 10^9$ still fits `long long`; with $10^{18}$ it does not and `__int128` is mandatory.

---

## 2. Factorials and Binomial Coefficients

```cpp
#include <bits/stdc++.h>
using namespace std;

constexpr long long MOD = 1'000'000'007;

long long power(long long base, long long exponent) {
    long long result = 1;
    for (base %= MOD; exponent; exponent >>= 1, base = (__int128)base * base % MOD)
        if (exponent & 1) result = (__int128)result * base % MOD;
    return result;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, k;
    cin >> n >> k;
    vector<long long> factorial(n + 1, 1);
    for (int i = 1; i <= n; ++i) factorial[i] = factorial[i - 1] * i % MOD;
    auto choose = [&](int a, int b) {
        if (b < 0 || b > a) return 0LL;
        return factorial[a] * power(factorial[b], MOD - 2) % MOD * power(factorial[a - b], MOD - 2) % MOD;
    };
    cout << choose(n, k) << '\n';
}
```

---

## 3. Catalan and Derangements

- Catalan $C_n = \binom{2n}{n} / (n + 1)$ counts balanced sequences; the division is another modular inverse.
- Derangements $D_n = (n - 1)(D_{n-1} + D_{n-2})$ with $D_0 = 1$, $D_1 = 0$.

---

## 4. The Prime-Modulus Conditions

- Fermat's inverse needs $p$ prime and $n < p$.
- With $n \ge p$ use Lucas: $\binom{n}{k} \bmod p = \prod \binom{n_i}{k_i} \bmod p$ over base-$p$ digits.
- With a composite modulus use extended Euclid per denominator, or CRT over prime powers.

---

## 5. Running Products with Zeros

A quotient of products needs zero handling: count zeros and keep the product of non-zero factors, else the reverse multiplication corrupts everything.

```cpp
// product of all but one element, modulo 1e9 + 7:
// zeros = count of zeros; product = product of non-zero values
// answer[i] = zeros > 1 ? 0 : zeros == 1 ? (a[i] ? 0 : product) : product * inverse(a[i])
```

---

## 6. Complexity Notes

- Each `power` call is $O(\log \text{MOD})$; precomputing both factorial and inverse factorial makes each `choose` $O(1)$.
- Tables cost $\Theta(n)$ memory and must stay below the modulus.
- One `%` on 64-bit values is a division instruction; `__int128` products compile to two 64-bit multiplies and a division, so avoid them in millions-per-second loops.