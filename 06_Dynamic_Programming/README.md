---
tags:
  - cp/dp
  - cp/algorithms
---

[[Home|🏠 Dashboard]] ❯ **Module 06: Dynamic Programming**

---

# Module 06: Dynamic Programming (DP)

*References from [[12_Reference_and_Catalog/codeforces_catalog_full.md|Codeforces Catalog]]:*
- [Dynamic Programming category on Codeforces](https://codeforces.com/catalog)
- [Dp On Trees by AghaTizi](https://codeforces.com/blog/entry/63257)

Dynamic Programming solves complex optimization problems by decomposing them into overlapping subproblems, satisfying the principle of **Optimal Substructure** (an optimal solution contains optimal solutions to its subproblems).

---

## 🧠 The 4-Step DP Blueprint

1. **State Definition:** What minimal parameters uniquely define a subproblem? (e.g. `dp[i][w]` = max value using a subset of first $i$ items with total weight $\le w$).
2. **Transition / Recurrence Relation:** How does the current state compute its answer from smaller previously solved states?
3. **Base Cases & Initialization:** What are the trivial endpoints? (e.g. `dp[0][0] = 0`, unreachable states = $-\infty$ or $\infty$).
4. **Order of Computation & Space Optimization:** Can we compute iteratively (tabulation) row by row, and compress the state table from 2D to 1D?

### Worked Example: 0/1 Knapsack in 1D
Weights `[2, 3, 4, 5]`, values `[3, 4, 5, 7]`, capacity `5`. Values come first, then weights; the capacity is the heaviest weight, so every item is affordable on its own:

```python
def knapsack(values, weights, capacity):
    best = [0] * (capacity + 1)              # best[w] = max value with total weight exactly w
    for v, w in zip(values, weights):
        for room in range(capacity, w - 1, -1):   # backwards, so w is used once
            best[room] = max(best[room], best[room - w] + v)
    return max(best)


print(knapsack([3, 4, 5, 7], [2, 3, 4, 5], 5))   # 7: item 4 alone beats 3 + 4
```

Walking `room` backwards is the whole trick. Forward, `best[room - w]` may already hold the current item, and the same table answers the unbounded variant. The values trace `[3, 4, 5, 7]`: taking both `3` and `4` (weights 2 + 3) gives 7 for weight 5, and `7` for weight 5 ties it.

---

## 🐍 Python-Specific DP Best Practices

### Top-Down (Memoization) vs. Bottom-Up (Tabulation)
- **Top-Down with `@functools.lru_cache(maxsize=None)`:**
  - Quick to write during contest pressure.
  - *Pitfall:* Python recursion stack overhead! Remember to set `sys.setrecursionlimit(300000)`. If depth exceeds $\sim 5 \times 10^5$, PyPy may encounter memory overhead or crash.
- **Bottom-Up (Tabulation):**
  - Iterative loops with 1D/2D lists.
  - Much faster on PyPy3 due to JIT loop unrolling and eliminates recursion overhead entirely.
  - Enables **rolling array space optimization** (e.g., $O(N \cdot W)$ space $\to O(W)$ space).

---

## 📂 Included Source Files & Templates
- 🎒 [[06_Dynamic_Programming/01_knapsack_and_subsets.py|01_knapsack_and_subsets.py]] — 0/1 Knapsack, Unbounded & Subset Sum
- 🏁 [[06_Dynamic_Programming/grid_and_paths_dp.py|grid_and_paths_dp.py]] — Grid paths with obstacles mod $10^9 + 7$ & Min Path Sum
- 📈 [[06_Dynamic_Programming/lis_and_lcs.py|lis_and_lcs.py]] — LIS in $O(N \log N)$ & LCS in $O(NM)$
- 🪨 [[06_Dynamic_Programming/interval_and_range_dp.py|interval_and_range_dp.py]] — Matrix chain multiplication / interval DP
- 🌲 [[06_Dynamic_Programming/tree_dp.py|tree_dp.py]] — Tree diameter & maximum independent set on tree
- 🎭 [[06_Dynamic_Programming/bitmask_dp.py|bitmask_dp.py]] — Traveling Salesperson ($O(N^2 2^N)$) & submask enumeration

---

⏮️ Previous: [[05_Data_Structures/README|05 Data Structures]] | 🏠 [[Home|Dashboard]] | ⏭️ Next: [[07_Graph_Algorithms/README|07 Graph Algorithms]]
