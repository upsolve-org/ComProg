"""
LIS and LCS Dynamic Programming in Python
1. Longest Increasing Subsequence (LIS) in O(N log N) using bisect
2. Longest Common Subsequence (LCS) in O(N * M)
"""

import sys
import bisect

def longest_increasing_subsequence_len(arr):
    """
    Finds length of LIS in O(N log N) time and O(N) space.
    tails[i] stores the smallest tail of all increasing subsequences of length i + 1 found so far.
    """
    tails = []
    for x in arr:
        idx = bisect.bisect_left(tails, x)
        if idx == len(tails):
            tails.append(x)
        else:
            tails[idx] = x
    return len(tails)

def longest_common_subsequence(s1, s2):
    """
    Returns length of LCS and reconstructed string for s1 and s2.
    Time Complexity: O(len(s1) * len(s2)).
    """
    n, m = len(s1), len(s2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    
    for i in range(n):
        for j in range(m):
            if s1[i] == s2[j]:
                dp[i + 1][j + 1] = dp[i][j] + 1
            else:
                dp[i + 1][j + 1] = max(dp[i][j + 1], dp[i + 1][j])
                
    # Reconstruct LCS
    lcs_chars = []
    i, j = n, m
    while i > 0 and j > 0:
        if s1[i - 1] == s2[j - 1]:
            lcs_chars.append(s1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
            
    return dp[n][m], "".join(reversed(lcs_chars))

TEST_CASES = [
    (
        "8\n10 9 2 5 3 7 101 18",
        "4"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    n = int(tokens[0])
    arr = [int(x) for x in tokens[1:1+n]]
    ans = longest_increasing_subsequence_len(arr)
    sys.stdout.write(str(ans) + "\n")

if __name__ == "__main__":
    solve()
