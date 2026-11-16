"""
Two Pointers Templates in Python:
1. Two-Sum on Sorted Array (Inward pointers)
2. Merging two sorted arrays in O(N + M)
3. 3-Sum (O(N^2) using outer loop + two pointers)
"""

import sys

def two_sum_sorted(arr, target):
    """
    Finds 1-based indices (i, j) such that arr[i-1] + arr[j-1] == target.
    Returns (-1, -1) if no such pair exists.
    Time Complexity: O(N), Space: O(1).
    """
    left = 0
    right = len(arr) - 1
    while left < right:
        s = arr[left] + arr[right]
        if s == target:
            return left + 1, right + 1
        elif s < target:
            left += 1
        else:
            right -= 1
    return -1, -1

def merge_sorted_arrays(a, b):
    """Merges two sorted lists in O(len(a) + len(b))."""
    i, j = 0, 0
    res = []
    n, m = len(a), len(b)
    while i < n and j < m:
        if a[i] <= b[j]:
            res.append(a[i])
            i += 1
        else:
            res.append(b[j])
            j += 1
    while i < n:
        res.append(a[i])
        i += 1
    while j < m:
        res.append(b[j])
        j += 1
    return res

TEST_CASES = [
    (
        "5 8\n1 2 4 6 10",
        "2 4"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    n = int(tokens[0])
    target = int(tokens[1])
    arr = [int(x) for x in tokens[2:2+n]]
    i, j = two_sum_sorted(arr, target)
    sys.stdout.write(f"{i} {j}\n")

if __name__ == "__main__":
    solve()
