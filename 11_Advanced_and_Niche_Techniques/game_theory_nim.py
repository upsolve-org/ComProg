"""
Game Theory: Nim and Sprague-Grundy Theorem in Python
1. Standard Nim: Winner determined by XOR sum of pile sizes
2. Sprague-Grundy values for impartial games (Mex calculation)
"""

import sys

def nim_winner(piles):
    """
    Returns 'First' if the first player has a winning strategy in standard Nim,
    or 'Second' otherwise.
    Rule: First player wins iff XOR sum of all pile sizes != 0.
    """
    xor_sum = 0
    for p in piles:
        xor_sum ^= p
    return "First" if xor_sum != 0 else "Second"

def mex(s):
    """Returns minimum excluded non-negative integer from set s."""
    m = 0
    while m in s:
        m += 1
    return m

def compute_grundy_subtraction_game(max_n, allowed_moves):
    """
    Computes Grundy values G[0 ... max_n] for a game where players can take
    x coins from the pile, where x in allowed_moves.
    """
    G = [0] * (max_n + 1)
    for i in range(1, max_n + 1):
        reachable = set()
        for move in allowed_moves:
            if i >= move:
                reachable.add(G[i - move])
        G[i] = mex(reachable)
    return G

TEST_CASES = [
    (
        "3\n3\n1 2 3\n2\n5 5\n4\n1 2 4 8",
        "Second\nSecond\nFirst"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    it = iter(tokens)
    t = int(next(it))
    out = []
    for _ in range(t):
        n = int(next(it))
        piles = [int(next(it)) for _ in range(n)]
        out.append(nim_winner(piles))
    sys.stdout.write("\n".join(out) + "\n")

if __name__ == "__main__":
    solve()
