"""
Practice Problem: Aggressive Cows / Maximum Minimum Distance
Given N stalls at positions X[0 ... N-1] and C cows, place all C cows into stalls
such that the minimum distance between any two cows is as large as possible.

Method: Binary Search on Answer
Time Complexity: O(N log(max_dist))
"""

import sys

def can_place_cows(stalls, c, min_dist):
    """Greedily checks if we can place at least c cows with >= min_dist spacing."""
    placed = 1
    last_pos = stalls[0]
    for pos in stalls[1:]:
        if pos - last_pos >= min_dist:
            placed += 1
            last_pos = pos
            if placed >= c:
                return True
    return False

def max_min_distance(stalls, c):
    stalls.sort()
    lo = 1
    hi = stalls[-1] - stalls[0]
    best = 1
    
    while lo <= hi:
        mid = (lo + hi) // 2
        if can_place_cows(stalls, c, mid):
            best = mid
            lo = mid + 1  # Try for a larger distance
        else:
            hi = mid - 1
            
    return best

TEST_CASES = [
    (
        "5 3\n1 2 8 4 9",
        "3"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    n = int(tokens[0])
    c = int(tokens[1])
    stalls = [int(x) for x in tokens[2:2+n]]
    ans = max_min_distance(stalls, c)
    sys.stdout.write(str(ans) + "\n")

if __name__ == "__main__":
    solve()
