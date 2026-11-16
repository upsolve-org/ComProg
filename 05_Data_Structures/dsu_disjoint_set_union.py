"""
Disjoint Set Union (DSU / Union-Find) in Python
Features:
- Path compression: O(alpha(N)) amortized operations
- Union by size: keeps tree depth minimal
- Connected components count tracker
"""

import sys

class DSU:
    def __init__(self, n):
        self.n = n
        self.parent = list(range(n))
        self.size = [1] * n
        self.num_components = n

    def find(self, x):
        """Finds representative of x with path compression."""
        root = x
        while root != self.parent[root]:
            root = self.parent[root]
        # Path compression
        curr = x
        while curr != root:
            nxt = self.parent[curr]
            self.parent[curr] = root
            curr = nxt
        return root

    def union(self, a, b):
        """Merges set containing a with set containing b. Returns True if merged."""
        root_a = self.find(a)
        root_b = self.find(b)
        if root_a == root_b:
            return False

        # Union by size: attach smaller tree under larger root
        if self.size[root_a] < self.size[root_b]:
            root_a, root_b = root_b, root_a

        self.parent[root_b] = root_a
        self.size[root_a] += self.size[root_b]
        self.num_components -= 1
        return True

    def same(self, a, b):
        return self.find(a) == self.find(b)

    def get_size(self, a):
        return self.size[self.find(a)]

TEST_CASES = [
    (
        "5 4\nunion 1 2\nunion 2 3\nsame 1 3\nsame 1 4",
        "YES\nNO"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    it = iter(tokens)
    n = int(next(it))
    q = int(next(it))
    
    # 1-indexed to 0-indexed
    dsu = DSU(n + 1)
    out = []
    for _ in range(q):
        op = next(it)
        u = int(next(it))
        v = int(next(it))
        if op == "union":
            dsu.union(u, v)
        elif op == "same":
            out.append("YES" if dsu.same(u, v) else "NO")
    sys.stdout.write("\n".join(out) + "\n")

if __name__ == "__main__":
    solve()
