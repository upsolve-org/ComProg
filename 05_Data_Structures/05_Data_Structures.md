---
tags:
  - cp/data-structures
---

[[Home|🏠 Dashboard]] ❯ **Module 05: Data Structures**

---

# Module 05: Data Structures

*References from [[12_Reference_and_Catalog/codeforces_catalog_full.md|Codeforces Catalog]]:*
- [EDU: Disjoint Set Union by Aksenov239](https://codeforces.com/blog/entry/75428)
- [EDU: Segment Tree by pashka](https://codeforces.com/blog/entry/78762)
- [Efficient and easy segment trees by Al.Cash](https://codeforces.com/blog/entry/18051)
- [C++ STL: Policy based data structures by adamant](https://codeforces.com/blog/entry/11080)

Data structures allow us to store, query, and mutate collections of data efficiently. In competitive programming, mastering these core structures is the prerequisite to crossing the 1400–1600 rating threshold.

---

## 🌲 Core Structures

### 1. Disjoint Set Union (DSU / Union-Find)
- Maintains partition of elements into disjoint dynamic sets.
- With **Path Compression** and **Union by Size/Rank**, operations are virtually $O(1)$ (specifically $O(\alpha(N))$, where $\alpha$ is the Inverse Ackermann function $\le 4$).
- Applications: Kruskal's MST, connected components, cycle detection in undirected graphs.

### 2. Fenwick Tree (Binary Indexed Tree - BIT)
- $O(\log N)$ Point Updates and $O(\log N)$ Prefix Sum queries.
- Extremely lightweight, low memory overhead, and 2× to 3× faster constant factors in Python than segment trees.
- Supports 1D and 2D arrays, inversion counting, and binary lifting in $O(\log N)$.

### 3. Segment Tree
- Can maintain arbitrary associative operations: Range Min/Max, Range Sum, Range GCD, XOR.
- **Iterative Segment Tree:** Fast and simple for point update + range query in $O(\log N)$ without recursive function overhead.
- **Lazy Propagation:** Supports range updates (e.g. add $+V$ to all elements in $[L, R]$) and range queries in $O(\log N)$.

### 4. Monotonic Stack & Queue
- **Monotonic Stack:** Solves "Next Greater Element" / "Previous Smaller Element" in $O(N)$ total time. Used in Largest Rectangle in Histogram.
- **Monotonic Queue:** Sliding Window Minimum/Maximum in amortized $O(1)$ per step.

### 5. Ordered Set (Simulating C++ PBDS in Python)
- In C++, `__gnu_pbds::tree` provides `order_of_key` (rank of element) and `find_by_order` ($K$-th smallest element) in $O(\log N)$.
- In Python, we implement this natively using coordinate compression + Fenwick Tree, or using the external `sortedcontainers.SortedList` when available.

---

## 📂 Included Source Files & Templates
- 🔗 [[05_Data_Structures/dsu_disjoint_set_union.py|dsu_disjoint_set_union.py]] — DSU with path compression & size tracking
- 🌳 [[05_Data_Structures/fenwick_tree.py|fenwick_tree.py]] — Fenwick Tree (PURQ & binary lifting $K$-th element)
- 📊 [[05_Data_Structures/segment_tree.py|segment_tree.py]] — Iterative Segment Tree & Lazy Segment Tree
- 📉 [[05_Data_Structures/monotonic_stack_and_queue.py|monotonic_stack_and_queue.py]] — Next Greater Element, Histogram & Sliding Max
- 🏷️ [[05_Data_Structures/ordered_set_python.py|ordered_set_python.py]] — Policy-Based Ordered Set in Python

---

⏮️ Previous: [[04_Sorting_and_Greedy/README|04 Sorting & Greedy]] | 🏠 [[Home|Dashboard]] | ⏭️ Next: [[06_Dynamic_Programming/README|06 Dynamic Programming]]
