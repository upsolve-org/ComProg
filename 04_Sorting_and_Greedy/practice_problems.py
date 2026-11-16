"""
Practice Problem: Movie Festival (CSES / Codeforces)
Given starting and ending times of N movies, find the maximum number of movies
one person can watch entirely without overlap.

Method: Sort by ending times (Greedy interval scheduling)
"""

import sys

def max_movies(movies):
    movies.sort(key=lambda x: x[1])
    count = 0
    curr_end = 0
    for s, e in movies:
        if s >= curr_end:
            count += 1
            curr_end = e
    return count

TEST_CASES = [
    (
        "3\n3 5\n4 9\n5 8",
        "2"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    it = iter(tokens)
    n = int(next(it))
    movies = []
    for _ in range(n):
        s = int(next(it))
        e = int(next(it))
        movies.append((s, e))
    ans = max_movies(movies)
    sys.stdout.write(str(ans) + "\n")

if __name__ == "__main__":
    solve()
