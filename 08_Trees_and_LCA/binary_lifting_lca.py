"""
Binary Lifting & Lowest Common Ancestor (LCA) in Python
Preprocessing: O(N log N)
LCA / K-th Ancestor / Tree Distance Query: O(log N)
"""

import sys

sys.setrecursionlimit(300000)

class BinaryLiftingLCA:
    def __init__(self, n, adj, root=1):
        self.n = n
        self.adj = adj
        self.root = root
        self.LOG = (n).bit_length() + 1
        
        # up[k][u] is 2^k ancestor of u
        self.up = [[0] * (n + 1) for _ in range(self.LOG)]
        self.depth = [0] * (n + 1)
        
        self._dfs(root, 0, 0)
        self._build_table()

    def _dfs(self, u, p, d):
        self.depth[u] = d
        self.up[0][u] = p
        for v in self.adj[u]:
            if v != p:
                self._dfs(v, u, d + 1)

    def _build_table(self):
        for k in range(1, self.LOG):
            for u in range(1, self.n + 1):
                parent_k_minus_1 = self.up[k - 1][u]
                self.up[k][u] = self.up[k - 1][parent_k_minus_1]

    def get_kth_ancestor(self, u, k):
        """Returns the k-th ancestor of node u in O(log N). Returns 0 if none."""
        curr = u
        for bit in range(self.LOG):
            if (k >> bit) & 1:
                curr = self.up[bit][curr]
                if curr == 0:
                    break
        return curr

    def lca(self, u, v):
        """Returns Lowest Common Ancestor of u and v in O(log N)."""
        # Ensure u is deeper than v
        if self.depth[u] < self.depth[v]:
            u, v = v, u
            
        # Lift u to same depth as v
        diff = self.depth[u] - self.depth[v]
        u = self.get_kth_ancestor(u, diff)
        
        if u == v:
            return u
            
        # Lift both until just below LCA
        for k in range(self.LOG - 1, -1, -1):
            if self.up[k][u] != self.up[k][v]:
                u = self.up[k][u]
                v = self.up[k][v]
                
        return self.up[0][u]

    def distance(self, u, v):
        """Returns number of edges on unique path between u and v."""
        ancestor = self.lca(u, v)
        return self.depth[u] + self.depth[v] - 2 * self.depth[ancestor]

TEST_CASES = [
    (
        "5 2\n1 2\n1 3\n3 4\n3 5\n4 5\n2 5",
        "3\n1"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    it = iter(tokens)
    n = int(next(it))
    q = int(next(it))
    adj = [[] for _ in range(n + 1)]
    for _ in range(n - 1):
        u = int(next(it))
        v = int(next(it))
        adj[u].append(v)
        adj[v].append(u)
        
    tree = BinaryLiftingLCA(n, adj, root=1)
    out = []
    for _ in range(q):
        u = int(next(it))
        v = int(next(it))
        out.append(str(tree.lca(u, v)))
    sys.stdout.write("\n".join(out) + "\n")

if __name__ == "__main__":
    solve()
