"""
Fast I/O Patterns & Templates for Competitive Programming in Python.
"""

import sys

def fast_read_all_tokens():
    """
    Fastest approach when input size N >= 10^5.
    Reads everything into memory, splits on whitespace, and returns an iterator.
    """
    data = sys.stdin.read().split()
    return iter(data)

def fast_line_reader():
    """
    Line-by-line reading for interactive problems or when memory is constrained.
    """
    readline = sys.stdin.readline
    return readline

def write_bulk(lines):
    """
    Writes all output strings joined with newlines.
    """
    sys.stdout.write("\n".join(lines) + "\n")

# Example Test Case execution
TEST_CASES = [
    (
        "3\n5\n1 2 3 4 5\n3\n10 20 30\n1\n99",
        "15\n60\n99"
    )
]

def solve():
    iterator = fast_read_all_tokens()
    try:
        t_str = next(iterator)
    except StopIteration:
        return
    t = int(t_str)
    results = []
    for _ in range(t):
        n = int(next(iterator))
        arr = [int(next(iterator)) for _ in range(n)]
        results.append(str(sum(arr)))
    write_bulk(results)

if __name__ == "__main__":
    solve()
