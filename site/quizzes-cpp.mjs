// C++20 pitfalls: every question targets a mistake that compiles cleanly and then misbehaves.
const q = (question, options, answer, explanation) => ({ question, options, answer, explanation })

export const cppQuizzes = [
  // 00_General_Advice_and_Practice
  [
    q(
      'A learner writes `long long best = 0; long long run = 0;` and adds `best = max(best, run)` after `run += x`. On the all-negative sample `3 / -5 -2 -3` it prints what?',
      [
        '`-1`: `max` keeps the first `run` value.',
        '`0`: `best` started at 0 and no negative run exceeded it.',
        '`-10`: it sums everything.',
        'It does not compile without including `<algorithm>`.'
      ],
      1,
      'Starting `best` and `run` at 0 assumes an empty subarray is allowed. The statement needs a non-empty one, so `best` must start at `LLONG_MIN` (or at the first value) for all-negative input.'
    ),
    q(
      'A learner writes `for (int i = 0; i < v.size() - 1; ++i)`. When is the loop unsafe?',
      [
        'When `v` is empty: `v.size() - 1` wraps to a huge unsigned value.',
        'Never, because `size_t` handles it.',
        'Only when the vector holds more than 2³¹ elements.',
        'Only when signed `i` is converted to `size_t` inside the comparison.'
      ],
      0,
      '`v.size()` is `size_t` (unsigned), so the subtraction stays unsigned and `0 - 1` wraps to `SIZE_MAX`. The loop then reads far past the end.'
    ),
    q(
      'Why does a bulk-print submission benefit from `cin.tie(nullptr)` plus a single output buffer?',
      [
        'It changes the printed precision of the values.',
        'It removes a flush before every read and one write syscall per value.',
        'It disables the C stream so `printf` starts failing.',
        'It sorts the output automatically.'
      ],
      1,
      '`tie(nullptr)` stops `cin` from flushing `cout` before each read, and buffering removes one syscall per token. Together they are the difference between tens of milliseconds and a TLE.'
    )
  ],
  // 01_Foundations_and_Complexity
  [
    q(
      'A prefix-sum table is built as `vector<int> pre(n + 1)`. With n = 2·10⁵ and values up to 10⁹, what happens?',
      [
        'It is correct: sums only grow to 2·10⁹, which still fits int.',
        'It compiles to `long long` automatically.',
        'The prefixes reach 2·10¹⁴ and overflow, silently or under UBSan.',
        'Only the final element overflows, so the difference trick still works.'
      ],
      2,
      '2·10⁵ values of 10⁹ sum to 2·10¹⁴, far past 2³¹−1. Use `vector<long long>`: every later difference on an overflowed prefix is wrong.'
    ),
    q(
      'Why must `ios::sync_with_stdio(false)` run before any I/O rather than after?',
      [
        'The flag detaches the buffers at setup; once reads have filled the tied C buffer the rest of the run is unsynchronised.',
        'It is UB whenever input has already started.',
        'Mixing it with `scanf` afterwards crashes the runtime.',
        'It only matters for output, and output always goes first.'
      ],
      0,
      'The call removes the per-operation locking between `cin` and `stdin`. Done after reads, some of the run kept the lock and the rest did not, so the two no longer agree on the buffer state.'
    ),
    q(
      'A difference array applies `diff[l] += v; diff[r + 1] -= v;` with queries up to `r = n`. Why is it sized `n + 2`?',
      [
        'The update writes index `n + 1` for `r = n`.',
        'Indexing at `n + 1` is faster than at `n`.',
        'The final prefix pass reads one past the end.',
        'Over-allocating by one stops the vector reallocating.'
      ],
      0,
      '`r + 1` is one past the last element when `r = n`, so the write needs a cell there. Any shorter vector gets an out-of-bounds write.'
    )
  ],
  // 02_Binary_and_Ternary_Search
  [
    q(
      'Why can `int mid = (lo + hi) / 2;` fail near LLONG_MAX?',
      [
        'It truncates the fraction instead of rounding.',
        '`lo + hi` overflows before the division.',
        'The division of two `long long` is undefined.',
        'It rounds differently on Windows.'
      ],
      1,
      'The addition happens first and can pass LLONG_MAX. `mid = lo + (hi - lo) / 2` never leaves the interval.'
    ),
    q(
      'What is wrong with `auto it = std::lower_bound(s.begin(), s.end(), x);` when `s` is a `std::set<int>`?',
      [
        'It is correct, so nothing.',
        'It does not compile because lower_bound needs random access.',
        'It compiles but walks O(n) elements and loses the tree’s O(log n) bound.',
        'It returns a different element than `s.lower_bound(x)`.'
      ],
      2,
      '`std::lower_bound` advances iterators with `++`, so a bidirectional set iterator makes it linear. `s.lower_bound(x)` uses the tree directly in O(log n).'
    ),
    q(
      'A ternary search uses `m1 = lo + (hi - lo) / 3`, `m2 = hi - (hi - lo) / 3` while `hi - lo > 2`. Trace `lo = 0, hi = 3`.',
      [
        'm1 = 1, m2 = 2: two distinct probes, fine.',
        'm1 = m2 = 1: the comparison never holds and the search drifts left.',
        'It underflows because hi - lo could be unsigned.',
        'm1 = 0, m2 = 3: the interval never shrinks.'
      ],
      1,
      'With `hi - lo = 3` the third is 1, so both probes land on 1. Equal probes make `f(m1) < f(m2)` false and shrink the wrong side; scanning a small tail avoids the case.'
    )
  ],
  // 03_Two_Pointers_and_Sliding_Window
  [
    q(
      'What does a comparator returning `a.x <= b.x` cause?',
      [
        'It is correct: the `=` makes ties stable.',
        'It sorts descending on ties.',
        'It can make introsort move elements outside the range and corrupt memory or crash.',
        'It silently switches the sort to insertion order.'
      ],
      2,
      'A comparator must be a strict weak order. With `<=`, equal elements claim to precede each other both ways, which violates the ordering and lets introsort walk out of bounds.'
    ),
    q(
      'In a converging two-pointer loop over sorted data, why must exactly one pointer move per comparison?',
      [
        'Otherwise `lo` can stall on the same index forever.',
        'Both must move to keep the loop symmetric.',
        'Only to prevent signed overflow of the sum.',
        'It is a style choice, either variant is fine.'
      ],
      0,
      'The loop ends when the pointers meet, so both must strictly progress toward each other. Moving neither (or reusing an index) never terminates.'
    ),
    q(
      'A greedy picks the longest event first instead of the one with the earliest end. Which input shows the flaw?',
      [
        'Two identical events.',
        'One long event [1, 10] plus unit events [2, 3], [4, 5], [6, 7].',
        'Ten events that all end at different times.',
        'Events given in reverse input order.'
      ],
      1,
      'The long event overlaps all three short ones: longest-first takes 1, earliest-finish takes 3. The exchange argument only holds for the earliest end.'
    )
  ],
  // 04_Sorting_and_Greedy
  [
    q(
      'What does `x & -x` do on an `unsigned long long`?',
      [
        'Isolates the lowest set bit: unsigned negation is `~x + 1` modulo 2⁶⁴.',
        'Clears the lowest set bit.',
        'Needs two’s complement hardware that C++ does not require.',
        'Reverses the bit order.'
      ],
      0,
      'Unsigned negation is defined modulo 2⁶⁴, so the AND leaves exactly the lowest set bit. Clearing it instead is `x &= x - 1`.'
    ),
    q(
      '`#include <ext/pb_ds/assoc_container.hpp>` fails to build. Which cause is correct?',
      [
        'It must come before `<bits/stdc++.h>`.',
        'PBDS only exists in C++14 mode.',
        'It is libstdc++-only and unavailable under libc++ and MSVC.',
        'It needs `using namespace std::tr1;` first.'
      ],
      2,
      'Policy-based data structures ship with GNU libstdc++ — what Codeforces uses. Other standard libraries do not have them; the extension headers go after `<bits/stdc++.h>`.'
    ),
    q(
      'A Fenwick update reads `for (; i <= n; i += i & -i) bit[i] += x;`. What breaks with `i += 1` instead?',
      [
        'Nothing: `i += 1` visits a superset of the cells.',
        'Some prefix queries come out too small because covering cells are skipped.',
        'The loop overflows and never ends.',
        'Only the build is affected, not the queries.'
      ],
      1,
      'The O(log n) update relies on jumping to the next cell that covers `i`. Walking one by one misses long-range cells, so prefix aggregates come out low.'
    )
  ],
  // 05_Data_Structures
  [
    q(
      'In a 0/1 knapsack over capacity, why is the capacity loop descending?',
      [
        'Descending has better cache locality.',
        'Ascending re-reads the just-written `c - w` cell and reuses the same item.',
        'Descending lets the answer be read from `best[0]`.',
        'It keeps modulo arithmetic consistent.'
      ],
      1,
      'Ascending writes `best[c - w]` earlier in the same item pass, so the item can be taken repeatedly. Descending makes the source cell come from before this item.'
    ),
    q(
      'Why is `1 << n` wrong for `n = 31` in a bitmask DP?',
      [
        'The left operand is `int`: bit 31 sets the sign and larger n is undefined.',
        'It is fine up to n = 63 on a 64-bit machine.',
        'It produces a negative value but still indexes correctly.',
        'It only needs extra parentheses.'
      ],
      0,
      'A shift of 31 produces `INT_MIN`. For n = 31 and beyond use `1LL << n`, or store bits as `1 << k` on an `unsigned` mask.'
    ),
    q(
      'A tree DP recurses on a path of 200,000 vertices. What is the realistic failure?',
      [
        'The compiler stack runs out while compiling.',
        'The answer overflows.',
        'The frames exceed the 8 MB stack and the program crashes.',
        'The recursion is ten times slower than an explicit stack.'
      ],
      2,
      'Each frame is tens of bytes and 200,000 of them pass 8 MB. Convert to an explicit stack with a BFS or post-order, or raise the stack limit locally.'
    )
  ],
  // 06_Dynamic_Programming
  [
    q(
      'Which weight condition makes Dijkstra correct?',
      [
        'No self-loops.',
        'All weights non-negative.',
        'The graph is connected.',
        'The number of edges is small.'
      ],
      1,
      'Dijkstra finalises a vertex on its first pop. A later negative edge can improve an already-final vertex, which Dijkstra never revisits.'
    ),
    q(
      'What do the stale-entry checks `if (d != distance[u]) continue;` in a lazy Dijkstra heap do?',
      [
        'They skip heap copies whose distance was improved later, so only the current one relaxes.',
        'They only save time; the answer is identical without them.',
        'They keep the heap below n entries.',
        'They are what make `greater<>` a min-heap.'
      ],
      0,
      'A vertex can sit in the heap several times with different distances. Relaxing from an outdated copy uses the wrong base distance and can corrupt the result.'
    ),
    q(
      'A directed cycle test stores only `visited` and no second `in-progress` state. Which wrong verdict does a valid 3-cycle get?',
      [
        'It is reported as a DAG, or the DFS recurses until overflow.',
        'Nothing: `visited` alone detects the cycle.',
        'It compiles but skips the cycle.',
        'It is always RE.'
      ],
      0,
      'The visit check sees the cycle edge back to a visited vertex and simply returns, so the cycle is never announced. Only an in-progress state turns the back edge into a detection.'
    )
  ],
  // 07_Graph_Algorithms
  [
    q(
      'A tree DFS filters the parent by vertex (`v != parent[u]`) instead of by edge id. When does it break?',
      [
        'When a parallel edge joins the same two vertices: the second copy is not filtered and the DFS walks back up.',
        'When vertex labels are not a permutation.',
        'When the tree is a star.',
        'Never: parents are unique in a tree.'
      ],
      0,
      'The second copy to the parent is not the parent vertex’s own edge, but the vertex test skips it anyway, corrupting depth and traversal order. Track the edge id.'
    ),
    q(
      '`const int LOG = 32 - __builtin_clz(n);` gives 32 for `n = 0`, but here n ≥ 1. For `n = 1` the lift loop `for (int k = LOG; k--;)` reads which index with LOG = 1?',
      [
        '`up[1]`, one past a table of size 1.',
        'Only `up[0]`, which is fine because `k--` is post-decrement in the body.',
        'It is fine because the body is skipped.',
        '`up[-1]` when the loop starts.'
      ],
      0,
      '`k--` evaluates k = 1 first, so `up[1]` is read and only `up[0]` exists. Use `bit_width(n) + 1` levels to cover the pad level.'
    ),
    q(
      'The subtree count loop sweeps the input backwards with `for (int i = n - 1; i > 0; --i)`. Why does it produce correct counts?',
      [
        'The parent of v is always smaller than v, so the reverse order is a valid post-order: children already hold their final counts.',
        'Reversing makes the array cache-friendly.',
        'It avoids recursion so it cannot overflow.',
        'It keeps the counts inside `int`.'
      ],
      0,
      'The input format guarantees a parent label below every child, so a reverse sweep accumulates to fully settled children before it touches a parent.'
    )
  ],
  // 08_Trees_and_LCA
  [
    q(
      'What does `for (int multiple = i * i; multiple <= n; multiple += i)` break at around i = 46,341?',
      [
        '`i * i` overflows signed int and starts the loop from a negative or wrong value.',
        'The step `i` overflows.',
        '`multiple` overflows first, at the loop body.',
        'The comparison to `n` wraps.'
      ],
      0,
      '2³¹−1 ≈ 46,341². Past that the product is UB and usually negative, so the loop never runs. `1LL * i * i` keeps it right.'
    ),
    q(
      'What does `power(a, b, 1)` return when the accumulator starts at `1 % mod`?',
      [
        '0, because every residue is 0 mod 1.',
        '1, because the accumulator starts at 1.',
        'Undefined: the modulus must exceed 1.',
        '`a`, untouched by the modulus.'
      ],
      0,
      '`1 % 1` is 0, and `base %= mod` is 0 too, so every multiplication stays 0. Starting at a bare `1` would wrongly return 1 for every call.'
    ),
    q(
      'A factorial table is precomputed to `n = 2·10⁶` modulo `10⁹+7`. Which part actually fails?',
      [
        'Nothing here: 2·10⁶ is below the modulus, so Fermat works.',
        'The products overflow `long long` before the modulo.',
        'Fermat requires the exponent to be composite.',
        'The table must start at 0 and skips index 1.'
      ],
      0,
      'Fermat’s inverse needs `a` coprime to `p`, i.e. `a < p`. With `n < MOD` every factorial value is coprime, so the scheme holds.'
    )
  ],
  // 09_Mathematics_and_Number_Theory
  [
    q(
      'A rolling hash keeps `long long h` with a modulus of 0 and relies on wrap-around. What appears?',
      [
        'A negative value whenever the product passes 2⁶³−1 (signed overflow is UB).',
        'Correct results, the wrap is guaranteed.',
        'Nothing until n exceeds LLONG_MAX.',
        'A float conversion error.'
      ],
      0,
      'Unsigned overflow is defined modulo 2⁶⁴; signed overflow is UB and the optimiser may fold it wrongly. Hash accumulators stay `unsigned long long`.'
    ),
    q(
      'Why does a KMP search fall back with `k = pi[k - 1]` after a full match instead of `k = 0`?',
      [
        '`k = 0` skips all overlapping occurrences.',
        'It prevents an out-of-bounds read of `pattern[k]`.',
        'It is the fastest possible assignment.',
        'It is only needed when the pattern is periodic.'
      ],
      0,
      'The following text can still overlap with a proper prefix of the pattern. The failure value keeps exactly that overlap; zeroing the state drops every overlapping occurrence.'
    ),
    q(
      'Inserting into `vector<array<int,26>>` while holding `int &next = children[node][c - \'a\']` across a `push_back`: what is the risk?',
      [
        'The outer vector may reallocate and leave `next` dangling.',
        'The 104-byte array is copied and breaks the neighbours.',
        'Nothing: only the inner arrays move.',
        'The reference is rebound to the new node automatically.'
      ],
      0,
      '`push_back` can free the old buffer and move everything. Re-index `children[node][c - \'a\']` after the push, or `reserve` the expected node count.'
    )
  ],
  // 10_String_Algorithms
  [
    q(
      'A Mo’s ordering sorts by block of `l` but never reverses on odd blocks. What is the cost?',
      [
        'The `r` end resets to the start of every block, roughly doubling the moves.',
        'The aggregate stops matching the window.',
        'The block size stops affecting the bound.',
        'Only readability suffers; the complexity is unchanged.'
      ],
      0,
      'Without the snake order, `r` sweeps back across the array for every new block. The reversal lets it continue from the previous block’s end.'
    ),
    q(
      'Why does the Nim winner come from the XOR of all pile sizes?',
      [
        'A non-zero XOR can always be zeroed by reducing one pile; a zero XOR cannot be zeroed at all.',
        'The XOR is the sum modulo 2 of the sizes.',
        'The maximum pile alone is not enough.',
        'Every pile is a power of two.'
      ],
      0,
      'From non-zero XOR, the pile owning the highest XOR bit can be reduced to restore zero; from zero every move creates a non-zero XOR. Zero is exactly the losing position.'
    ),
    q(
      'Misère Nim lets the last mover lose. Which condition flips the verdict compared to normal Nim?',
      [
        'Every pile has size 1: the all-ones parity decides.',
        'The XOR is a power of two.',
        'There are three piles.',
        'No condition: the XOR decides both versions.'
      ],
      0,
      'With all piles at 1 only single stones move, so the side facing an even count wins. Mixed sizes keep the normal-play XOR rule.'
    )
  ],
  // 11_Advanced_and_Niche_Techniques
  [
    q(
      'A constructive task asks for n distinct even-sum integers. Which class of answer trivially satisfies it?',
      [
        'The integers 1..n with any single value nudged by +1.',
        'All values equal to n.',
        'A random permutation of 1..n.',
        'The integers 1..n alone: they already are distinct.'
      ],
      0,
      'Distinctness comes from 1..n and one +1 fixes the sum’s parity, apart from the n = 1 edge. Equal values or a random permutation control neither property.'
    ),
    q(
      'Why can a `cerr` debug print be left in a submission that writes to `cout`?',
      [
        'Judges compare `stdout` only; `cerr` is separate.',
        'It interleaves cleanly with `cout` in every checker.',
        'It is always free, so nothing must be removed.',
        'It slows the program by less than 1 ms in total.'
      ],
      0,
      '`cerr` is unbuffered and separate from the compared `stdout`. A few lines are harmless; tight loops should buffer it or remove it.'
    ),
    q(
      'Which expression is the standard bit trick for the next power of two at or above x?',
      [
        '`x |= x >> 1; x |= x >> 2; x |= x >> 4; ... ; x + 1`',
        '`1 << countr_zero(x)`',
        '`-x & x`',
        '`x << 1`'
      ],
      0,
      'The shifts spread every set bit to the right; adding 1 carries out to the next power of two. C++20 wraps the same idea as `bit_ceil(x)`.'
    )
  ],
  // 12_Reference_and_Catalog
  [
    q(
      'Which of these is UB that a fast-I/O skeleton does not address?',
      [
        'Multiplying two values of 10⁹ into an `int` accumulator.',
        'Reading stdin with `cin` after `tie(nullptr)`.',
        'Writing `\'\\n\'` to `cout`.',
        'Calling `size()` on an empty vector.'
      ],
      0,
      'Signed overflow past 2³¹−1 is UB and may be optimised wrongly. Reading, newline output, and `size()` on an empty vector are all safe.'
    ),
    q(
      'What is `v[x]` after `int x; cin >> x;` when the read fails (empty input)?',
      [
        'Undefined: the input-failure branch leaves `x` uninitialised.',
        'Zero, because `int` is value-initialised.',
        'A compilation error for an unused variable.',
        'A thrown exception from `operator>>`.'
      ],
      0,
      'A bare `int x;` in a function body is uninitialised. A failed extraction writes nothing, so `v[x]` indexes garbage; initialise or check the stream.'
    ),
    q(
      'Why is `strlen(s.c_str())` avoided inside a tight character loop?',
      [
        '`s.size()` is stored and O(1), while `strlen` rescans until the NUL.',
        '`strlen` needs a trailing NUL that `std::string` no longer keeps.',
        'The two return different types and need a cast.',
        '`strlen` modifies its argument.'
      ],
      0,
      '`s.size()` is a field read; `strlen` walks the string each call, and a scan inside an O(n) loop is O(n²) overall.'
    )
  ]
]