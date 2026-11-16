"""
Ordered Set / Order Statistic Tree in Python
Equivalent to C++ PBDS (__gnu_pbds::tree).

Provides:
- add(x): Inserts value x in O(log M)
- remove(x): Removes value x in O(log M)
- order_of_key(x): Returns the number of elements strictly less than x in O(log M)
- find_by_order(k): Returns the k-th smallest element (0-indexed) in O(log M)

Implemented using a Fenwick Tree with Coordinate Compression for arbitrary integers.
"""

import sys

class OrderedSetOffline:
    """
    Offline Ordered Set supporting arbitrary integer values up to 10^9.
    Requires passing all possible values (from queries and inputs) at initialization
    to construct coordinate compression.
    """
    def __init__(self, all_possible_values):
        self.sorted_unique = sorted(set(all_possible_values))
        self.val_to_rank = {v: i + 1 for i, v in enumerate(self.sorted_unique)}
        self.n = len(self.sorted_unique)
        self.bit = [0] * (self.n + 1)
        self.present = set()

    def _bit_add(self, idx, val):
        while idx <= self.n:
            self.bit[idx] += val
            idx += idx & (-idx)

    def _bit_query(self, idx):
        s = 0
        while idx > 0:
            s += self.bit[idx]
            idx -= idx & (-idx)
        return s

    def add(self, x):
        if x in self.present:
            return
        self.present.add(x)
        idx = self.val_to_rank[x]
        self._bit_add(idx, 1)

    def remove(self, x):
        if x not in self.present:
            return
        self.present.remove(x)
        idx = self.val_to_rank[x]
        self._bit_add(idx, -1)

    def order_of_key(self, x):
        """Number of elements strictly less than x."""
        import bisect
        # Find index in sorted_unique strictly less than x
        idx = bisect.bisect_left(self.sorted_unique, x)
        return self._bit_query(idx)

    def find_by_order(self, k):
        """Returns k-th smallest element (0-indexed). Returns None if out of bounds."""
        target = k + 1
        if self._bit_query(self.n) < target:
            return None
            
        idx = 0
        current_sum = 0
        mask = 1 << (self.n.bit_length() - 1)
        while mask > 0:
            nxt = idx + mask
            if nxt <= self.n and current_sum + self.bit[nxt] < target:
                idx = nxt
                current_sum += self.bit[nxt]
            mask >>= 1
            
        ans_rank = idx + 1
        return self.sorted_unique[ans_rank - 1]

TEST_CASES = [
    (
        "5\nadd 10\nadd 20\nadd 5\norder 15\nfind 1",
        "2\n10"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    it = iter(tokens)
    q = int(next(it))
    
    queries = []
    vals = []
    for _ in range(q):
        cmd = next(it)
        arg = int(next(it))
        queries.append((cmd, arg))
        if cmd in ("add", "remove", "order"):
            vals.append(arg)
            
    oset = OrderedSetOffline(vals)
    out = []
    for cmd, arg in queries:
        if cmd == "add":
            oset.add(arg)
        elif cmd == "remove":
            oset.remove(arg)
        elif cmd == "order":
            out.append(str(oset.order_of_key(arg)))
        elif cmd == "find":
            ans = oset.find_by_order(arg)
            out.append(str(ans) if ans is not None else "-1")
            
    sys.stdout.write("\n".join(out) + "\n")

if __name__ == "__main__":
    solve()
