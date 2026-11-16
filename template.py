"""
Competitive Programming Python 3 / PyPy 3 Template
Author: Rai Artienda / ComProg
Optimized for: Codeforces, AtCoder, CSES, LeetCode

Notes for Pythonistas:
1. Always prefer submitting in PyPy 3 on Codeforces if available (often 5x-10x faster).
   Caveat: PyPy recursion is sometimes slower and consumes more memory than CPython.
2. For fast I/O when input is large (N >= 10^5), reading all tokens at once via
   `sys.stdin.read().split()` is the fastest possible approach in Python.
3. Avoid appending strings with += in loops; collect into a list and use "".join().
4. Use random 64-bit integer masks for dict/set keys if you suspect anti-hash hacking.
"""

import sys
import math
import collections
import bisect
import heapq

# Set higher recursion depth for deep DFS / Tree traversals
sys.setrecursionlimit(300000)

def solve():
    """
    Main solver function.
    Reads input, processes the logic, and prints the result.
    """
    input_data = sys.stdin.read().split()
    if not input_data:
        return

    iterator = iter(input_data)
    
    # Read number of test cases (t)
    # If the problem has a single testcase, comment out the t loop
    num_test_cases = int(next(iterator))
    
    out = []
    for _ in range(num_test_cases):
        n = int(next(iterator))
        arr = [int(next(iterator)) for _ in range(n)]
        
        # --- Problem logic here ---
        ans = sum(arr)
        out.append(str(ans))

    sys.stdout.write("\n".join(out) + "\n")

if __name__ == "__main__":
    solve()
