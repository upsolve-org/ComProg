# Python in Competitive Programming: The Ultimate Guide

Python is one of the most productive languages for competitive programming due to its concise syntax, dynamic typing, built-in arbitrary precision integers (bignums), and extensive standard library. However, competitive programming environments impose strict time limits (often 1.0 to 2.0 seconds), making it essential to understand Python's internal performance characteristics.

---

## 1. PyPy 3 vs. CPython 3

On platforms like Codeforces and AtCoder:
- **PyPy 3 (Recommended default):**
  - Includes a Just-In-Time (JIT) compiler.
  - Can execute arithmetic loops and array operations up to **10× faster** than standard CPython.
  - *When to avoid:* Highly recursive code with large frames can consume more memory and suffer overhead in PyPy.
- **CPython 3 (Fallback):**
  - Use if PyPy experiences memory limit exceeded (MLE) or unusual JIT warm-up latency.

---

## 2. Fast I/O in Python

Standard `input()` and `print()` in Python have significant overhead due to string decoding and automatic flushing.

### The Fastest I/O Pattern (Bulk Tokenization)
For problems with large input ($N \ge 10^5$), reading everything into memory at once is significantly faster:

```python
import sys

def main():
    # Read all tokens at once
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    
    it = iter(input_data)
    
    t = int(next(it))
    out = []
    for _ in range(t):
        n = int(next(it))
        # Process array
        arr = [int(next(it)) for _ in range(n)]
        
        # Collect answers in a list
        ans = sum(arr)
        out.append(str(ans))
        
    # Write everything in one pass
    sys.stdout.write("\n".join(out) + "\n")

if __name__ == "__main__":
    main()
```

### Line-by-Line Fast I/O
If inputs are stream-based or interactive:
```python
import sys
input = sys.stdin.readline
print = sys.stdout.write  # Note: requires string argument and manual "\n"
```

---

## 3. Python Performance Pitfalls & Anti-Patterns

| Anti-Pattern (Slow) | Fast Replacement | Explanation |
|---|---|---|
| `x in my_list` ($O(N)$) | `x in my_set` ($O(1)$) | Membership test on list is linear search. |
| `my_list.pop(0)` ($O(N)$) | `deque.popleft()` ($O(1)$) | Popping from the front of a list shifts all elements. |
| `s += char` in a loop ($O(N^2)$) | `chars.append(char)` then `"".join(chars)` ($O(N)$) | Strings are immutable in Python; `+=` allocates a new string. |
| `[[]] * N` | `[[] for _ in range(N)]` | `[[]] * N` duplicates references to the *same* list. |
| Deep recursion without setting limit | `sys.setrecursionlimit(300000)` | Default limit is 1,000, causing `RecursionError`. |

---

## 4. Defending Against Hash Collisions (Anti-Hacking)

In Codeforces contests, users can view your code during the contest or the hacking phase. If you use a regular `dict` or `set` with integer keys:
```python
# VULNERABLE TO HACKING
seen = set()
for x in arr:
    seen.add(x)
```
Hacker test generators construct special inputs that map to identical hash buckets in Python's internal hash table, degrading $O(1)$ lookups to $O(N)$ and causing **Time Limit Exceeded (TLE)**.

### The Safe Hash Wrapper
XOR your integer keys with a fixed pseudo-random integer:
```python
import random

# Generate a random 64-bit mask once per execution
RANDOM_MASK = random.getrandbits(31)

def safe_add(s: set, x: int):
    s.add(x ^ RANDOM_MASK)

def safe_in(s: set, x: int) -> bool:
    return (x ^ RANDOM_MASK) in s
```
Or create a custom key class or hash function.

---

## 5. Python Standard Library Gems for CP

- **`collections.deque`**: Double-ended queue for BFS, sliding windows, and monotonic queues.
- **`collections.Counter`**: Frequency map of elements.
- **`collections.defaultdict`**: Adjacency lists for graph representations without explicit key initialization.
- **`heapq`**: Binary min-heap ($O(\log N)$ push and pop). For a max-heap, multiply values by $-1$.
- **`bisect`**: Fast binary search on sorted lists (`bisect_left` for lower bound, `bisect_right` for upper bound).
- **`math.gcd` & `math.isqrt`**: Extremely fast C-implemented GCD and exact integer square root.
- **`itertools.accumulate`**: Fast prefix sums calculation.
- **`itertools.permutations` / `combinations`**: Effortless brute force generation for small $N \le 10$.
- **`functools.lru_cache(maxsize=None)`**: Automatic memoization for recursive dynamic programming.
