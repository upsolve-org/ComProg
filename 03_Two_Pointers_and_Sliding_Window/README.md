---
tags:
  - cp/algorithms
  - cp/two-pointers
---

[[Home|🏠 Dashboard]] ❯ **Module 03: Two Pointers and Sliding Window**

---

# Module 03: Two Pointers and Sliding Window

*Reference from [[12_Reference_and_Catalog/codeforces_catalog_full.md|Codeforces Catalog]]:*
- [EDU: Two Pointers Method by pashka](https://codeforces.com/blog/entry/78586)

The Two Pointers method is an optimization technique that reduces quadratic $O(N^2)$ checks to linear $O(N)$ by maintaining two indices that move monotonically across the input.

---

## 🧭 Patterns & Archetypes

### 1. Inward Converging Pointers (Sorted Arrays)
- One pointer at `left = 0`, one pointer at `right = N - 1`.
- Used for finding pairs with a target sum, reversing elements, container with most water.
- In each step, if `arr[left] + arr[right] < target`, increment `left`. If `> target`, decrement `right`.

### 2. Same-Direction Pointers (Caterpillar / Sliding Window)
- Both pointers move from left to right: `left` and `right`.
- **Fixed-size window ($K$):** Expand `right` to size $K$, then slide both pointers together.
- **Variable-size window:**
  - Expand `right` to include elements until a condition is violated.
  - Shrink `left` until the condition is restored.
  - Used for "Longest subarray with sum $\le S$", "Subarrays with at most $K$ distinct elements".

---

## 💡 Python Optimization Note
When counting distinct frequencies in a sliding window, using `collections.defaultdict(int)` or an array if values are small ($V \le 10^5$) is substantially faster than deleting keys from a regular `dict`.

---

## 📂 Included Source Files & Templates
- ↔️ [[03_Two_Pointers_and_Sliding_Window/two_pointers_templates.py|two_pointers_templates.py]] — Sorted 2-Sum, array merging
- 🪟 [[03_Two_Pointers_and_Sliding_Window/sliding_window_templates.py|sliding_window_templates.py]] — Longest subarray sum $\le S$, at most $K$ distinct

---

⏮️ Previous: [[02_Binary_and_Ternary_Search/README|02 Binary & Ternary Search]] | 🏠 [[Home|Dashboard]] | ⏭️ Next: [[04_Sorting_and_Greedy/README|04 Sorting & Greedy]]
