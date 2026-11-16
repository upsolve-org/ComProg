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
