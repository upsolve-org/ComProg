"""
Segment Tree in Python:
1. Iterative Segment Tree: Point Update, Range Query in O(log N) - Ultra-fast in Python.
2. Lazy Propagation Segment Tree: Range Addition Update, Range Sum Query in O(log N).
"""

import sys

class IterativeSegmentTree:
    """
    Non-recursive Segment Tree for point update and range query.
    0-indexed externally.
    """
    def __init__(self, data, default=0, func=lambda a, b: a + b):
        self.n = len(data)
        self.default = default
        self.func = func
        self.tree = [default] * (2 * self.n)
        
        # Build initial leaves
        for i in range(self.n):
            self.tree[self.n + i] = data[i]
            
        # Build internal nodes
        for i in range(self.n - 1, 0, -1):
            self.tree[i] = self.func(self.tree[2 * i], self.tree[2 * i + 1])

    def update(self, pos, value):
        """Sets element at index pos to value."""
        pos += self.n
        self.tree[pos] = value
        pos >>= 1
        while pos > 0:
            self.tree[pos] = self.func(self.tree[2 * pos], self.tree[2 * pos + 1])
            pos >>= 1

    def query(self, left, right):
        """Returns func(arr[left ... right]) inclusive."""
        res_left = self.default
        res_right = self.default
        left += self.n
        right += self.n + 1
        
        while left < right:
            if left & 1:
                res_left = self.func(res_left, self.tree[left])
                left += 1
            if right & 1:
                right -= 1
                res_right = self.func(self.tree[right], res_right)
            left >>= 1
            right >>= 1
            
        return self.func(res_left, res_right)

class LazySegmentTree:
    """
    Segment Tree with Lazy Propagation supporting:
    - Range Addition: arr[l ... r] += val
    - Range Sum Query: sum(arr[l ... r])
    """
    def __init__(self, data):
        self.n = len(data)
        self.tree = [0] * (4 * self.n)
        self.lazy = [0] * (4 * self.n)
        if self.n > 0:
            self._build(data, 1, 0, self.n - 1)

    def _build(self, data, node, l, r):
        if l == r:
            self.tree[node] = data[l]
            return
        mid = (l + r) // 2
        self._build(data, 2 * node, l, mid)
        self._build(data, 2 * node + 1, mid + 1, r)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def _push(self, node, l, r):
        if self.lazy[node] != 0:
            val = self.lazy[node]
            mid = (l + r) // 2
            
            # Apply to left child
            self.lazy[2 * node] += val
            self.tree[2 * node] += val * (mid - l + 1)
            
            # Apply to right child
            self.lazy[2 * node + 1] += val
            self.tree[2 * node + 1] += val * (r - mid)
            
            self.lazy[node] = 0

    def update_range(self, ql, qr, val, node=1, l=0, r=None):
        if r is None:
            r = self.n - 1
        if ql > r or qr < l:
            return
        if ql <= l and r <= qr:
            self.tree[node] += val * (r - l + 1)
            self.lazy[node] += val
            return
            
        self._push(node, l, r)
        mid = (l + r) // 2
        self.update_range(ql, qr, val, 2 * node, l, mid)
        self.update_range(ql, qr, val, 2 * node + 1, mid + 1, r)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def query_range(self, ql, qr, node=1, l=0, r=None):
        if r is None:
            r = self.n - 1
        if ql > r or qr < l:
            return 0
        if ql <= l and r <= qr:
            return self.tree[node]
            
        self._push(node, l, r)
        mid = (l + r) // 2
        return (
            self.query_range(ql, qr, 2 * node, l, mid)
            + self.query_range(ql, qr, 2 * node + 1, mid + 1, r)
        )

TEST_CASES = [
    (
        "5 4\n1 2 3 4 5\nquery 1 3\nupdate 2 10\nquery 1 3\nquery 0 4",
        "9\n16\n22"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    it = iter(tokens)
    n = int(next(it))
    q = int(next(it))
    arr = [int(next(it)) for _ in range(n)]
    
    st = IterativeSegmentTree(arr, default=0, func=lambda a, b: a + b)
    out = []
    for _ in range(q):
        op = next(it)
        if op == "query":
            l = int(next(it))
            r = int(next(it))
            out.append(str(st.query(l, r)))
        elif op == "update":
            pos = int(next(it))
            val = int(next(it))
            st.update(pos, val)
    sys.stdout.write("\n".join(out) + "\n")

if __name__ == "__main__":
    solve()
