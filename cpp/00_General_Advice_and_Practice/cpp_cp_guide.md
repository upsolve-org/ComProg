# C++ in Competitive Programming: The Survival Guide

C++20 is the fastest language you can reasonably submit. It is also the one with the most ways to be silently wrong. This guide lists the rules that separate a working submission from a hackable one.

---

## 1. The Skeleton

Every submission starts from the same three lines, so muscle memory carries them.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    // ... solve ...
    cout << n << '\n';
}
```

- `ios::sync_with_stdio(false)` detaches the C++ streams from C stdio.
- `cin.tie(nullptr)` stops `cin` from flushing `cout` before every read.
- `'\n'` never forces a flush; `endl` does.

---

## 2. Undefined Behaviour Is Not "Probably Fine"

The optimiser assumes UB never happens. When it does, results are arbitrary and differ between `-O0` and `-O2`.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int x;
    cin >> x;                       // x = 2000000000
    cout << x * 2 << '\n';          // UB: 4e9 does not fit in int

    long long big = x;
    cout << big * 2 << '\n';        // 4000000000
}
```

The three recurring sources: signed overflow, out-of-bounds indexing, and reading an uninitialised variable.

---

## 3. 64-Bit Accumulators by Default

- Values are up to $10^9$; $n$ is up to $2 \times 10^5$; sums reach $2 \times 10^{14}$.
- Make the accumulator, not just the answer, `long long`.
- For products of two $10^9$ values use `long long` (or `__int128` for products of products).

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    long long sum = 0, sumSq = 0;
    for (int i = 0, x; i < n; ++i) {
        cin >> x;
        sum += x;
        sumSq += 1LL * x * x;       // 1LL lifts the multiplication to 64 bits
    }
    cout << sum << ' ' << sumSq << '\n';
}
```

---

## 4. Harden `unordered_map` Against Anti-Hash Tests

`std::unordered_map` with default hashing on `int` is the identity function, and stdlib bucket counts are ordinary primes. A hacker can produce thousands of keys in one bucket and turn $O(1)$ into $O(n)$ per lookup. A fixed 64-bit mixer removes the exploit.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct SplitMix64 {
    static uint64_t splitmix64(uint64_t x) {
        x += 0x9e3779b97f4a7c15ULL;
        x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
        x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
        return x ^ (x >> 31);
    }
    size_t operator()(uint64_t x) const {
        static const uint64_t seed = chrono::steady_clock::now().time_since_epoch().count();
        return splitmix64(x + seed);
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    unordered_map<long long, int, SplitMix64> count;
    int n;
    cin >> n;
    for (int i = 0, x; i < n; ++i) { cin >> x; ++count[x]; }
    cout << count.size() << '\n';
}
```

- If you need a deterministic order anyway, sort and use `vector`: no hashing, no attack surface.
- `gp_hash_table` from an extension header is faster still, but non-portable.

---

## 5. Recursion Depth

The default 8 MB stack holds roughly $10^5$ to $2 \times 10^5$ small frames. Deeper DFS on $2 \times 10^5$ vertices can still blow it, so prefer an explicit stack.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<vector<int>> adj(n);
    for (int i = 0; i < n - 1; ++i) {
        int u, v;
        cin >> u >> v;
        --u, --v;
        adj[u].push_back(v);
        adj[v].push_back(u);
    }
    vector<int> parent(n, -2), order;
    order.reserve(n);
    parent[0] = -1;
    order.push_back(0);
    for (size_t i = 0; i < order.size(); ++i) {      // BFS-style explicit growth
        int u = order[i];
        for (int v : adj[u])
            if (parent[v] == -2) { parent[v] = u; order.push_back(v); }
    }
    cout << order.size() << '\n';
}
```

---

## 6. Iterators Are Pointers with Rules

- `vector::push_back` may reallocate and invalidate every iterator and reference.
- `erase` invalidates the erased position and everything after it.
- Range-for over a container you mutate is a bug; index instead.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    vector<int> v = {1, 2, 3, 4, 5, 6};
    for (size_t i = 0; i < v.size();) {              // erase-in-place pattern
        if (v[i] % 2 == 0) v.erase(v.begin() + i);   // no iterator kept across erase
        else ++i;
    }
    for (int x : v) cout << x << ' ';
    cout << '\n';
}
```

---

## 7. `std::set` and `std::map` Members

On an ordered container the member functions are the $O(\log n)$ ones. `std::lower_bound(set.begin(), set.end(), x)` is $O(n)$ on a bidirectional iterator and defeats the point.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    set<int> s = {10, 20, 30};
    auto it = s.lower_bound(15);      // O(log n), first element >= 15
    if (it != s.end()) cout << *it << '\n';
}
```

---

## 8. Fixed-Width Bit Sets

`std::bitset<64>` compiles to single instructions; `vector<bool>` is a bit-packed specialisation with proxy references.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    unsigned long long mask;
    cin >> mask;
    bitset<64> bits(mask);
    cout << bits.count() << '\n';                 // number of set bits
    cout << popcount(mask) << '\n';               // same answer without copies
}
```

---

## 9. Floating Point Answers

When the answer is real, print with fixed precision and compare within an epsilon; never compare with `==`.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    double a, b;
    cin >> a >> b;
    cout << fixed << setprecision(10) << a / b << '\n';
}
```

---

## 10. Compile Flags That Catch Bugs Early

- `-Wall -Wextra` locally to see unused and signed/unsigned mixes.
- `-fsanitize=address,undefined -g` while stress testing.
- `-D_GLIBCXX_DEBUG` turns STL misuse into a runtime error instead of memory corruption.
- Submit with none of them: they cost time.