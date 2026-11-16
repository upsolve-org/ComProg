---
tags:
  - cp/code
  - cp/data
---

[[ComProg/Home|🏠 Dashboard]] ❯ [[ComProg/05_Data_Structures/README|05_Data_Structures]] ❯ **Fenwick Tree**

---

# Fenwick Tree

> [!abstract] Implementation Note
> This note contains the complete, battle-tested Python implementation of **Fenwick Tree**.
> Source file: `ComProg/05_Data_Structures/fenwick_tree.py`
> Run test runner: `python3 run_tests.py ComProg/05_Data_Structures/fenwick_tree.py`

---

## 🐍 Python Implementation

```python
"""
Fenwick Tree (Binary Indexed Tree / BIT) in Python
Features:
- Point update, range sum query in O(log N)
- Binary lifting on Fenwick tree in O(log N) to find k-th element
- 1-based indexing internally
"""

import sys

class FenwickTree:
    def __init__(self, n):
        self.n = n
        self.tree = [0] * (n + 1)

    def add(self, idx, delta):
        """Adds delta to element at 1-based index idx."""
        while idx <= self.n:
            self.tree[idx] += delta
            idx += idx & (-idx)

    def prefix_sum(self, idx):
        """Returns sum of elements from index 1 to idx inclusive."""
        res = 0
        while idx > 0:
            res += self.tree[idx]
            idx -= idx & (-idx)
        return res

    def range_query(self, left, right):
        """Returns sum of elements in [left, right] inclusive (1-based)."""
        if left > right:
            return 0
        return self.prefix_sum(right) - self.prefix_sum(left - 1)

    def find_kth(self, k):
        """
        Binary lifting on BIT in O(log N).
        Finds smallest index with prefix_sum >= k (assuming non-negative values).
        """
        idx = 0
        current_sum = 0
        # Largest power of 2 <= n
        mask = 1 << (self.n.bit_length() - 1)
        while mask > 0:
            nxt = idx + mask
            if nxt <= self.n and current_sum + self.tree[nxt] < k:
                idx = nxt
                current_sum += self.tree[nxt]
            mask >>= 1
        return idx + 1

TEST_CASES = [
    (
        "5 4\n1 2 3 4 5\nquery 2 4\nadd 3 2\nquery 2 4\nquery 1 5",
        "9\n11\n17"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    it = iter(tokens)
    n = int(next(it))
    q = int(next(it))
    
    bit = FenwickTree(n)
    for i in range(1, n + 1):
        val = int(next(it))
        bit.add(i, val)
        
    out = []
    for _ in range(q):
        op = next(it)
        if op == "query":
            l = int(next(it))
            r = int(next(it))
            out.append(str(bit.range_query(l, r)))
        elif op == "add":
            idx = int(next(it))
            delta = int(next(it))
            bit.add(idx, delta)
    sys.stdout.write("\n".join(out) + "\n")

if __name__ == "__main__":
    solve()
```

---

## ⚡ Complexity & Analysis
- **Time Complexity:** See docstrings and implementation above.
- **Space Complexity:** See docstrings and implementation above.

---

⏮️ [[ComProg/05_Data_Structures/README|Back to 05_Data_Structures]] | 🏠 [[ComProg/Home|Dashboard]]
