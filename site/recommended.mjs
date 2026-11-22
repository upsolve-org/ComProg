// Curated Codeforces training problems per chapter, enriched at build time
// with exact titles, ratings, tags, and solved counts from codeforces-problems.json.

export const recommendedByChapter = {
  '00_getting_started': {
    cfTag: 'implementation',
    subtitle: 'Build fast-I/O fluency and bug-free submission habits on classic Division 2 A problems.',
    problems: [
      { id: '4A', topic: 'Conditionals & parity', tier: 'Foundation', why: 'Classic warm-up testing edge cases like n = 2.' },
      { id: '71A', topic: 'String formatting & loops', tier: 'Foundation', why: 'Practice reading T test cases and formatting output cleanly.' },
      { id: '231A', topic: 'Counting & multi-line input', tier: 'Foundation', why: 'Fast row-by-row integer parsing and summation.' },
      { id: '282A', topic: 'String inspection', tier: 'Foundation', why: 'Simple state simulation across operations.' },
      { id: '158A', topic: 'Threshold filtering', tier: 'Core', why: 'Combines 1-indexed array lookup with a positivity guard.' }
    ]
  },
  '01_foundations_and_complexity': {
    cfTag: 'implementation',
    subtitle: 'Master O(1) prefix-sum queries, difference arrays, and hash-map prefix counting.',
    problems: [
      { id: '363B', topic: 'Prefix sums / fixed window', tier: 'Foundation', why: 'Direct application of O(n) cumulative sums to find the minimum k-span.' },
      { id: '433B', topic: 'Static range sum queries', tier: 'Foundation', why: 'Build two prefix-sum arrays (original and sorted) to answer 10⁵ queries.' },
      { id: '295A', topic: 'Difference arrays (nested)', tier: 'Core', why: 'Apply a difference array to operations, then a second difference array to the elements.' },
      { id: '816B', topic: 'Difference array + prefix sum', tier: 'Core', why: 'Convert range increments into admissibility counts in O(N + Q).' },
      { id: '1398C', topic: 'Prefix sum + hash map', tier: 'Challenge', why: 'Rewrite sum(l..r) = r - l + 1 into P[r] - r = P[l-1] - (l-1).' }
    ]
  },
  '02_binary_and_ternary_search': {
    cfTag: 'binary search',
    subtitle: 'Progress from bisect lookups to binary search on the answer and unimodal ternary search.',
    problems: [
      { id: '706B', topic: 'Upper bound (bisect_right)', tier: 'Foundation', why: 'Sort prices and count affordable shops per query in O(log n).' },
      { id: '474B', topic: 'Prefix sums + lower bound', tier: 'Foundation', why: 'Locate which pile contains worm q using bisect_left on cumulative totals.' },
      { id: '1613C', topic: 'Binary search on the answer', tier: 'Core', why: 'Monotonic damage check: find the smallest poison duration k.' },
      { id: '1201C', topic: 'Binary search on median', tier: 'Core', why: 'Check whether raising all right-half elements to target M fits within k operations.' },
      { id: '1355E', topic: 'Ternary search on convex cost', tier: 'Challenge', why: 'Minimize convex brick-moving cost over target height H using ternary search.' }
    ]
  },
  '03_two_pointers_and_sliding_windows': {
    cfTag: 'two pointers',
    subtitle: 'Practice opposite-end convergence, variable-length sliding windows, and frequency windows.',
    problems: [
      { id: '381A', topic: 'Opposite-end two pointers', tier: 'Foundation', why: 'Maintain left and right pointers greedily picking the larger exposed card.' },
      { id: '1341B', topic: 'Fixed-size sliding window', tier: 'Foundation', why: 'Slide a k-window counting strictly interior peaks in O(n).' },
      { id: '279B', topic: 'Variable sliding window', tier: 'Core', why: 'Classic longest subarray with sum ≤ t using monotonic L and R.' },
      { id: '676C', topic: 'Sliding window with budget k', tier: 'Core', why: 'Find the longest substring with at most k mismatched characters.' },
      { id: '701C', topic: 'Minimum covering window', tier: 'Challenge', why: 'Shrink L whenever the window contains every distinct character type.' }
    ]
  },
  '04_sorting_and_greedy': {
    cfTag: 'greedy',
    subtitle: 'Train custom sort keys, interval sweeps, exchange arguments, and regret greedy with heaps.',
    problems: [
      { id: '160A', topic: 'Sorting + greedy prefix', tier: 'Foundation', why: 'Sort descending and take the fewest coins exceeding half the total.' },
      { id: '230A', topic: 'Custom key sorting', tier: 'Foundation', why: 'Sort dragons by strength ascending so bonus power accumulates early.' },
      { id: '492B', topic: 'Gap sweep after sorting', tier: 'Core', why: 'Compute maximum interior half-gap plus boundary distances.' },
      { id: '1343C', topic: 'Greedy block partitioning', tier: 'Core', why: 'Pick the maximum element from every maximal same-sign contiguous block.' },
      { id: '1526C2', topic: 'Regret greedy with min-heap', tier: 'Challenge', why: 'Take every potion and pop the most negative one from a min-heap whenever health < 0.' }
    ]
  },
  '05_data_structures': {
    cfTag: 'data structures',
    subtitle: 'Apply DSU, Segment Trees, Fenwick Trees (BIT), and Monotonic Stacks to real contest tasks.',
    problems: [
      { id: '1167C', topic: 'DSU component sizes', tier: 'Foundation', why: 'Union members of each group and report sz[find(i)] in O(α(n)).' },
      { id: '339D', topic: 'Segment tree point update', tier: 'Core', why: 'Alternating OR / XOR merge up a binary segment tree.' },
      { id: '25D', topic: 'DSU cycle & bridge wiring', tier: 'Core', why: 'Collect redundant cycle edges with DSU and reconnect components.' },
      { id: '61E', topic: 'Fenwick tree inversion triples', tier: 'Challenge', why: 'Coordinate-compress values and count greater-left × smaller-right with two BITs.' },
      { id: '547B', topic: 'Monotonic stack / DSU spans', tier: 'Challenge', why: 'Find each element’s maximal minimum-value span using nearest smaller neighbors.' }
    ]
  },
  '06_dynamic_programming': {
    cfTag: 'dp',
    subtitle: 'Build mastery across 1D transitions, knapsack, grid/state DP, interval DP, and SOS/bitmask DP.',
    problems: [
      { id: '189A', topic: 'Unbounded 1D knapsack', tier: 'Foundation', why: 'Maximize pieces of lengths a, b, c summing to exactly n.' },
      { id: '1195C', topic: '2-row state machine DP', tier: 'Core', why: 'Track best total ending in row 0, row 1, or skipping column i.' },
      { id: '455A', topic: 'Frequency house-robber DP', tier: 'Core', why: 'Aggregate counts by value and choose take(v) vs skip(v).' },
      { id: '607B', topic: 'Interval DP on palindromes', tier: 'Challenge', why: 'Merge matching endpoints s[l] == s[r] or split at every k ∈ [l, r).' },
      { id: '165E', topic: 'Bitmask / SOS DP', tier: 'Challenge', why: 'Propagate submask witnesses across 22-bit masks in O(B · 2ᴮ).' }
    ]
  },
  '07_graph_algorithms': {
    cfTag: 'graphs',
    subtitle: 'Practice BFS state graphs, Kahn’s topological sort, Dijkstra, MST, and Tarjan bridges.',
    problems: [
      { id: '520B', topic: 'BFS shortest path on states', tier: 'Foundation', why: 'Model ×2 and −1 operations as unweighted directed edges.' },
      { id: '510C', topic: 'Topological sort (Kahn’s)', tier: 'Core', why: 'Extract character ordering constraints from adjacent words and detect cycles.' },
      { id: '20C', topic: 'Dijkstra + path reconstruction', tier: 'Core', why: 'Standard priority-queue Dijkstra with parent pointers on 10⁵ vertices.' },
      { id: '1245D', topic: 'MST with super-source node', tier: 'Challenge', why: 'Model power stations as edges from virtual node 0 and run Kruskal/Prim.' },
      { id: '118E', topic: 'Bridges & DFS tree orientation', tier: 'Challenge', why: 'A connected graph has a strongly connected orientation iff it has zero bridges.' }
    ]
  },
  '08_trees_and_lca': {
    cfTag: 'trees',
    subtitle: 'Combine DFS subtree aggregation, Euler tour flattening, and binary lifting LCA.',
    problems: [
      { id: '580C', topic: 'Rooted tree DFS', tier: 'Foundation', why: 'Pass consecutive-obstacle count down from root to leaves.' },
      { id: '1336A', topic: 'Subtree size & depth greedy', tier: 'Core', why: 'Compute depth[u] − (subtree[u] − 1) in one post-order DFS.' },
      { id: '191C', topic: 'LCA + tree difference array', tier: 'Challenge', why: 'Add +1 at u, +1 at v, −2 at LCA(u, v) and accumulate bottom-up.' },
      { id: '383C', topic: 'Euler tour + Fenwick tree', tier: 'Challenge', why: 'Flatten subtrees to [tin[u], tout[u]] for alternating-sign range updates.' },
      { id: '1304E', topic: 'LCA tree path distances', tier: 'Challenge', why: 'Check parity and shortest distances with and without an added shortcut edge.' }
    ]
  },
  '09_mathematics_and_number_theory': {
    cfTag: 'number theory',
    subtitle: 'Sharpen GCD bounds, Sieve of Eratosthenes, SPF factorization, combinatorics, and bitmasks.',
    problems: [
      { id: '1370A', topic: 'GCD observation', tier: 'Foundation', why: 'Prove the maximum pairwise GCD in [1..n] is always floor(n / 2).' },
      { id: '1420B', topic: 'Bitwise MSB grouping', tier: 'Foundation', why: 'Two numbers satisfy (a & b) ≥ (a ^ b) iff they share the same highest set bit.' },
      { id: '230B', topic: 'Sieve of Eratosthenes', tier: 'Core', why: 'A number has exactly 3 divisors iff it is the square of a prime.' },
      { id: '154B', topic: 'SPF prime factorization', tier: 'Challenge', why: 'Track active prime factors in O(log n) per activation/deactivation.' },
      { id: '300C', topic: 'Modular factorials & nCr', tier: 'Challenge', why: 'Precompute fact[] and inv_fact[] mod 10⁹+7 to sum valid digit counts.' }
    ]
  },
  '10_string_algorithms': {
    cfTag: 'strings',
    subtitle: 'Master KMP prefix borders, Z-algorithm, double rolling hashes, and binary XOR tries.',
    problems: [
      { id: '126B', topic: 'KMP / Z-function borders', tier: 'Core', why: 'Find the longest prefix that is also a suffix and appears in the middle.' },
      { id: '271D', topic: 'Double rolling hash', tier: 'Core', why: 'Hash all valid substrings with ≤ k bad characters into a set.' },
      { id: '471D', topic: 'KMP on difference arrays', tier: 'Core', why: 'Run linear-time KMP on adjacent height differences.' },
      { id: '706D', topic: 'Binary XOR Trie', tier: 'Challenge', why: 'Maintain a 30-bit Trie supporting insert, delete, and max-XOR queries.' },
      { id: '432D', topic: 'Z-function + prefix counts', tier: 'Challenge', why: 'Count occurrences of every prefix-suffix border in O(n).' }
    ]
  },
  '11_advanced_techniques': {
    cfTag: 'games',
    subtitle: 'Tackle constructive permutations, Mo’s offline square-root queries, and Nim/Grundy games.',
    problems: [
      { id: '1382B', topic: 'Game theory / Nim prefix', tier: 'Foundation', why: 'Analyze forced 1-stone moves before the first pile with > 1 stone.' },
      { id: '1352G', topic: 'Constructive parity zigzag', tier: 'Core', why: 'Interleave odd ascending and even descending with a 2-element swap.' },
      { id: '1194D', topic: 'Grundy period analysis', tier: 'Core', why: 'Discover the periodic P/N-state pattern modulo k + 1.' },
      { id: '86D', topic: 'Mo’s algorithm (O(1) add/rem)', tier: 'Challenge', why: 'Maintain sum(cnt[x]² · x) across 2·10⁵ offline range queries.' },
      { id: '617E', topic: 'Mo’s algorithm + prefix XOR', tier: 'Challenge', why: 'Count pairs with P[r] ^ P[l-1] = k inside the sliding Mo window.' }
    ]
  }
}
