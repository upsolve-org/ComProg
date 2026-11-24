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

### Worked Example: Binary Search on Time
A piece that takes `e` cycles is done by minute `t` exactly `t // e` times, and there are only 3 real pieces, so each detector stops counting after 3. With detectives of speed 4 and 6 minutes per piece, the claim "two pieces are done by minute `t`" flips once and stays true:

```python
import bisect

agents = [4, 6]
evidence = [5, 3]
b = len(agents)


def pieces_done(t):
    return sum(min(t // evidence[i % len(evidence)], len(evidence)) for _ in agents for i in range(len(evidence)))


def finish():
    lo, hi = 0, 100
    while lo < hi:
        mid = (lo + hi) // 2
        if pieces_done(mid) >= b:              # feasible: binary search left
            hi = mid
        else:
            lo = mid + 1
    return lo


print(finish(), pieces_done(2), pieces_done(3))   # 3 0 2
print(bisect.bisect_left(range(100), True, key=lambda t: pieces_done(t) >= b))
```

`pieces_done` is monotone in `t` (nothing later drops below 2, then 4, and so on). One `mid` per halving of the 100-minute range finishes the job in 7 probes, and `bisect` answers the same 3 without the hand-written loop.

---

## 🎮 3. Game Theory & Nim
- **Impartial Games under Normal Play Convention:**
  - Games where available moves depend only on the current state (not on which player's turn it is).
  - Last player to move wins.
- **Bouton's Theorem for Nim:**
  - A position with pile sizes $(x_1, x_2, \dots, x_k)$ is a winning position if and only if the **XOR sum** is non-zero:
    $$x_1 \oplus x_2 \oplus \dots \oplus x_k \ne 0$$

Piles `2 3 5` XOR to `0b010 ^ 0b011 ^ 0b101 = 0b100 = 4`, so column 3 has an odd number of set bits (`1, 2, 2`) and the first player wins. The reply `p ^ x` makes every column even:

```python
piles = [2, 3, 5]
x = 0
for p in piles:
    x ^= p
print(x, x != 0)                         # 4 True

reply = [p ^ x for p in piles]
print(reply)                             # [6, 7, 1]: reducing pile 5 to 1 zeroes the XOR
print([p - r for p, r in zip(piles, reply) if r <= p])   # [4]: take 4 from pile 5
```

Check the reply: `2 ^ 3 ^ 1 = 0`. With piles `3 3 5 5` the XOR is `0` before any move, so the second player wins by mirroring every move: the two odd columns `0` and `2` already balance.
- **Sprague-Grundy Theorem:**
  - Any composite impartial game decomposes into independent games whose values equal their **Grundy value (mex of reachable states)**.

---

## 📂 Included Source Files & Templates
- 🧩 [[11_Advanced_and_Niche_Techniques/constructive_algorithms.py|constructive_algorithms.py]] — Gray code generator & parity permutations
- 📦 [[11_Advanced_and_Niche_Techniques/mo_algorithm_and_sqrt_decomp.py|mo_algorithm_and_sqrt_decomp.py]] — Sqrt decomposition & Mo's algorithm
- 🎮 [[11_Advanced_and_Niche_Techniques/game_theory_nim.py|game_theory_nim.py]] — Nim XOR sum & Sprague-Grundy theorem with `mex`

---

⏮️ Previous: [[10_String_Algorithms/README|10 String Algorithms]] | 🏠 [[Home|Dashboard]] | ⏭️ Next: [[12_Reference_and_Catalog/README|12 Reference & Catalog]]
