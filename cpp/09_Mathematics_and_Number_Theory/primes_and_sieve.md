# A Sieve and Prime Factorisation

A sieve marks composites once per prime, and only from the square of that prime.

---

## 1. Smallest Prime Factor Sieve

The smallest-prime-factor (SPF) table factorises any value up to the limit in $O(\log v)$.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<int> spf(n + 1, 0);
    for (int i = 2; i <= n; ++i) {
        if (spf[i]) continue;
        spf[i] = i;
        if (1LL * i * i <= n)
            for (long long multiple = 1LL * i * i; multiple <= n; multiple += i)
                if (!spf[multiple]) spf[multiple] = i;
    }
    int value;
    cin >> value;
    while (value > 1) {                              // factor in O(log value)
        cout << spf[value] << ' ';
        value /= spf[value];
    }
    cout << '\n';
}
```

`if (!spf[multiple])` keeps the *smallest* factor; drop it for a plain boolean sieve.

---

## 2. Linear Sieve

Every composite is crossed exactly once, by its smallest prime factor — $O(n)$ but with more memory traffic than the plain sieve for most limits.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<int> primes;
    vector<bool> composite(n + 1, false);
    for (int i = 2; i <= n; ++i) {
        if (!composite[i]) primes.push_back(i);
        for (int p : primes) {
            if (1LL * i * p > n) break;
            composite[i * p] = true;
            if (i % p == 0) break;                   // p must be the smallest factor of i * p
        }
    }
    cout << primes.size() << '\n';
}
```

---

## 3. Trial Division for Large Single Values

Sieve the primes up to $\sqrt{x}$ (at most $10^9$ values need a $\sqrt{10^{18}} = 10^9$ sieve, so cap at $10^6$ and trial divide the remainder):

```cpp
long long remaining = x;
for (int p : primes) {
    if (1LL * p * p > remaining) break;
    while (remaining % p == 0) { factors.push_back(p); remaining /= p; }
}
if (remaining > 1) factors.push_back(remaining);      // a prime factor > sqrt(x)
```

---

## 4. Totient and Divisor Counts from the Same Sieve

`phi[i]` starts at `i` and is corrected at each prime factor; the divisor count comes from the exponent decomposition. Both need the SPF pass above.

`phi[i] = phi[i / p] * (p - 1)` when `p` divides `i / p`, otherwise `phi[i / p] * p`.

---

## 5. Complexity Notes

- Eratosthenes $O(n \log \log n)$, memory $O(n)$ with a `vector<bool>` of $n/8$ bytes.
- Linear sieve $O(n)$ but constant-heavy; mark from `i * i` in the simple version.
- SPF factorisation is $O(\log v)$; trial division alone is $O(\sqrt v)$.
- A sieve past $10^8$ needs a `bitset` and segmented passes.