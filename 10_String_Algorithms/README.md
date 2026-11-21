---
tags:
  - cp/strings
  - cp/algorithms
---

[[Home|🏠 Dashboard]] ❯ **Module 10: String Algorithms**

---

# Module 10: String Algorithms

*References from [[12_Reference_and_Catalog/codeforces_catalog_full.md|Codeforces Catalog]]:*
- [Strings category on Codeforces](https://codeforces.com/catalog)
- [Hashing category](https://codeforces.com/catalog)

String processing in competitive programming involves pattern matching, prefix structures, and substring equality testing.

---

## 🧵 Core String Techniques

### 1. Polynomial Rolling Hash (Double Hash)
- Maps any substring $S[L \dots R]$ into a numeric hash value in $O(1)$ time after $O(N)$ precomputation.
- **Hacking Defense:** Single hash modulo $10^9 + 7$ is easily hacked on Codeforces (via the Thue-Morse sequence). Always use **Double Hashing** with two distinct large primes (e.g. $10^9 + 7$ and $10^9 + 9$) or random bases!

### 2. Knuth-Morris-Pratt (KMP) & Prefix Function $\pi$
- $\pi[i]$ is the length of the longest proper prefix of $S[0 \dots i]$ that is also a suffix of $S[0 \dots i]$.
- Computable in $O(N)$ time.
- Finds all occurrences of pattern $P$ in text $T$ in $O(|T| + |P|)$.

The prefix function on its own, right after a long run. `ababaca` loses its tail to three different letters over three steps, and every step falls back to an earlier border instead of jumping to `i - 1`:

```python
def prefix_function(s):
    pi = [0] * len(s)
    for i in range(1, len(s)):
        j = pi[i - 1]
        while j > 0 and s[i] != s[j]:
            j = pi[j - 1]                 # the only place a restart could hide
        if s[i] == s[j]:
            j += 1
        pi[i] = j
    return pi


print(prefix_function("ababaca"))         # [0, 0, 1, 2, 3, 0, 1]
```

At `i = 5` the character is `c`, not `b`, so `j` drops `3 → 1 → 0` in one frame; `i = 6` matches `s[0]` and gets `1`, not `5`. Each `j` only ever falls by the borders it gained, so the total work is $O(n)$.

### 3. Z-Algorithm
- Computes the $Z$-array where $Z[i]$ is the length of the longest common prefix (LCP) between $S$ and the suffix of $S$ starting at index $i$.
- Computable in $O(N)$ time.

### 4. Trie (Prefix Tree) & Binary Trie
- Tree where each edge represents a character (or bit $0/1$).
- **Binary Trie:** Inserts numbers represented in binary. Allows finding the element in the set that has the **maximum XOR** with a query value in $O(\text{bits})$.

---

## 📂 Included Source Files & Templates
- 🗝️ [[10_String_Algorithms/polynomial_rolling_hash.py|polynomial_rolling_hash.py]] — Double Rolling Hash (anti-hack)
- 🔍 [[10_String_Algorithms/kmp_prefix_function.py|kmp_prefix_function.py]] — KMP prefix function $\pi$ pattern search
- ⚡ [[10_String_Algorithms/z_algorithm.py|z_algorithm.py]] — Z-algorithm for linear string matching
- 🌲 [[10_String_Algorithms/trie_prefix_tree.py|trie_prefix_tree.py]] — String Trie & Binary Trie for maximum XOR query

---

⏮️ Previous: [[09_Mathematics_and_Number_Theory/README|09 Math & Number Theory]] | 🏠 [[Home|Dashboard]] | ⏭️ Next: [[11_Advanced_and_Niche_Techniques/README|11 Advanced Techniques]]
