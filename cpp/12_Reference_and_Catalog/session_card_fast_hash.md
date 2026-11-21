# Session Card: Anti-Hash Hash Set

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
        return (size_t)mix(x + seed);
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    unordered_set<long long, SplitMix64> seen;
    int n;
    cin >> n;
    for (int i = 0, x; i < n; ++i) { cin >> x; seen.insert(x); }
    cout << seen.size() << '\n';
}
```

- `unordered_map` uses `pair<const K, V>` keys; the hash takes the key type only, so keep it narrow.
- `reserve(n)` reduces rehashes but does not fix a bad hash.
- A sorted `vector` plus `lower_bound` needs no hash at all and is CPU-cache friendly.
- `operator[]` default-inserts; `contains`/`count` do not.
- Iterator invalidation: insertion may rehash, so no references across inserts.