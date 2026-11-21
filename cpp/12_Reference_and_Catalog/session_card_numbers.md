# Session Card: Numbers

- Accumulators and answers: `long long` whenever the sum can pass $2^{31}-1$.
- Products: `__int128` when factors approach $10^{18}$.
- Modular power:

```cpp
long long power(long long base, long long exponent, long long mod) {
    long long result = 1 % mod;
    for (base %= mod; exponent; exponent >>= 1, base = (__int128)base * base % mod)
        if (exponent & 1) result = (__int128)result * base % mod;
    return result;
}
```

- Inverse: Fermat `power(a, p - 2, p)` for prime `p`; extended Euclid otherwise.
- Overflow-safe sum of two `long long`: `a > LLONG_MAX - b ? wrap : a + b`.
- `std::gcd` takes absolute values; sign it yourself.
- Floating answers: `fixed << setprecision(9)` and compare with `1e-9`.
- Bit shifts: `1ULL << k`, guard `k >= 64`.
- `INT_MIN / -1` overflows `int`; cast first.