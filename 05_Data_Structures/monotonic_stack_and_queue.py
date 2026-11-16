"""
Monotonic Stack & Monotonic Queue Templates in Python.
1. Next Greater Element: O(N) using Monotonic Stack
2. Largest Rectangle in Histogram: O(N)
3. Sliding Window Maximum: O(N) using Monotonic Deque
"""

import sys
import collections

def next_greater_elements(arr):
    """
    Returns array res where res[i] is the first index j > i such that arr[j] > arr[i].
    If no such index exists, res[i] = -1.
    Time Complexity: O(N).
    """
    n = len(arr)
    res = [-1] * n
    stack = []  # Stores indices
    
    for i in range(n):
        while stack and arr[i] > arr[stack[-1]]:
            prev_idx = stack.pop()
            res[prev_idx] = i
        stack.append(i)
        
    return res

def largest_rectangle_in_histogram(heights):
    """
    Calculates the largest rectangular area in a histogram.
    Time Complexity: O(N).
    """
    stack = []  # stores index
    max_area = 0
    h = heights + [0]  # dummy sentinel
    
    for i, curr_h in enumerate(h):
        start = i
        while stack and stack[-1][1] > curr_h:
            idx, height = stack.pop()
            max_area = max(max_area, height * (i - idx))
            start = idx
        stack.append((start, curr_h))
        
    return max_area

def sliding_window_maximum(arr, k):
    """
    Finds the maximum value in every sliding window of size k.
    Time Complexity: O(N).
    """
    dq = collections.deque()  # Stores indices of elements in decreasing order
    res = []
    
    for i in range(len(arr)):
        # Remove elements outside window
        if dq and dq[0] < i - k + 1:
            dq.popleft()
            
        # Maintain decreasing order in deque
        while dq and arr[dq[-1]] <= arr[i]:
            dq.pop()
            
        dq.append(i)
        
        # Window is full
        if i >= k - 1:
            res.append(arr[dq[0]])
            
    return res

TEST_CASES = [
    (
        "6\n2 1 5 6 2 3",
        "10"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    n = int(tokens[0])
    heights = [int(x) for x in tokens[1:1+n]]
    ans = largest_rectangle_in_histogram(heights)
    sys.stdout.write(str(ans) + "\n")

if __name__ == "__main__":
    solve()
