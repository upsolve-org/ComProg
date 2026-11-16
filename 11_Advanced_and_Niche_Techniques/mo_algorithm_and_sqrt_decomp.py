"""
Square Root Decomposition & Mo's Algorithm in Python
1. Sqrt Decomposition: Point update in O(1), Range Sum Query in O(sqrt(N))
2. Mo's Algorithm: Offline range query processing in O((N + Q) * sqrt(N))
"""

import sys
import math

class SqrtDecomposition:
    def __init__(self, arr):
        self.n = len(arr)
        self.arr = list(arr)
        self.block_size = max(1, math.isqrt(self.n))
        num_blocks = (self.n + self.block_size - 1) // self.block_size
        self.blocks = [0] * num_blocks
        
        for i, val in enumerate(arr):
            self.blocks[i // self.block_size] += val

    def update(self, idx, val):
        diff = val - self.arr[idx]
        self.arr[idx] = val
        self.blocks[idx // self.block_size] += diff

    def query(self, l, r):
        res = 0
        b_start = l // self.block_size
        b_end = r // self.block_size
        
        if b_start == b_end:
            for i in range(l, r + 1):
                res += self.arr[i]
        else:
            # First partial block
            for i in range(l, (b_start + 1) * self.block_size):
                res += self.arr[i]
            # Complete intermediate blocks
            for b in range(b_start + 1, b_end):
                res += self.blocks[b]
            # Last partial block
            for i in range(b_end * self.block_size, r + 1):
                res += self.arr[i]
                
        return res

def mos_algorithm_distinct_values(arr, queries):
    """
    Answers number of distinct values in range [l, r] for each query offline.
    Time Complexity: O((N + Q) * sqrt(N)).
    """
    n = len(arr)
    block_size = max(1, math.isqrt(n))
    
    # queries: (l, r, original_index)
    sorted_queries = sorted(
        queries,
        key=lambda q: (q[0] // block_size, q[1] if (q[0] // block_size) % 2 == 0 else -q[1])
    )
    
    counts = {}
    curr_distinct = 0
    cur_l, cur_r = 0, -1
    answers = [0] * len(queries)
    
    def add(idx):
        nonlocal curr_distinct
        v = arr[idx]
        old = counts.get(v, 0)
        if old == 0:
            curr_distinct += 1
        counts[v] = old + 1

    def remove(idx):
        nonlocal curr_distinct
        v = arr[idx]
        old = counts[v]
        if old == 1:
            curr_distinct -= 1
        counts[v] = old - 1

    for ql, qr, qidx in sorted_queries:
        while cur_l > ql:
            cur_l -= 1
            add(cur_l)
        while cur_r < qr:
            cur_r += 1
            add(cur_r)
        while cur_l < ql:
            remove(cur_l)
            cur_l += 1
        while cur_r > qr:
            remove(cur_r)
            cur_r -= 1
        answers[qidx] = curr_distinct
        
    return answers

TEST_CASES = [
    (
        "5 3\n1 2 1 3 2\n0 4\n1 3\n2 4",
        "3\n3\n3"
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
    queries = []
    for i in range(q):
        l = int(next(it))
        r = int(next(it))
        queries.append((l, r, i))
        
    ans = mos_algorithm_distinct_values(arr, queries)
    sys.stdout.write("\n".join(map(str, ans)) + "\n")

if __name__ == "__main__":
    solve()
