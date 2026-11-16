---
tags:
  - cp/math
  - cp/number-theory
---

[[Home|🏠 Dashboard]] ❯ **Module 09: Mathematics and Number Theory**

---

# Module 09: Mathematics and Number Theory

*References from [[12_Reference_and_Catalog/codeforces_catalog_full.md|Codeforces Catalog]]:*
- [Mathematics category on Codeforces](https://codeforces.com/catalog)
- [Number Theory category](https://codeforces.com/catalog)
- [Bitwise Operations category](https://codeforces.com/catalog)
- [Combinatorics category](https://codeforces.com/catalog)

Competitive programming problems heavily feature number theory, modular arithmetic, combinatorics, and bitwise manipulation. Python's native support for arbitrary-precision integers (bignums) gives it a major natural advantage here.

---

## 🔢 1. Number Theory Fundamentals

- **Primality Testing:** Deterministic trial division up to $\sqrt{N}$ in $O(\sqrt{N})$.
- **Sieve of Eratosthenes:** Finds all primes up to $N$ in $O(N \log \log N)$.
- **Smallest Prime Factor (SPF):** Computes prime factorization of any queried number $\le N$ in $O(\log N)$ after an $O(N)$ sieve preprocessing.
- **Euclidean Algorithm for GCD:** `math.gcd(a, b)` operates in $O(\log(\min(a, b)))$.

---

## 🧮 2. Modular Arithmetic & Combinatorics

Most counting problems require answers modulo a prime $P$ (typically $10^9 + 7$ or $998244353$).
- **Modular Inverse:**
  - By Fermat's Little Theorem (when $P$ is prime):
    $$a^{-1} \equiv a^{P - 2} \pmod P$$
  - In modern Python 3.8+:
    `pow(a, -1, MOD)` natively computes the modular inverse in $O(\log P)$!
- **Combinations $\binom{N}{K} \pmod P$:**
  Precomputing factorials and inverse factorials up to $N = 10^6$ in $O(N)$ allows querying $\binom{N}{K}$ in $O(1)$:
  $$\binom{N}{K} = \text{fact}[N] \cdot \text{invFact}[K] \cdot \text{invFact}[N - K] \pmod P$$

---

## 💻 3. Bitwise Manipulation Tricks

| Operation | Expression |
|---|---|
| Check if $k$-th bit is set | `(x >> k) & 1` |
| Set $k$-th bit | `x \| (1 << k)` |
| Clear $k$-th bit | `x & ~(1 << k)` |
| Toggle $k$-th bit | `x ^ (1 << k)` |
| Lowest set bit | `x & -x` |
| Clear lowest set bit | `x & (x - 1)` |
| Count set bits | `x.bit_count()` |

---

## 📂 Included Source Files & Templates
- 🔍 [[09_Mathematics_and_Number_Theory/primes_and_sieve.py|primes_and_sieve.py]] — Sieve of Eratosthenes & Smallest Prime Factor
- 🎲 [[09_Mathematics_and_Number_Theory/modular_arithmetic_and_combinatorics.py|modular_arithmetic_and_combinatorics.py]] — $nCr \pmod P$ in $O(1)$
- 🧮 [[09_Mathematics_and_Number_Theory/gcd_extended_euclidean.py|gcd_extended_euclidean.py]] — Extended GCD & Linear Diophantine solver
- 💻 [[09_Mathematics_and_Number_Theory/bitwise_operations.py|bitwise_operations.py]] — Bitwise operations & Linear Basis (XOR basis)

---

⏮️ Previous: [[08_Trees_and_LCA/README|08 Trees & LCA]] | 🏠 [[Home|Dashboard]] | ⏭️ Next: [[10_String_Algorithms/README|10 String Algorithms]]
