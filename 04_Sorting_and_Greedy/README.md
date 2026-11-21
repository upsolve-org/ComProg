---
tags:
  - cp/algorithms
  - cp/greedy
  - cp/sorting
---

[[Home|🏠 Dashboard]] ❯ **Module 04: Sorting and Greedy Algorithms**

---

# Module 04: Sorting and Greedy Algorithms

*References from [[12_Reference_and_Catalog/codeforces_catalog_full.md|Codeforces Catalog]]:*
- [Sortings category on Codeforces](https://codeforces.com/catalog)
- [On "is this greedy or DP", forcing and rubber bands by -is-this-fft-](https://codeforces.com/blog/entry/106346)

Sorting is a prerequisite for almost half of all contest problems. Greedy algorithms make the best local choice at each step with the hope that these choices lead to a globally optimal solution.

---

## 🐍 Python Sorting Mastery

### 1. Custom Keys & Lambda
Python's Timsort (`list.sort()` or `sorted()`) is an adaptive, stable $O(N \log N)$ algorithm.
```python
# Sort by second element ascending, then first element descending
arr.sort(key=lambda x: (x[1], -x[0]))
```

### 2. Custom Comparators via `functools.cmp_to_key`
When sorting order depends on comparing two elements together (e.g. Largest Number concatenated: whether `str(a) + str(b) > str(b) + str(a)`):
```python
from functools import cmp_to_key

def custom_compare(a, b):
    # Return -1 if a < b, 1 if a > b, 0 if equal
    if str(a) + str(b) > str(b) + str(a):
        return -1
    else:
        return 1

arr.sort(key=cmp_to_key(custom_compare))
```

### 3. Coordinate Compression
Maps large coordinate values (e.g., up to $10^9$) down to compact contiguous indices $0 \dots M-1$:
```python
unique_sorted = sorted(set(coords))
compressed_map = {val: idx for idx, val in enumerate(unique_sorted)}
```

---

## 🎯 Proving Greedy: The Exchange Argument
To prove a greedy order $A$ is optimal:
1. Suppose an optimal solution differs from greedy order $A$.
2. Find the first inversion where two adjacent elements violate the greedy rule.
3. Show that swapping (exchanging) them either improves the objective or leaves it unchanged without violating constraints.
4. Conclude that by repeated swaps, the greedy solution achieves optimal value.

### Worked Example: Earliest Finish First
Sorting by start time gives `B` and `C` equal footing (both start at 2–3) and only one can be picked. Sorting by finish time puts `B` first, and after it ends at 3 the rest of the day stays free:

```python
events = [("A", 1, 6), ("B", 2, 3), ("C", 3, 5), ("D", 5, 6), ("E", 7, 9)]


def most_events(events):
    picked, last_end = [], 0
    for name, start, end in sorted(events, key=lambda e: e[2]):
        if start >= last_end:            # compatible with everything picked
            picked.append(name)
            last_end = end
    return picked


def count_from(first, events):
    rest = [e for e in events if e[0] != first[0]]
    return 1 + len(most_events([e for e in rest if e[1] >= first[2]]))


print(most_events(events), "· A first:", count_from(events[0], events))
```

The greedy answer is `['B', 'C', 'D', 'E']`, four events. Forcing `A` first (it finishes at 6) leaves only `E`, so it collects two: whichever optimal solution starts elsewhere, the earliest finisher is never worse.

---

## 📂 Included Source Files & Templates
- 🔢 [[04_Sorting_and_Greedy/sorting_and_custom_keys.py|sorting_and_custom_keys.py]] — Coordinate compression, `cmp_to_key` largest number
- ⏱️ [[04_Sorting_and_Greedy/greedy_templates.py|greedy_templates.py]] — Interval scheduling, meeting rooms sweep line
- 🎬 [[04_Sorting_and_Greedy/practice_problems.py|practice_problems.py]] — Movie Festival (classic greedy)

---

⏮️ Previous: [[03_Two_Pointers_and_Sliding_Window/README|03 Two Pointers & Sliding Window]] | 🏠 [[Home|Dashboard]] | ⏭️ Next: [[05_Data_Structures/README|05 Data Structures]]
