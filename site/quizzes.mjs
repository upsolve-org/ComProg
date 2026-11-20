const q = (question, options, answer, explanation) => ({ question, options, answer, explanation })

export const quizzes = [
  // 00_General_Advice_and_Practice
  [
    q(
      'Why does removing the first element of a Python list with pop(0) inside a loop over N elements cause Time Limit Exceeded?',
      [
        'It shifts all remaining N − 1 elements in memory, making the loop O(N²).',
        'Python lists store elements as a doubly linked list with slow pointer hops.',
        'Calling pop(0) triggers a full garbage collection pass on every call.',
        'List indexing in Python uses a hash table lookup.'
      ],
      0,
      'A Python list is a contiguous dynamic array. Removing index 0 shifts every subsequent element left by one slot in O(N) time; use collections.deque and popleft() for O(1) front removal.'
    ),
    q(
      'In a Codeforces round that uses pretests followed by system tests, what does "Pretests passed" guarantee?',
      [
        'Your solution passed the initial small test subset, but can still fail final system tests on edge cases or large inputs.',
        'Your solution is permanently Accepted and cannot be hacked or rejudged.',
        'Your solution passed every hidden maximum-constraint test case.',
        'Your solution used less than half of the memory limit.'
      ],
      0,
      'Pretests only check a partial test suite during the live round. Always test minimum boundaries, maximum constraints, and tricky counterexamples yourself before moving on.'
    ),
    q(
      'When should you prefer submitting under PyPy3 over CPython in a competitive programming contest?',
      [
        'When your solution executes tight pure-Python loops or heavy arithmetic iterations.',
        'When your solution spends 99% of its time inside a single C-extension call like str.split().',
        'When your recursive function needs unlimited stack depth without overhead.',
        'When the input size is N <= 10 and startup time is the only cost.'
      ],
      0,
      'PyPy3 uses a Just-In-Time (JIT) compiler that compiles hot Python loops into fast machine code, often running pure-Python loops 5x to 10x faster than CPython.'
    )
  ],
  // 01_Foundations_and_Complexity
  [
    q(
      'Given a 1-padded prefix sum array pref of length N + 1 where pref[k] = sum(A[0..k-1]), what is the sum of the 0-indexed subarray A[L..R] inclusive?',
      [
        'pref[R + 1] - pref[L]',
        'pref[R] - pref[L - 1]',
        'pref[R + 1] - pref[L + 1]',
        'pref[R] - pref[L]'
      ],
      0,
      'Because pref[R + 1] sums A[0..R] and pref[L] sums A[0..L-1], their difference pref[R + 1] - pref[L] isolates the exact contiguous range A[L..R] in O(1) time.'
    ),
    q(
      'To add v to every element in A[L..R] using a difference array diff before reconstructing A via prefix sums, which two updates are needed?',
      [
        'diff[L] += v and diff[R + 1] -= v',
        'diff[L - 1] += v and diff[R] -= v',
        'diff[L] += v and diff[R] -= v',
        'diff[L] -= v and diff[R + 1] += v'
      ],
      0,
      'Adding v at index L starts the +v offset from L onward in the prefix sum, and subtracting v at R + 1 cancels that offset immediately after index R.'
    ),
    q(
      'If a problem specifies N <= 200,000 and a 1.0-second time limit, which asymptotic time complexity is the safest target?',
      [
        'O(N) or O(N log N)',
        'O(N²)',
        'O(N² log N)',
        'O(2^N)'
      ],
      0,
      'At N = 200,000, O(N log N) performs roughly 3.6 million operations, fitting comfortably within 1 second in Python, whereas O(N²) requires 40 billion operations and will TLE.'
    )
  ],
  // 02_Binary_and_Ternary_Search
  [
    q(
      'In a sorted list A = [1, 4, 4, 4, 7], what do bisect_left(A, 4) and bisect_right(A, 4) return?',
      [
        'bisect_left returns 1 and bisect_right returns 4',
        'bisect_left returns 1 and bisect_right returns 3',
        'bisect_left returns 0 and bisect_right returns 4',
        'bisect_left returns 2 and bisect_right returns 4'
      ],
      0,
      'bisect_left finds the first index where A[i] >= 4 (index 1), while bisect_right finds the first index where A[i] > 4 (index 4). Their difference 4 - 1 = 3 is the count of 4s.'
    ),
    q(
      'What property must the feasibility predicate check(x) satisfy to apply binary search on the answer space?',
      [
        'Monotonicity: check(x) transitions at most once between False and True across the search range.',
        'Convexity: check(x) decreases to a valley and then increases again.',
        'Linearity: check(x) must run in O(1) time for every candidate x.',
        'Periodicity: check(x) repeats its truth value every k steps.'
      ],
      0,
      'Binary search requires a monotonic boundary (all False followed by all True, or all True followed by all False) so each probe eliminates half of the remaining candidates.'
    ),
    q(
      'When minimizing a strictly unimodal function f(x) over [L, R] with ternary search, if f(m1) > f(m2) for m1 < m2, which sub-interval can be discarded?',
      [
        'The left third [L, m1], keeping [m1, R]',
        'The right third [m2, R], keeping [L, m2]',
        'The middle third [m1, m2], keeping only the outer ends',
        'Both [L, m1] and [m2, R] at once'
      ],
      0,
      'If f(m1) > f(m2) on a function that decreases to a single minimum and then increases, the minimum cannot lie to the left of m1, so we set L = m1.'
    )
  ],
  // 03_Two_Pointers_and_Sliding_Window
  [
    q(
      'Why does a variable-size sliding window with an outer for-loop on R and an inner while-loop advancing L run in O(N) total time?',
      [
        'Both L and R only move forward and each visits at most N positions across the entire algorithm.',
        'The inner while-loop never executes more than once per outer iteration.',
        'Python optimizes nested while-loops into vector instructions automatically.',
        'The window size R - L + 1 stays constant throughout the scan.'
      ],
      0,
      'By amortized analysis, each element enters the window once when R advances and leaves at most once when L advances, giving at most 2N pointer movements in total.'
    ),
    q(
      'When sliding a fixed-size window of length K from index i - 1 to index i (where i >= K), how do you update the window sum in O(1)?',
      [
        'window_sum += A[i] - A[i - K]',
        'window_sum += A[i] - A[i - K + 1]',
        'window_sum = sum(A[i - K : i])',
        'window_sum += A[i + 1] - A[i - K]'
      ],
      0,
      'The new window A[i - K + 1 .. i] gains element A[i] on the right and loses element A[i - K] on the left.'
    ),
    q(
      'If every subarray inside a currently valid window [L..R] is also valid, how many valid subarrays end at index R?',
      [
        'R - L + 1',
        'R - L',
        '(R - L + 1) * (R - L) // 2',
        'L + 1'
      ],
      0,
      'Any starting index from L to R inclusive forms a valid subarray ending at R, which gives exactly R - L + 1 subarrays.'
    )
  ],
  // 04_Sorting_and_Greedy
  [
    q(
      'To maximize the number of non-overlapping intervals you can attend, which greedy sorting order is provably optimal?',
      [
        'Sort intervals by earliest finish time (ascending end coordinate).',
        'Sort intervals by earliest start time (ascending start coordinate).',
        'Sort intervals by shortest duration (end - start).',
        'Sort intervals by fewest overlaps with other intervals.'
      ],
      0,
      'Choosing the compatible interval that finishes earliest leaves the maximum possible timeline free for all subsequent intervals.'
    ),
    q(
      'In Python, which key function sorts pairs (start, end) by ascending start time, breaking ties by descending end time?',
      [
        'key=lambda item: (item[0], -item[1])',
        'key=lambda item: (-item[0], item[1])',
        'key=lambda item: (item[1], -item[0])',
        'key=lambda item: item[0] - item[1]'
      ],
      0,
      'Python compares tuples lexicographically: item[0] sorts ascending by start, and -item[1] reverses numeric order for the tie-breaker.'
    ),
    q(
      'What is the purpose of coordinate compression on an array of N = 100,000 integers with values up to 10^9?',
      [
        'It maps the values to dense ranks in [0, N - 1] while preserving their relative order.',
        'It reduces the number of elements in the array to log2(N).',
        'It sorts the array in O(N) time without comparisons.',
        'It encrypts the coordinates to prevent hash collisions.'
      ],
      0,
      'Replacing sparse values up to 10^9 with their sorted unique indices in [0, U - 1] lets you index frequency tables, Fenwick trees, or segment trees directly.'
    )
  ],
  // 05_Data_Structures
  [
    q(
      'In a Fenwick Tree (Binary Indexed Tree), what does the bitwise expression i & -i compute for a 1-based index i?',
      [
        'The value of the lowest set bit of i (the largest power of 2 dividing i).',
        'The index of the highest set bit of i.',
        'The bitwise complement of i modulo N.',
        'The parent node index i // 2 in a binary heap.'
      ],
      0,
      'In two’s complement arithmetic, -i is (~i + 1), so i & -i isolates the lowest set bit, which determines the block length stored at index i.'
    ),
    q(
      'Why do we combine path compression with union by size/rank in a Disjoint Set Union (DSU)?',
      [
        'To keep trees flat so find and union run in nearly O(1) amortized time, O(alpha(N)).',
        'To keep the elements inside each set sorted in ascending order.',
        'To allow arbitrary edge deletions in O(1) online time.',
        'To reduce the parent array memory from O(N) to O(log N).'
      ],
      0,
      'Union by size bounds tree height by O(log N), and path compression relinks visited nodes directly to the root, achieving inverse-Ackermann amortized complexity.'
    ),
    q(
      'To find the minimum of every sliding window of size K in O(N) total time, how should a monotonic deque be maintained?',
      [
        'Keep indices in increasing order of their array values, popping larger elements from the back before pushing.',
        'Keep indices in decreasing order of their array values, popping smaller elements from the back.',
        'Sort the deque with timsort after every window shift.',
        'Push elements to a min-heap and clear the entire heap every K steps.'
      ],
      0,
      'Popping elements from the back that are >= the new element keeps the deque monotonic increasing from front to back, so the front always holds the window minimum.'
    )
  ],
  // 06_Dynamic_Programming
  [
    q(
      'When implementing 0/1 Knapsack with a 1D array dp[0..W], why must the inner capacity loop run backward from W down to weight?',
      [
        'So each transition reads dp[w - weight] from the previous item’s state without using the same item multiple times.',
        'Because Python range loops execute faster when stepping by -1.',
        'To ensure smaller capacities are never updated.',
        'Because unbounded knapsack requires a backward loop while 0/1 knapsack requires a forward loop.'
      ],
      0,
      'Iterating w downward guarantees dp[w - weight] has not yet been updated during the current item’s pass, enforcing the 0/1 single-use constraint.'
    ),
    q(
      'What does tails[k] store in the O(N log N) Longest Increasing Subsequence (LIS) algorithm?',
      [
        'The smallest possible ending value of an increasing subsequence of length k + 1 seen so far.',
        'The number of increasing subsequences of length k + 1.',
        'The starting index of the longest increasing subsequence ending at index k.',
        'The maximum value among the first k + 1 elements.'
      ],
      0,
      'Keeping the smallest tail for each subsequence length makes tails monotonically increasing, allowing bisect_left to place each new element in O(log N) time.'
    ),
    q(
      'In Interval DP where dp[L][R] depends on narrower sub-intervals dp[L][k] and dp[k + 1][R], what must the outermost loop iterate over?',
      [
        'The interval length len from smallest to largest.',
        'The left endpoint L from 0 to N - 1.',
        'The split point k from 0 to N - 1.',
        'The right endpoint R from N - 1 down to 0.'
      ],
      0,
      'Because computing dp[L][R] of length len requires shorter intervals of length < len to be ready, iterating in increasing order of interval length satisfies all dependencies.'
    )
  ],
  // 07_Graph_Algorithms
  [
    q(
      'In Breadth-First Search (BFS), why should you mark a neighbor vertex as visited at the moment it is enqueued rather than when it is dequeued?',
      [
        'To prevent the same vertex from being pushed into the queue multiple times by different neighbors in the same layer.',
        'Because collections.deque does not allow duplicate integers.',
        'To make BFS traverse the graph in depth-first order.',
        'Because dequeueing a vertex takes O(V) time.'
      ],
      0,
      'Marking on enqueue ensures each vertex enters the queue at most once, keeping total time and queue size strictly O(V + E).'
    ),
    q(
      'Why does Dijkstra’s algorithm fail on graphs with negative-weight edges?',
      [
        'It assumes popping the smallest distance in the priority queue finalizes that node, which a later negative edge could undercut.',
        'Python heapq raises an exception when tuple distances are negative.',
        'Negative weights always create an infinite cycle in every directed graph.',
        'Adjacency lists cannot store negative numbers.'
      ],
      0,
      'Dijkstra’s greedy invariant relies on non-negative weights so path distances never decrease as edges are added; use Bellman-Ford when negative weights exist.'
    ),
    q(
      'In Tarjan’s DFS on an undirected graph, when is a tree edge (u, v) from parent u to child v a bridge?',
      [
        'When low[v] > tin[u] (strictly greater).',
        'When low[v] >= tin[u] (greater than or equal).',
        'When low[v] == tin[v].',
        'When tin[u] > low[u].'
      ],
      0,
      'low[v] > tin[u] means no node in v’s subtree has a back-edge reaching u or any ancestor of u, so removing edge (u, v) disconnects v’s subtree.'
    )
  ],
  // 08_Trees_and_LCA
  [
    q(
      'What key property of an Euler tour (DFS entry and exit timestamps tin[u]..tout[u]) makes it useful for subtree queries?',
      [
        'Every vertex u’s entire subtree maps to a single contiguous range [tin[u], tout[u]] in the flattened array.',
        'Vertices are ordered by their distance from the root in ascending BFS order.',
        'It reduces the tree height to O(log N) without changing parent pointers.',
        'It sorts the children of every node by their degree.'
      ],
      0,
      'Because DFS explores all descendants of u before leaving u, the timestamps [tin[u], tout[u]] form a contiguous interval ideal for Fenwick or Segment Tree range queries.'
    ),
    q(
      'Once you compute w = LCA(u, v) in a rooted tree with node depths depth[], what is the number of edges on the simple path between u and v?',
      [
        'depth[u] + depth[v] - 2 * depth[w]',
        'depth[u] + depth[v] - depth[w]',
        'abs(depth[u] - depth[v])',
        'depth[u] + depth[v] + 2 * depth[w]'
      ],
      0,
      'The path climbs from u to w (depth[u] - depth[w] edges) and descends from w to v (depth[v] - depth[w] edges), summing to depth[u] + depth[v] - 2 * depth[w].'
    ),
    q(
      'In the two-BFS algorithm for tree diameter, what does the first BFS from an arbitrary node X find?',
      [
        'A farthest node A from X, which is guaranteed to be one of the endpoints of the tree’s diameter.',
        'The centroid of the tree where all branches have size <= N / 2.',
        'The exact diameter length directly without needing a second traversal.',
        'The Lowest Common Ancestor of the deepest leaves.'
      ],
      0,
      'In any tree, a vertex farthest from an arbitrary starting node is always a diameter endpoint; a second BFS from A finds the opposite endpoint B and the diameter.'
    )
  ],
  // 09_Mathematics_and_Number_Theory
  [
    q(
      'Why does the inner loop of the Sieve of Eratosthenes start crossing out multiples of prime p at p * p instead of 2 * p?',
      [
        'Every composite multiple k * p with 2 <= k < p already has a prime factor smaller than p and was crossed out earlier.',
        'Numbers between 2 * p and p * p are always prime.',
        'Starting at 2 * p would cross out p itself.',
        'It reduces the space complexity of the sieve from O(N) to O(sqrt(N)).'
      ],
      0,
      'Any smaller multiple of p has a prime factor <= k < p, so p * p is the very first composite number whose smallest prime factor is p.'
    ),
    q(
      'When computing combinations nCr modulo a prime p = 1,000,000,007, how should you divide by (r! * (n - r)!) mod p?',
      [
        'Multiply by the modular inverse pow(fact[r] * fact[n - r], p - 2, p) modulo p.',
        'Use integer floor division (fact[n] % p) // ((fact[r] * fact[n - r]) % p).',
        'Use floating-point division and round to the nearest integer.',
        'Subtract fact[r] and fact[n - r] from fact[n] modulo p.'
      ],
      0,
      'Modular arithmetic does not distribute over floor division. By Fermat’s Little Theorem (or pow(x, -1, p)), division modulo prime p is multiplication by the modular inverse.'
    ),
    q(
      'What does Brian Kernighan’s bitwise operation x & (x - 1) do to a positive integer x?',
      [
        'It clears (sets to 0) the lowest set bit of x.',
        'It isolates the lowest set bit of x and clears all higher bits.',
        'It flips all bits of x up to the highest set bit.',
        'It multiplies x by 2 and subtracts 1.'
      ],
      0,
      'Subtracting 1 turns the lowest 1-bit into 0 and all lower 0-bits into 1s, so x & (x - 1) zeroes out that lowest set bit in O(1).'
    )
  ],
  // 10_String_Algorithms
  [
    q(
      'What does the KMP prefix function value pi[i] represent for the prefix substring S[0..i]?',
      [
        'The length of the longest proper prefix of S[0..i] that is also a suffix of S[0..i].',
        'The length of the longest common prefix between S and the suffix S[i..N-1].',
        'The number of distinct characters in S[0..i].',
        'The length of the longest palindromic substring centered at i.'
      ],
      0,
      'pi[i] measures the longest proper border of S[0..i], enabling KMP to shift the pattern to the longest viable overlap on a mismatch without re-reading text characters.'
    ),
    q(
      'Why is a single 32-bit modulus (around 10^9 + 7) risky for polynomial rolling hashes when comparing all substrings of a string of length N = 100,000?',
      [
        'By the Birthday Paradox, collisions become likely once the number of distinct hashes approaches sqrt(M) ≈ 31,600.',
        'Python integers overflow at 2^31 - 1 and wrap around to negative values.',
        'Computing powers modulo 10^9 + 7 takes O(N²) time.',
        'A 32-bit modulus only works for binary strings of 0s and 1s.'
      ],
      0,
      'Comparing ~10^5 substrings against a 10^9 modulus has high collision probability via the Birthday Paradox; use double hashing or a 61-bit modulus with a random base.'
    ),
    q(
      'How do you find the maximum XOR pair x ^ y in an array using a Binary Trie of 30-bit integers?',
      [
        'Walk from the most significant bit (bit 29) down to bit 0, greedily taking the child branch opposite to the current bit of x whenever it exists.',
        'Walk from the least significant bit (bit 0) up to bit 29, taking matching bits.',
        'Perform a breadth-first search across all leaves and sort their depths.',
        'Count how many numbers share the same lowest set bit in the root.'
      ],
      0,
      'Because 2^k > 2^(k-1) + ... + 2^0, securing a 1 in a higher bit of the XOR result always beats any combination of lower bits.'
    )
  ],
  // 11_Advanced_and_Niche_Techniques
  [
    q(
      'According to Bouton’s Theorem, when does the first player have a forced win in standard normal-play Nim with pile sizes A_1, A_2, ..., A_n?',
      [
        'When the bitwise XOR sum A_1 ^ A_2 ^ ... ^ A_n is non-zero.',
        'When the arithmetic sum A_1 + A_2 + ... + A_n is an odd number.',
        'When the number of non-empty piles n is odd.',
        'When the maximum pile size is strictly greater than the sum of the others.'
      ],
      0,
      'A Nim state is losing (P-position) if and only if the XOR sum is 0. From any non-zero XOR sum, there is always a move that reduces one pile to make the new XOR sum 0.'
    ),
    q(
      'In Mo’s algorithm with block size B ≈ sqrt(N), how should offline queries (L, R) be sorted to guarantee O((N + Q) sqrt(N)) pointer steps?',
      [
        'Sort primarily by left block L // B, and secondarily by R (alternating ascending/descending R on odd/even blocks).',
        'Sort queries by their interval length R - L in ascending order.',
        'Sort queries by (L + R) // 2 and binary search each block.',
        'Sort queries strictly by R first and then by L.'
      ],
      0,
      'Grouping by L // B restricts L to moving at most B steps per query, while sorting R monotonically within each block restricts R to sweeping the array once per block.'
    ),
    q(
      'When solving a constructive problem that asks for a permutation of 1..N with large adjacent differences, which canonical pattern is most effective?',
      [
        'Interleave extremes: [1, N, 2, N - 1, 3, N - 2, ...].',
        'Output the identity permutation [1, 2, 3, ..., N].',
        'Cyclic shift by one: [2, 3, ..., N, 1].',
        'Group all even numbers followed by all odd numbers in ascending order.'
      ],
      0,
      'Interleaving low and high extremes alternates steps of size N - 1, N - 2, N - 3, ..., producing every distinct difference from 1 to N - 1.'
    )
  ],
  // 12_Reference_and_Catalog
  [
    q(
      'Which combination of two techniques transforms "sum or update values in the subtree of node u" into a standard 1D range query?',
      [
        'Euler Tour (DFS entry/exit timestamps) + Fenwick Tree or Segment Tree.',
        'Binary Lifting + Kruskal’s Minimum Spanning Tree.',
        'Topological Sort + Polynomial Rolling Hash.',
        'Ternary Search + Monotonic Stack.'
      ],
      0,
      'An Euler tour maps each subtree to a contiguous range [tin[u], tout[u]], allowing a Fenwick Tree or Segment Tree to handle subtree updates and queries in O(log N).'
    ),
    q(
      'When an optimization problem asks to "minimize the maximum weight/capacity needed to satisfy a condition", which paradigm should you check first?',
      [
        'Binary Search on the Answer combined with a greedy, two-pointer, or BFS/DFS feasibility check.',
        'Sprague-Grundy theorem with mex values.',
        'Extended Euclidean Algorithm with Chinese Remainder Theorem.',
        'KMP prefix function on the input array.'
      ],
      0,
      'Minimax / bottleneck thresholds almost always have a monotonic feasibility predicate: if threshold X works, any threshold > X also works.'
    ),
    q(
      'What is the fastest way to isolate a hidden edge-case bug when your contest submission fails on Test 42?',
      [
        'Write a small random test generator and stress-test your fast solution against a simple brute-force solver on tiny inputs (N <= 8).',
        'Submit random +/- 1 changes to your loop bounds until it passes.',
        'Rewrite the same algorithm from scratch without changing the logic.',
        'Only test the sample input from the problem statement again.'
      ],
      0,
      'Stress-testing against an obviously correct brute-force solver on thousands of small random inputs finds a minimal 5-element counterexample in seconds.'
    )
  ]
]
