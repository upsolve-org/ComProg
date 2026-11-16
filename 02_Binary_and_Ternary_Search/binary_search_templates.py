"""
Binary Search Templates in Python
- Manual Lower/Upper Bound
- Python bisect usage
- Binary search on answer predicate
- Floating point binary search
"""

import bisect

def lower_bound(arr, target):
    """
    Returns the first index i such that arr[i] >= target.
    Equivalent to bisect.bisect_left(arr, target).
    Time Complexity: O(log N).
    """
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

def upper_bound(arr, target):
    """
    Returns the first index i such that arr[i] > target.
    Equivalent to bisect.bisect_right(arr, target).
    Time Complexity: O(log N).
    """
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo

def binary_search_first_true(lo, hi, check):
    """
    Finds the minimum integer x in [lo, hi] such that check(x) is True.
    Assumes check(x) is monotonic: False ... False True ... True.
    Returns hi + 1 if no such x exists.
    """
    ans = hi + 1
    left, right = lo, hi
    while left <= right:
        mid = (left + right) // 2
        if check(mid):
            ans = mid
            right = mid - 1
        else:
            left = mid + 1
    return ans

def binary_search_last_true(lo, hi, check):
    """
    Finds the maximum integer x in [lo, hi] such that check(x) is True.
    Assumes check(x) is monotonic: True ... True False ... False.
    Returns lo - 1 if no such x exists.
    """
    ans = lo - 1
    left, right = lo, hi
    while left <= right:
        mid = (left + right) // 2
        if check(mid):
            ans = mid
            left = mid + 1
        else:
            right = mid - 1
    return ans

def float_binary_search(lo, hi, check, iterations=80):
    """
    Finds boundary for continuous mathematical monotonic functions.
    Using fixed iterations guarantees absolute/relative precision and prevents infinite loops.
    """
    left, right = float(lo), float(hi)
    for _ in range(iterations):
        mid = (left + right) / 2.0
        if check(mid):
            right = mid
        else:
            left = mid
    return (left + right) / 2.0

TEST_CASES = [
    (
        "6 3\n1 2 4 4 5 8\n4\n3\n9",
        "2 4\n2 2\n6 6"
    )
]

def solve():
    import sys
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    it = iter(tokens)
    n = int(next(it))
    q = int(next(it))
    arr = [int(next(it)) for _ in range(n)]
    
    out = []
    for _ in range(q):
        val = int(next(it))
        lb = lower_bound(arr, val)
        ub = upper_bound(arr, val)
        out.append(f"{lb} {ub}")
    sys.stdout.write("\n".join(out) + "\n")

if __name__ == "__main__":
    solve()
