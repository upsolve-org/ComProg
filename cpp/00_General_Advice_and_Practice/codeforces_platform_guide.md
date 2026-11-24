# The Codeforces Platform: Submission, Verdicts and Hacks

Codeforces runs two kinds of round. In a **rated** round, other contestants can read your submission after the round ends and submit counter-tests (**hacks**); during the round, Div. 2 C and later are sealled behind room review. On an **Educational** round or an **ICPC**-style contest, there is no hacking. The rules below matter mostly in the first kind.

---

## 1. The Verdict Alphabet

| Verdict | Means | Where to look |
|---|---|---|
| WA | wrong answer on test $k$ | the logic, not the code |
| TLE | time limit exceeded | the complexity, not micro-optimisation first |
| RE | runtime error | out-of-bounds, division by zero, deep recursion |
| MLE | memory limit | over-allocated arrays, `bitset` of $10^9$ |
| CE | compilation error | read the first error line only |

The test number tells you *where* it broke, not *why*. Reproduce it small.

---

## 2. Hacking Is a Directed Attack

A hacker reads your code and builds the one input that breaks it. The usual attacks, each with the defence:

- **Hash flooding.** Thousands of keys hashing to one bucket. Defence: a splitmix64 hash with a random seed.
- **Worst case of a "$O(\log n)$ expected" structure.** Defence: amortised or worst-case structures where the bound is required.
- **Deep recursion.** A path graph of $2 \times 10^5$ vertices for a recursive DFS. Defence: an explicit stack.
- **Signed overflow.** The maximum value on the constraint. Defence: `long long`.
- **`while (x != target)` loops.** An input that never reaches the target. Defence: a bounded loop counter.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct SplitMix64 {
    static uint64_t mix(uint64_t x) {
        x += 0x9e3779b97f4a7c15ULL;
        x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
        x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
        return x ^ (x >> 31);
    }
    size_t operator()(uint64_t x) const {
        static const uint64_t seed = chrono::steady_clock::now().time_since_epoch().count();
        return mix(x + seed);
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    unordered_map<int, int, SplitMix64> seen;   // survives an anti-hash hack
    int n;
    cin >> n;
    long long answer = 0;
    for (int i = 0, x; i < n; ++i) {
        cin >> x;
        answer += seen[x];
        ++seen[x];
    }
    cout << answer << '\n';
}
```

---

## 3. Test Locally Before the Clock Runs

- Rewrite the sample inputs into files and diff against expected output.
- Stress-test with a brute force on tiny random cases (see the practice section of the module README).
- Compile once with sanitizers: `g++ -O1 -g -fsanitize=address,undefined main.cpp`.
- Read the constraints again after the solution is written; five minutes here saves a TLE.

```sh
g++ -std=gnu++20 -O2 main.cpp -o main
printf '4\n-2 1 -3 4\n' | ./main
```

---

## 4. Order of Reading a Statement

1. Input format — what arrives first, what delimits what.
2. Constraints — the complexity budget and the overflow budget.
3. Output rule — exact token, one per line, or a whole number.
4. Samples — prediction before running.

---

## 5. Etiquette Under Pressure

- Commit to a plan for five minutes before switching problems.
- When stuck, write the invariant you cannot prove; it usually names the bug.
- After a WA, generate a counter-test yourself instead of resubmitting a hunch; each wrong submission costs rating and time.