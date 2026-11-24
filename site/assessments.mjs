// Multiple structured coding assessments per chapter, placed directly after
// each topic lesson in the learning flow, each with 6-8 comprehensive test cases
// (basic, edge, boundary, negative/zero, and multi-query cases).

const pyBase = '# Read from standard input and print your result.\nimport sys\ninput = sys.stdin.readline\n\n'
const cppBase = `#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    // Write your solution here.
    return 0;
}
`

const tc = (label, input, expected) => ({ label, input, expected: String(expected) })

export const chapterAssessments = {
  '00_getting_started': [
    {
      id: '00-sum',
      afterNote: 'python_cp_guide.md',
      afterNoteCpp: 'cpp_cp_guide.md',
      title: 'Drill 1: 64-Bit Integer Sum',
      difficulty: 'Warmup',
      labIndex: 0,
      task: 'Read two signed integers a and b on one line (−10⁹ ≤ a, b ≤ 10⁹) and print a + b. Make sure your code handles 64-bit sums and negative values cleanly.',
      cases: [
        tc('Basic positive & negative', '7 -2', '5'),
        tc('Both zero', '0 0', '0'),
        tc('Large negative sum', '-1000000000 -1000000000', '-2000000000'),
        tc('Large positive sum (overflows 32-bit)', '2000000000 2000000000', '4000000000'),
        tc('Opposite cancellation', '999999999 -999999999', '0'),
        tc('Single negative offset', '-43 42', '-1')
      ],
      hints: [
        'Parse both integers from the same line (split() in Python, long long a, b; cin >> a >> b; in C++).',
        'In C++, 2e9 + 2e9 overflows 32-bit int — always use long long.',
        'Check negative + negative and zero + zero.'
      ],
      pythonStarter: 'a, b = map(int, input().split())\n# Print a + b\n',
      cppStarter: `#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    long long a, b;
    cin >> a >> b;
    // Print a + b
}
`
    },
    {
      id: '00-multi-test',
      afterNote: 'codeforces_platform_guide.md',
      title: 'Drill 2: Multi-Test Parity Check',
      difficulty: 'Warmup',
      task: 'Read an integer t (1 ≤ t ≤ 1000), followed by t lines each containing a single integer n (1 ≤ n ≤ 10⁹). For each test case, print YES if n can be split into two positive even integers (like Codeforces 4A), or NO otherwise.',
      cases: [
        tc('Mixed small cases', '4\n8\n2\n3\n4', 'YES\nNO\nNO\nYES'),
        tc('Edge n = 1 and n = 2', '2\n1\n2', 'NO\nNO'),
        tc('Large even and odd', '2\n1000000000\n999999999', 'YES\nNO'),
        tc('Single valid case', '1\n6', 'YES'),
        tc('All odd numbers', '3\n5\n7\n9', 'NO\nNO\nNO'),
        tc('Smallest valid even (4)', '1\n4', 'YES')
      ],
      hints: [
        'Two positive even numbers are each at least 2, so their sum must be at least 4.',
        'Any even number n ≥ 4 can be split as 2 + (n - 2).',
        'Don’t forget n = 2 is even, yet 2 = 1 + 1 is NOT two even numbers!'
      ],
      pythonStarter: pyBase + 't = int(input())\nfor _ in range(t):\n    n = int(input())\n    # Print YES or NO\n',
      cppStarter: cppBase
    }
  ],

  '01_foundations_and_complexity': [
    {
      id: '01-prefix-queries',
      afterNote: 'prefix_sums_and_diff_arrays.md',
      title: 'Drill 1: Static Range Sum Queries',
      difficulty: 'Warmup',
      task: 'Read n and q, then n integers a₁..aₙ, then q lines each containing 1-based indices l and r (1 ≤ l ≤ r ≤ n). Print the sum aₗ + ... + aᵣ for each query in O(1) per query using a prefix sum array.',
      cases: [
        tc('Basic range queries', '5 3\n2 4 -1 5 3\n1 3\n2 5\n4 4', '5\n11\n5'),
        tc('Full array & single ends', '4 3\n10 20 30 40\n1 4\n1 1\n4 4', '100\n10\n40'),
        tc('All negative numbers', '3 2\n-5 -2 -8\n1 3\n2 3', '-15\n-10'),
        tc('64-bit sums', '3 1\n1000000000 1000000000 1000000000\n1 3', '3000000000'),
        tc('Zero-sum cancellation', '4 2\n5 -5 5 -5\n1 4\n2 3', '0\n0'),
        tc('Single element array', '1 2\n42\n1 1\n1 1', '42\n42')
      ],
      hints: [
        'Build pref of size n + 1 with pref[0] = 0 and pref[i] = pref[i - 1] + a[i - 1].',
        'The 1-based inclusive sum from l to r is simply pref[r] - pref[l - 1].',
        'Use 64-bit integers (long long in C++) for the prefix array.'
      ],
      pythonStarter: pyBase + 'n, q = map(int, input().split())\na = list(map(int, input().split()))\n',
      cppStarter: cppBase
    },
    {
      id: '01-diff-array',
      afterNote: 'prefix_sums_and_diff_arrays.md',
      title: 'Drill 2: Range Add via Difference Array',
      difficulty: 'Core',
      task: 'Start with an array of n zeros (1 ≤ n ≤ 200,000). Read n and q, followed by q updates (l, r, v) adding v to every index in [l, r] (1-based). Print the final array separated by spaces in O(n + q) time.',
      cases: [
        tc('Overlapping range adds', '5 3\n1 3 2\n2 5 3\n3 3 -1', '2 5 4 3 3'),
        tc('Full range update', '4 1\n1 4 7', '7 7 7 7'),
        tc('Zero updates', '3 0', '0 0 0'),
        tc('Cancelling updates', '4 2\n1 4 5\n1 4 -5', '0 0 0 0'),
        tc('Point updates at boundaries', '4 2\n1 1 9\n4 4 -4', '9 0 0 -4'),
        tc('Single element multiple adds', '1 3\n1 1 10\n1 1 -3\n1 1 5', '12')
      ],
      hints: [
        'Create diff of size n + 2 initialized to 0.',
        'For each update (l, r, v), do diff[l] += v and diff[r + 1] -= v.',
        'Take a running prefix sum of diff[1..n] to reconstruct the final array.'
      ],
      pythonStarter: pyBase + 'n, q = map(int, input().split())\ndiff = [0] * (n + 2)\n',
      cppStarter: cppBase
    },
    {
      id: '01-kadane',
      afterNote: 'end',
      title: 'Capstone: Maximum Subarray Sum',
      difficulty: 'Core',
      labIndex: 1,
      task: 'Read n (1 ≤ n ≤ 10⁶), then n integers in [−10⁹, 10⁹] on the next line. Print the largest sum of any non-empty contiguous subarray in O(n) time.',
      cases: [
        tc('Classic mixed array', '9\n-2 1 -3 4 -1 2 1 -5 4', '6'),
        tc('All negative values', '5\n-1 -2 -3 -4 -5', '-1'),
        tc('Negative with middle peak', '3\n-5 -2 -3', '-2'),
        tc('Bridge across negative dip', '3\n2 -1 2', '3'),
        tc('64-bit overflow check', '4\n1000000000 1000000000 1000000000 1000000000', '4000000000'),
        tc('Single negative element', '1\n-8', '-8'),
        tc('All zeros', '3\n0 0 0', '0')
      ],
      hints: [
        'Maintain cur = max(x, cur + x) and best = max(best, cur).',
        'Initialize cur and best to the first element (not 0!) so all-negative arrays work.',
        'Use long long in C++.'
      ],
      pythonStarter: pyBase + 'n = int(input())\na = list(map(int, input().split()))\n',
      cppStarter: cppBase
    }
  ],

  '02_binary_and_ternary_search': [
    {
      id: '02-lower-bound',
      afterNote: 'binary_search_templates.md',
      title: 'Drill 1: First Element At Least X',
      difficulty: 'Warmup',
      labIndex: 2,
      task: 'Read n and q, followed by n sorted integers and q query values. For each query x, print the zero-based index of the first value ≥ x, or −1 if none exists (one per line).',
      cases: [
        tc('Duplicates & bounds', '5 3\n1 4 4 6 8\n4 5 0', '1\n3\n0'),
        tc('Single element hit & miss', '1 2\n3\n3 4', '0\n-1'),
        tc('Query above maximum', '3 1\n1 2 4\n5', '-1'),
        tc('Negative sorted values', '4 5\n-2 -2 0 7\n-3 -2 -1 7 8', '0\n0\n2\n3\n-1'),
        tc('All identical values', '4 3\n5 5 5 5\n4 5 6', '0\n0\n-1'),
        tc('Exact last element', '4 1\n2 4 6 8\n8', '3')
      ],
      hints: [
        'Search over [0, n) with invariant: answer is in [lo, hi].',
        'If a[mid] >= x, set hi = mid; otherwise set lo = mid + 1.',
        'If lo == n at the end, print -1.'
      ],
      pythonStarter: pyBase + 'n, q = map(int, input().split())\na = list(map(int, input().split()))\nqueries = list(map(int, input().split()))\n',
      cppStarter: cppBase
    },
    {
      id: '02-bs-answer',
      afterNote: 'binary_search_templates.md',
      title: 'Drill 2: Binary Search on the Answer (Cutting Ribbons)',
      difficulty: 'Core',
      task: 'Read n and k (1 ≤ n ≤ 10⁵, 1 ≤ k ≤ 10⁹), then n integer wood lengths aᵢ (1 ≤ aᵢ ≤ 10⁹). Find the maximum integer length L ≥ 0 such that you can cut at least k pieces of length L from the planks.',
      cases: [
        tc('Standard cut', '4 7\n8 5 7 9', '3'),
        tc('Exact single plank', '1 3\n10', '3'),
        tc('Not enough total wood (L = 0)', '2 10\n3 4', '0'),
        tc('Large lengths', '3 5\n1000000000 1000000000 1000000000', '500000000'),
        tc('k equals sum of all lengths', '3 6\n2 2 2', '1'),
        tc('Single huge piece needed', '4 1\n3 9 2 7', '9')
      ],
      hints: [
        'For a candidate length L > 0, the number of pieces is sum(x // L for x in a).',
        'If pieces(L) >= k is True, any smaller length is also True — binary search for the last True!',
        'Handle L = 0 cleanly by setting lo = 0, hi = max(a) and checking mid = (lo + hi + 1) // 2.'
      ],
      pythonStarter: pyBase + 'n, k = map(int, input().split())\na = list(map(int, input().split()))\n',
      cppStarter: cppBase
    },
    {
      id: '02-ternary-peak',
      afterNote: 'ternary_search.md',
      title: 'Drill 3: Unimodal Peak Index',
      difficulty: 'Core',
      task: 'Read n (3 ≤ n ≤ 200,000), then a strictly unimodal array a₀..aₙ₋₁ (strictly increasing up to a unique peak, then strictly decreasing). Print the 0-based index of the peak in O(log n) time.',
      cases: [
        tc('Peak in the middle', '5\n1 3 7 5 2', '2'),
        tc('Peak near left', '4\n1 9 6 2', '1'),
        tc('Peak near right', '4\n-5 -2 4 1', '2'),
        tc('Minimum length 3', '3\n0 10 0', '1'),
        tc('Negative unimodal values', '5\n-100 -50 -10 -20 -80', '2'),
        tc('Longer mountain', '7\n2 4 8 15 23 19 3', '4')
      ],
      hints: [
        'Compare a[m1] and a[m2] with m1 = lo + (hi - lo) // 3 and m2 = hi - (hi - lo) // 3 (or compare a[mid] vs a[mid + 1]).',
        'When a[m1] < a[m2], the peak cannot be in [lo, m1], so set lo = m1 + 1.',
        'Shrink until hi - lo <= 2, then take the argmax of the remaining 2–3 indices.'
      ],
      pythonStarter: pyBase + 'n = int(input())\na = list(map(int, input().split()))\n',
      cppStarter: cppBase
    }
  ],

  '03_two_pointers_and_sliding_windows': [
    {
      id: '03-two-sum-sorted',
      afterNote: 'two_pointers_templates.md',
      title: 'Drill 1: Two-Sum on a Sorted Array',
      difficulty: 'Warmup',
      task: 'Read n and target (2 ≤ n ≤ 200,000), then n sorted integers a₁..aₙ. Find if two distinct indices i < j satisfy aᵢ + aⱼ = target. Print "i j" (1-based, smallest i if multiple) or "-1" if no pair exists.',
      cases: [
        tc('Standard pair found', '5 9\n1 2 4 7 11', '2 4'),
        tc('No pair exists', '4 10\n1 2 3 5', '-1'),
        tc('Duplicate values forming target', '4 8\n2 4 4 9', '2 3'),
        tc('Negative & positive cancellation', '5 0\n-7 -3 1 3 8', '2 4'),
        tc('Ends of array', '3 10\n1 5 9', '1 3'),
        tc('Two elements only', '2 5\n2 3', '1 2')
      ],
      hints: [
        'Place L = 0 and R = n - 1.',
        'If a[L] + a[R] < target, increment L; if > target, decrement R.',
        'When a[L] + a[R] == target, print L + 1 and R + 1 immediately.'
      ],
      pythonStarter: pyBase + 'n, target = map(int, input().split())\na = list(map(int, input().split()))\n',
      cppStarter: cppBase
    },
    {
      id: '03-fixed-window',
      afterNote: 'sliding_window_templates.md',
      title: 'Drill 2: Best Fixed-Length Window',
      difficulty: 'Core',
      labIndex: 3,
      task: 'Read n and k (1 ≤ k ≤ n ≤ 200,000), then n signed integers. Print the maximum sum of any contiguous window of length exactly k in O(n) time.',
      cases: [
        tc('Standard mixed array', '5 3\n2 -1 4 3 -2', '6'),
        tc('All negative values', '3 2\n-5 -2 -1', '-3'),
        tc('Window equals full array', '2 2\n7 -4', '3'),
        tc('Window of size 1', '5 1\n-5 8 3 8 -5', '8'),
        tc('Best window at the end', '4 3\n-2 -3 -4 1', '-6'),
        tc('64-bit sums', '4 2\n1000000000 1000000000 -5 1000000000', '2000000000')
      ],
      hints: [
        'Compute the sum of the first k elements.',
        'For i from k to n - 1, add a[i] and subtract a[i - k].',
        'Track the maximum window sum across all positions.'
      ],
      pythonStarter: pyBase + 'n, k = map(int, input().split())\na = list(map(int, input().split()))\n',
      cppStarter: cppBase
    },
    {
      id: '03-var-window',
      afterNote: 'end',
      title: 'Capstone: Longest Subarray Within Budget',
      difficulty: 'Core',
      task: 'Read n and budget T (1 ≤ n ≤ 200,000, 0 ≤ T ≤ 10¹²), then n non-negative integers aᵢ. Print the length of the longest contiguous subarray whose sum is ≤ T.',
      cases: [
        tc('Standard books example', '4 5\n3 1 2 1', '3'),
        tc('Every element exceeds budget', '3 2\n5 6 7', '0'),
        tc('Entire array fits', '4 20\n4 3 5 2', '4'),
        tc('Zero budget with zeros in array', '5 0\n1 0 0 2 0', '2'),
        tc('Single element fits', '3 4\n5 4 5', '1'),
        tc('Best window at the very end', '6 6\n5 5 2 2 1 1', '4')
      ],
      hints: [
        'Because all elements are non-negative, expanding R increases the sum and advancing L decreases it.',
        'For each R, add a[R], then while cur > T subtract a[L] and increment L.',
        'Update ans = max(ans, R - L + 1).'
      ],
      pythonStarter: pyBase + 'n, T = map(int, input().split())\na = list(map(int, input().split()))\n',
      cppStarter: cppBase
    }
  ],

  '04_sorting_and_greedy': [
    {
      id: '04-coord-compress',
      afterNote: 'sorting_and_custom_keys.md',
      title: 'Drill 1: Coordinate Compression Ranks',
      difficulty: 'Warmup',
      task: 'Read n (1 ≤ n ≤ 200,000), then n integers (possibly huge or negative). Replace each element with its 0-based rank among the sorted distinct values and print the result separated by spaces.',
      cases: [
        tc('Sparse positive values', '5\n10 1000000000 42 1000000000 5', '1 3 2 3 0'),
        tc('Negative & positive', '4\n-100 0 -100 50', '0 1 0 2'),
        tc('All equal elements', '3\n7 7 7', '0 0 0'),
        tc('Already sorted distinct', '4\n1 2 3 4', '0 1 2 3'),
        tc('Reverse sorted', '4\n9 6 3 1', '3 2 1 0'),
        tc('Single element', '1\n-999999999', '0')
      ],
      hints: [
        'Extract sorted unique values: uniq = sorted(set(a)).',
        'Map each unique value to its index: rank = {v: i for i, v in enumerate(uniq)}.',
        'In C++, use sort + unique + lower_bound.'
      ],
      pythonStarter: pyBase + 'n = int(input())\na = list(map(int, input().split()))\n',
      cppStarter: cppBase
    },
    {
      id: '04-events',
      afterNote: 'greedy_templates.md',
      title: 'Capstone: Attend the Most Events',
      difficulty: 'Core',
      labIndex: 4,
      task: 'Read n (1 ≤ n ≤ 200,000), then n lines with start and end times (start < end). Print the maximum number of non-overlapping events one person can attend. An event may start when the previous one ends.',
      cases: [
        tc('Standard greedy choice', '4\n1 5\n2 3\n3 4\n4 6', '3'),
        tc('All share same finish', '3\n1 5\n2 5\n3 5', '1'),
        tc('Unsorted touching intervals', '3\n4 6\n1 2\n2 4', '3'),
        tc('Long span wrapping three short ones', '4\n0 7\n1 2\n2 3\n3 4', '3'),
        tc('Negative timestamps', '3\n-5 -2\n-3 0\n0 1', '2'),
        tc('Single event', '1\n10 20', '1')
      ],
      hints: [
        'Sort intervals by end time ascending.',
        'Track last_end = -infinity; whenever start >= last_end, attend the event and set last_end = end.',
        'By the exchange argument, finishing earlier never reduces future options.'
      ],
      pythonStarter: pyBase + 'n = int(input())\nevents = [tuple(map(int, input().split())) for _ in range(n)]\n',
      cppStarter: cppBase
    }
  ],

  '05_data_structures': [
    {
      id: '05-dsu-groups',
      afterNote: 'dsu_disjoint_set_union.md',
      title: 'Drill 1: Track Connected Groups (DSU)',
      difficulty: 'Core',
      labIndex: 5,
      task: 'Read n and q, then q lines with two people u and v (1..n) to connect. Print the number of connected groups after each connection, one per line.',
      cases: [
        tc('Gradual full merge', '4 4\n1 2\n3 4\n2 3\n1 4', '3\n2\n1\n1'),
        tc('Self loops on n = 1', '1 2\n1 1\n1 1', '1\n1'),
        tc('Repeated edge', '3 2\n2 3\n3 2', '2\n2'),
        tc('Redundant & self loops', '4 5\n1 1\n2 1\n1 2\n3 4\n2 4', '4\n3\n3\n2\n1'),
        tc('Star graph', '5 4\n1 2\n1 3\n1 4\n1 5', '4\n3\n2\n1'),
        tc('No merges decrease below 2', '4 2\n1 2\n3 4', '3\n2')
      ],
      hints: [
        'Initialize parent[i] = i, size[i] = 1, components = n.',
        'Use path compression in find(x) and union by size.',
        'Only decrement components when find(u) != find(v).'
      ],
      pythonStarter: pyBase + 'n, q = map(int, input().split())\n',
      cppStarter: cppBase
    },
    {
      id: '05-bit-sum',
      afterNote: 'fenwick_tree.md',
      title: 'Drill 2: Dynamic Point Update & Range Sum (BIT)',
      difficulty: 'Core',
      task: 'Read n and q, then n integers a₁..aₙ, followed by q queries: "1 i v" adds v to aᵢ; "2 l r" prints the sum of a[l..r] (1-based). Aim for O(log n) per query.',
      cases: [
        tc('Updates and range queries', '5 4\n1 2 3 4 5\n2 1 5\n1 3 10\n2 2 4\n2 1 5', '15\n19\n25'),
        tc('Negative delta updates', '3 3\n5 5 5\n1 2 -10\n2 1 3\n2 2 2', '5\n-5'),
        tc('Single element updates', '1 3\n4\n2 1 1\n1 1 6\n2 1 1', '4\n10'),
        tc('64-bit sums', '2 2\n1000000000 1000000000\n1 1 1000000000\n2 1 2', '3000000000'),
        tc('Multiple updates before query', '4 4\n0 0 0 0\n1 1 3\n1 4 7\n2 1 4\n2 2 3', '10\n0'),
        tc('Boundary indices', '4 2\n1 2 3 4\n2 1 1\n2 4 4', '1\n4')
      ],
      hints: [
        'Use a 1-indexed Fenwick Tree (BIT): update climbs with i += i & -i, query descends with i -= i & -i.',
        'Range sum [l, r] is query(r) - query(l - 1).',
        'Initialize the BIT by adding each initial a[i] at index i.'
      ],
      pythonStarter: pyBase + 'n, q = map(int, input().split())\na = list(map(int, input().split()))\n',
      cppStarter: cppBase
    },
    {
      id: '05-mono-nge',
      afterNote: 'monotonic_stack_and_queue.md',
      title: 'Drill 3: Next Greater Element (Monotonic Stack)',
      difficulty: 'Core',
      task: 'Read n (1 ≤ n ≤ 200,000), then n integers a₀..aₙ₋₁. For each index i, print the first value strictly greater than aᵢ to its right, or −1 if none exists. Print n space-separated answers.',
      cases: [
        tc('Standard mixed array', '5\n2 1 5 3 6', '5 5 6 6 -1'),
        tc('Strictly decreasing', '4\n9 7 4 1', '-1 -1 -1 -1'),
        tc('Strictly increasing', '4\n1 2 3 4', '2 3 4 -1'),
        tc('Duplicates require strictly greater', '4\n3 3 3 4', '4 4 4 -1'),
        tc('Single element', '1\n42', '-1'),
        tc('Negative values', '4\n-5 -2 -8 -1', '-2 -1 -1 -1')
      ],
      hints: [
        'Maintain a stack of indices whose next greater element has not been found yet (values stay decreasing).',
        'When a[i] > a[stack[-1]], pop idx and set ans[idx] = a[i].',
        'Every index is pushed once and popped at most once -> O(n).'
      ],
      pythonStarter: pyBase + 'n = int(input())\na = list(map(int, input().split()))\n',
      cppStarter: cppBase
    }
  ],

  '06_dynamic_programming': [
    {
      id: '06-knapsack',
      afterNote: '01_knapsack_and_subsets.md',
      title: 'Drill 1: 0/1 Knapsack Maximum Value',
      difficulty: 'Core',
      task: 'Read n items and capacity W (1 ≤ n ≤ 100, 1 ≤ W ≤ 10,000), followed by n lines with weight wᵢ and value vᵢ. Each item can be chosen at most once. Print the maximum total value fitting in capacity W.',
      cases: [
        tc('Classic 3 items', '3 8\n3 30\n4 50\n5 60', '90'),
        tc('No item fits', '2 3\n4 10\n5 20', '0'),
        tc('All items fit', '3 10\n2 5\n3 7\n4 8', '20'),
        tc('Exact capacity trade-off', '4 7\n1 1\n3 4\n4 5\n5 7', '9'),
        tc('Single item fits', '1 5\n5 42', '42'),
        tc('Duplicate weights', '3 4\n2 10\n2 15\n2 20', '35')
      ],
      hints: [
        'Use a 1D array dp[0..W] initialized to 0.',
        'For each item (w, v), iterate cap from W DOWN to w so each item is used at most once.',
        'Transition: dp[cap] = max(dp[cap], dp[cap - w] + v).'
      ],
      pythonStarter: pyBase + 'n, W = map(int, input().split())\nitems = [tuple(map(int, input().split())) for _ in range(n)]\n',
      cppStarter: cppBase
    },
    {
      id: '06-grid-paths',
      afterNote: 'grid_and_paths_dp.md',
      title: 'Drill 2: Count Open Grid Paths',
      difficulty: 'Core',
      labIndex: 6,
      task: 'Read h and w (1 ≤ h, w ≤ 100), then h rows of "." (open) and "#" (wall). Count paths from top-left to bottom-right moving only right or down, modulo 1,000,000,007.',
      cases: [
        tc('Center wall', '3 3\n...\n.#.\n...', '2'),
        tc('Single open cell', '1 1\n.', '1'),
        tc('Blocked start', '1 2\n#.', '0'),
        tc('Blocked finish', '2 2\n..\n.#', '0'),
        tc('Wall barrier splits grid', '3 3\n.#.\n###\n.#.', '0'),
        tc('Open 3x4 grid', '3 4\n....\n....\n....', '10')
      ],
      hints: [
        'If grid[0][0] == "#", answer is 0 immediately.',
        'For each open cell (r, c), dp[r][c] = (dp[r-1][c] + dp[r][c-1]) % MOD.',
        'Set dp[r][c] = 0 whenever grid[r][c] == "#".'
      ],
      pythonStarter: pyBase + 'MOD = 10**9 + 7\nh, w = map(int, input().split())\ngrid = [input().strip() for _ in range(h)]\n',
      cppStarter: cppBase
    },
    {
      id: '06-lis',
      afterNote: 'lis_and_lcs.md',
      title: 'Drill 3: Longest Strictly Increasing Subsequence (O(n log n))',
      difficulty: 'Challenge',
      task: 'Read n (1 ≤ n ≤ 200,000), then n integers. Print the length of the longest strictly increasing subsequence.',
      cases: [
        tc('Classic LIS', '8\n10 9 2 5 3 7 101 18', '4'),
        tc('Strictly decreasing', '5\n5 4 3 2 1', '1'),
        tc('All equal (strictly increasing!)', '4\n7 7 7 7', '1'),
        tc('Already increasing', '5\n1 2 3 4 5', '5'),
        tc('Negative & positive', '6\n-5 -2 -3 0 4 2', '4'),
        tc('Single element', '1\n99', '1')
      ],
      hints: [
        'Maintain tails where tails[k] is the smallest ending value of an increasing subsequence of length k + 1.',
        'For each x, find idx = bisect_left(tails, x) (lower_bound in C++).',
        'If idx == len(tails), append x; else set tails[idx] = x.'
      ],
      pythonStarter: pyBase + 'from bisect import bisect_left\nn = int(input())\na = list(map(int, input().split()))\n',
      cppStarter: cppBase
    }
  ],

  '07_graph_algorithms': [
    {
      id: '07-bfs-shortest',
      afterNote: 'graph_traversal_bfs_dfs.md',
      title: 'Drill 1: Shortest Unweighted Route (BFS)',
      difficulty: 'Core',
      labIndex: 7,
      task: 'Read n and m, then m undirected edges between vertices 1..n. Print the minimum number of edges from 1 to n, or −1 if unreachable.',
      cases: [
        tc('Two routes, pick shorter', '5 5\n1 2\n2 3\n3 5\n1 4\n4 5', '2'),
        tc('Disconnected target', '4 1\n1 2', '-1'),
        tc('Trivial n = 1', '1 0', '0'),
        tc('Cycle without path to n', '5 5\n1 2\n2 3\n3 1\n4 5\n1 2', '-1'),
        tc('Direct edge 1-n', '4 2\n1 4\n2 3', '1'),
        tc('Linear chain', '4 3\n1 2\n2 3\n3 4', '3')
      ],
      hints: [
        'Use a FIFO queue (collections.deque in Python, std::queue in C++).',
        'Initialize dist[1] = 0 and all others to -1; mark dist[v] = dist[u] + 1 BEFORE pushing v.',
        'Print dist[n].'
      ],
      pythonStarter: pyBase + 'from collections import deque\nn, m = map(int, input().split())\n',
      cppStarter: cppBase
    },
    {
      id: '07-topo-sort',
      afterNote: 'topological_sort.md',
      title: 'Drill 2: Lexicographically Smallest Topological Order',
      difficulty: 'Core',
      task: 'Read n and m, then m directed edges u → v (1..n). Print the lexicographically smallest topological ordering separated by spaces, or "-1" if the graph contains a cycle.',
      cases: [
        tc('DAG with tie-breaking', '4 2\n4 2\n3 1', '3 1 4 2'),
        tc('Simple directed cycle', '3 3\n1 2\n2 3\n3 1', '-1'),
        tc('No edges (sorted 1..n)', '4 0', '1 2 3 4'),
        tc('Chain reversed', '3 2\n3 2\n2 1', '3 2 1'),
        tc('Diamond DAG', '4 4\n1 3\n1 2\n2 4\n3 4', '1 2 3 4'),
        tc('Self loop cycle', '2 1\n1 1', '-1')
      ],
      hints: [
        'Compute indegree[v] for every vertex and push all 0-indegree vertices into a min-heap (heapq / priority_queue with greater<>).',
        'Pop the smallest vertex, append to order, and decrement indegree of its neighbors.',
        'If len(order) < n at the end, there is a cycle -> print -1.'
      ],
      pythonStarter: pyBase + 'import heapq\nn, m = map(int, input().split())\n',
      cppStarter: cppBase
    },
    {
      id: '07-dijkstra',
      afterNote: 'shortest_path_dijkstra.md',
      title: 'Drill 3: Weighted Shortest Path (Dijkstra)',
      difficulty: 'Challenge',
      task: 'Read n and m, then m directed weighted edges (u, v, w) with 1 ≤ w ≤ 10⁹. Print the minimum total weight from vertex 1 to vertex n, or −1 if unreachable.',
      cases: [
        tc('Classic relaxation', '5 6\n1 2 2\n1 3 5\n2 3 1\n2 4 4\n3 5 2\n4 5 1', '5'),
        tc('Unreachable target', '3 1\n1 2 10', '-1'),
        tc('64-bit path weights', '3 2\n1 2 1000000000\n2 3 1000000000', '2000000000'),
        tc('Multiple edges between same pair', '2 3\n1 2 10\n1 2 3\n1 2 7', '3'),
        tc('Single node', '1 0', '0'),
        tc('Longer hop count but lighter weight', '4 4\n1 4 100\n1 2 1\n2 3 1\n3 4 1', '3')
      ],
      hints: [
        'Push (0, 1) into a min-heap; skip popped entries with d > dist[u].',
        'Relax each outgoing edge (v, w): if d + w < dist[v], update dist[v] and push (dist[v], v).',
        'Use 64-bit INF (e.g. 10**18) for distances.'
      ],
      pythonStarter: pyBase + 'import heapq\nn, m = map(int, input().split())\n',
      cppStarter: cppBase
    }
  ],

  '08_trees_and_lca': [
    {
      id: '08-descendants',
      afterNote: 'tree_basics_and_euler_tour.md',
      title: 'Drill 1: Count Subtree Descendants',
      difficulty: 'Core',
      labIndex: 8,
      task: 'Read n (1 ≤ n ≤ 200,000), then the parent of each vertex 2..n in order (root is 1). Print the number of proper descendants of each vertex 1..n separated by spaces.',
      cases: [
        tc('Branching tree', '5\n1 1 3 3', '4 0 2 0 0'),
        tc('Single root', '1', '0'),
        tc('Child label smaller than parent', '4\n4 1 1', '3 0 0 1'),
        tc('Non-monotonic labels', '6\n1 5 5 2 2', '5 4 0 0 2 0'),
        tc('Line chain', '4\n1 2 3', '3 2 1 0'),
        tc('Star tree', '5\n1 1 1 1', '4 0 0 0 0')
      ],
      hints: [
        'Build an adjacency list of children for each node (a child can have a smaller ID than its parent!).',
        'Run an iterative BFS/DFS from root 1 to record visit order, then accumulate sub[parent] += sub[u] + 1 in reverse order.',
        'Iterative traversal avoids recursion-depth errors on chains of length 200,000.'
      ],
      pythonStarter: pyBase + 'n = int(input())\nparents = list(map(int, input().split())) if n > 1 else []\n',
      cppStarter: cppBase
    },
    {
      id: '08-kth-ancestor',
      afterNote: 'binary_lifting_lca.md',
      title: 'Drill 2: K-th Ancestor Queries (Binary Lifting)',
      difficulty: 'Challenge',
      task: 'Read n and q, then the parent of each vertex 2..n (root is 1), followed by q lines of (u, k). For each query, print the k-th ancestor of u, or −1 if u has fewer than k ancestors.',
      cases: [
        tc('Basic lifting jumps', '5 4\n1 2 3 4\n5 2\n5 4\n5 5\n3 1', '3\n1\n-1\n2'),
        tc('k = 0 returns self', '3 2\n1 1\n2 0\n1 0', '2\n1'),
        tc('Root has no ancestors', '3 2\n1 2\n1 1\n3 2', '-1\n1'),
        tc('Branching tree', '6 3\n1 1 2 2 3\n5 2\n6 2\n4 3', '1\n1\n-1'),
        tc('Single node', '1 2\n1 0\n1 1', '1\n-1'),
        tc('Power-of-two jump (k=4)', '6 1\n1 2 3 4 5\n6 4', '2')
      ],
      hints: [
        'Precompute up[j][u] = 2^j-th ancestor of u using up[j][u] = up[j-1][up[j-1][u]] (0 when none).',
        'For query (u, k), iterate bits j: if (k >> j) & 1, set u = up[j][u].',
        'If u becomes 0, return -1.'
      ],
      pythonStarter: pyBase + 'n, q = map(int, input().split())\nparents = list(map(int, input().split())) if n > 1 else []\n',
      cppStarter: cppBase
    }
  ],

  '09_mathematics_and_number_theory': [
    {
      id: '09-coprime',
      afterNote: 'gcd_extended_euclidean.md',
      title: 'Drill 1: Count Coprime Values (GCD)',
      difficulty: 'Warmup',
      labIndex: 9,
      task: 'Read n and k (1 ≤ n ≤ 200,000, 1 ≤ k ≤ 10⁹), then n integers in [1, 10⁹]. Print how many of them satisfy gcd(aᵢ, k) = 1.',
      cases: [
        tc('Standard mix', '5 12\n1 5 6 7 18', '3'),
        tc('k = 1 (all coprime)', '3 1\n1 4 10', '3'),
        tc('None coprime', '3 30\n2 3 5', '0'),
        tc('Composite k', '4 18\n1 9 25 35', '3'),
        tc('Large primes', '3 996983051\n999983 997 2', '1'),
        tc('Single element equal to k', '1 7\n7', '0')
      ],
      hints: [
        'Use math.gcd in Python or std::gcd in C++ (<numeric>).',
        'Count elements where gcd(x, k) == 1.',
        'gcd(1, k) is always 1.'
      ],
      pythonStarter: pyBase + 'from math import gcd\nn, k = map(int, input().split())\na = list(map(int, input().split()))\n',
      cppStarter: cppBase
    },
    {
      id: '09-sieve',
      afterNote: 'primes_and_sieve.md',
      title: 'Drill 2: Count Primes Up To N (Sieve)',
      difficulty: 'Core',
      task: 'Read an integer n (1 ≤ n ≤ 1,000,000). Print the number of prime numbers p with 2 ≤ p ≤ n using the Sieve of Eratosthenes.',
      cases: [
        tc('n = 10 (2, 3, 5, 7)', '10', '4'),
        tc('n = 1 (no primes)', '1', '0'),
        tc('n = 2 (first prime)', '2', '1'),
        tc('n = 100', '100', '25'),
        tc('n = 1000', '1000', '168'),
        tc('n = 100000', '100000', '9592')
      ],
      hints: [
        'Create a boolean array is_prime of size n + 1 initialized to True; mark 0 and 1 False.',
        'For p from 2 up to int(n ** 0.5), if is_prime[p], mark multiples starting from p * p.',
        'Sum is_prime.'
      ],
      pythonStarter: pyBase + 'n = int(input())\n',
      cppStarter: cppBase
    },
    {
      id: '09-modpow',
      afterNote: 'modular_arithmetic_and_combinatorics.md',
      title: 'Drill 3: Fast Modular Exponentiation',
      difficulty: 'Core',
      task: 'Read t (1 ≤ t ≤ 10,000), followed by t lines of (a, b) with 0 ≤ a, b ≤ 10¹⁸. Print aᵇ mod 1,000,000,007 for each query (define 0⁰ = 1).',
      cases: [
        tc('Standard powers', '3\n2 10\n3 4\n5 0', '1024\n81\n1'),
        tc('Zero base cases', '2\n0 0\n0 5', '1\n0'),
        tc('Large exponent mod reduction', '2\n2 1000000006\n1000000000 1000000000', '1\n140625001'),
        tc('Base larger than MOD', '1\n1000000008 1000000000000', '1'),
        tc('Single power of 1', '1\n1 999999999999', '1'),
        tc('Mod boundary', '1\n1000000007 5', '0')
      ],
      hints: [
        'Binary exponentiation squares the base and multiplies into res whenever b & 1.',
        'Reduce base %= MOD before looping (especially in C++ where a * a overflows long long if a >= MOD!).',
        'Python’s built-in pow(a, b, MOD) implements binary exponentiation natively in C.'
      ],
      pythonStarter: pyBase + 'MOD = 10**9 + 7\nt = int(input())\n',
      cppStarter: cppBase
    }
  ],

  '10_string_algorithms': [
    {
      id: '10-kmp-count',
      afterNote: 'kmp_prefix_function.md',
      title: 'Drill 1: Count Pattern Occurrences (KMP)',
      difficulty: 'Core',
      labIndex: 10,
      task: 'Read text T and pattern P on two non-empty lines of lowercase letters (length ≤ 200,000). Print how many times P occurs in T, including overlapping occurrences, in O(|T| + |P|) time.',
      cases: [
        tc('Overlapping matches', 'aaaa\naa', '3'),
        tc('Banana overlap', 'banana\nana', '2'),
        tc('Pattern longer than text', 'ab\nabc', '0'),
        tc('Exact full match', 'xyz\nxyz', '1'),
        tc('Periodic overlap', 'abababab\nabab', '3'),
        tc('No match at all', 'abcdef\nghi', '0')
      ],
      hints: [
        'Compute the KMP prefix function pi on P + "#" + T.',
        'Every position where pi[i] == len(P) is an occurrence of P.',
        'Because "#" never appears in lowercase letters, pi[i] never exceeds len(P).'
      ],
      pythonStarter: pyBase + 'text = input().strip()\npattern = input().strip()\n',
      cppStarter: cppBase
    },
    {
      id: '10-z-borders',
      afterNote: 'z_algorithm.md',
      title: 'Drill 2: Longest Proper Prefix-Suffix Border',
      difficulty: 'Core',
      task: 'Read a non-empty lowercase string s (length ≤ 200,000). Print the length of the longest proper prefix of s that is also a suffix of s (or 0 if none exists).',
      cases: [
        tc('Classic border', 'abacaba', '3'),
        tc('Periodic string', 'ababab', '4'),
        tc('No border', 'abcdef', '0'),
        tc('All identical', 'aaaaa', '4'),
        tc('Single character', 'z', '0'),
        tc('Two equal halves', 'abcabc', '3')
      ],
      hints: [
        'This is literally pi[n - 1] from the KMP prefix function — or the largest Z[i] with i + Z[i] == n!',
        'Make sure the prefix is PROPER (length < n).',
        'Both KMP and Z-algorithm run in O(n).'
      ],
      pythonStarter: pyBase + 's = input().strip()\n',
      cppStarter: cppBase
    }
  ],

  '11_advanced_techniques': [
    {
      id: '11-constructive',
      afterNote: 'constructive_algorithms.md',
      title: 'Drill 1: No-Adjacent-Difference-1 Permutation',
      difficulty: 'Core',
      task: 'Read n (1 ≤ n ≤ 100,000). Print any permutation of 1..n where no two adjacent elements differ by 1, OR print "NO SOLUTION" if impossible. (For deterministic testing, print all even numbers ascending followed by all odd numbers ascending.)',
      cases: [
        tc('n = 5 (evens then odds)', '5', '2 4 1 3 5'),
        tc('n = 4 (evens then odds)', '4', '2 4 1 3'),
        tc('n = 1 (trivial)', '1', '1'),
        tc('n = 2 (impossible)', '2', 'NO SOLUTION'),
        tc('n = 3 (impossible)', '3', 'NO SOLUTION'),
        tc('n = 6 (evens then odds)', '6', '2 4 6 1 3 5')
      ],
      hints: [
        'For n = 2 or n = 3, no valid permutation exists.',
        'For n = 1, print 1.',
        'For n >= 4, printing 2, 4, ..., then 1, 3, ... guarantees every adjacent gap is ≥ 2!'
      ],
      pythonStarter: pyBase + 'n = int(input())\n',
      cppStarter: cppBase
    },
    {
      id: '11-nim',
      afterNote: 'game_theory_nim.md',
      title: 'Capstone: Decide a Nim Game',
      difficulty: 'Core',
      labIndex: 11,
      task: 'Read n (1 ≤ n ≤ 200,000), then n pile sizes in [0, 10⁹]. Players alternate removing a positive number of stones from one pile. Print First if the first player can force a win, or Second otherwise.',
      cases: [
        tc('XOR = 0 (1^2^3 = 0)', '3\n1 2 3', 'Second'),
        tc('XOR != 0 (2^3 = 1)', '2\n2 3', 'First'),
        tc('Single empty pile', '1\n0', 'Second'),
        tc('Symmetric twin piles', '2\n7 7', 'Second'),
        tc('Four-pile P-state', '4\n0 8 9 1', 'Second'),
        tc('Single non-empty pile', '3\n0 0 4', 'First')
      ],
      hints: [
        'Compute xor_sum = a[0] ^ a[1] ^ ... ^ a[n-1].',
        'By the Bouton / Sprague-Grundy theorem, First wins iff xor_sum != 0.',
        'Zero piles do not affect the XOR sum.'
      ],
      pythonStarter: pyBase + 'n = int(input())\npiles = list(map(int, input().split()))\n',
      cppStarter: cppBase
    }
  ]
}
