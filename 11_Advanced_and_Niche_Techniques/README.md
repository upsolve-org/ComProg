---
tags:
  - cp/advanced
  - cp/algorithms
---

[[Home|🏠 Dashboard]] ❯ **Module 11: Advanced and Niche Techniques**

---

# Module 11: Advanced and Niche Techniques

*References from [[12_Reference_and_Catalog/codeforces_catalog_full.md|Codeforces Catalog]]:*
- [Constructive Algorithms category](https://codeforces.com/catalog)
- [Square Root Techniques category](https://codeforces.com/catalog)
- [Sweeping Line category](https://codeforces.com/catalog)
- [Games (Game Theory) category](https://codeforces.com/catalog)

This module covers specialized, higher-tier contest techniques frequently seen in Codeforces Div 2 (C/D/E) and Div 1 rounds.

---

## 🧩 1. Constructive Algorithms
*Reference: [Tips on Constructive Algorithms by vmaksimovski](https://codeforces.com/blog/entry/75765)*
- Instead of finding a value, you are asked to construct an array, matrix, permutation, or sequence satisfying specific properties.
- **Mental Framework:**
  - Test $N = 1, 2, 3, 4, 5$ by hand.
  - Look for invariants (parity of sum, alternating patterns $1, -1, 1, -1$, binary representation).
  - Solve backwards from the target configuration.

---

## 📦 2. Square Root Decomposition & Mo's Algorithm
- **Sqrt Decomposition:** Divides an array of length $N$ into blocks of size $B \approx \sqrt{N}$. Point updates take $O(1)$ and range queries take $O(\sqrt{N})$.
- **Mo's Algorithm:** Offline algorithm to answer $Q$ range queries on an array in $O((N + Q)\sqrt{N})$ time.
  - Sorts queries by block of left endpoint, then right endpoint (Hilbert order or alternating left-right).

---

## 🎮 3. Game Theory & Nim
- **Impartial Games under Normal Play Convention:**
  - Games where available moves depend only on the current state (not on which player's turn it is).
  - Last player to move wins.
- **Bouton's Theorem for Nim:**
  - A position with pile sizes $(x_1, x_2, \dots, x_k)$ is a winning position if and only if the **XOR sum** is non-zero:
    $$x_1 \oplus x_2 \oplus \dots \oplus x_k \ne 0$$
- **Sprague-Grundy Theorem:**
  - Any composite impartial game decomposes into independent games whose values equal their **Grundy value (mex of reachable states)**.

---

## 📂 Included Source Files & Templates
- 🧩 [[11_Advanced_and_Niche_Techniques/constructive_algorithms.py|constructive_algorithms.py]] — Gray code generator & parity permutations
- 📦 [[11_Advanced_and_Niche_Techniques/mo_algorithm_and_sqrt_decomp.py|mo_algorithm_and_sqrt_decomp.py]] — Sqrt decomposition & Mo's algorithm
- 🎮 [[11_Advanced_and_Niche_Techniques/game_theory_nim.py|game_theory_nim.py]] — Nim XOR sum & Sprague-Grundy theorem with `mex`

---

⏮️ Previous: [[10_String_Algorithms/README|10 String Algorithms]] | 🏠 [[Home|Dashboard]] | ⏭️ Next: [[12_Reference_and_Catalog/README|12 Reference & Catalog]]
