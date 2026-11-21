# Z-Algorithm

`z[i]` is the length of the longest common prefix of `s` and `s[i..]`. With a window `[l, r)` of the longest match so far, every position inside the window reuses a mirror value and extends only past `r`.

---

## 1. Building `z`

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string s;
    cin >> s;
    int n = (int)s.size();
    vector<int> z(n, 0);
    for (int i = 1, l = 0, r = 0; i < n; ++i) {
        if (i < r) z[i] = min(r - i, z[i - l]);
        while (i + z[i] < n && s[z[i]] == s[i + z[i]]) ++z[i];
        if (i + z[i] > r) { l = i; r = i + z[i]; }
    }
    for (int value : z) cout << value << ' ';
    cout << '\n';
}
```

`z[0]` is 0 by convention. The loop is amortised $O(n)$ because `r` only grows.

---

## 2. Pattern Search

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string pattern, text;
    cin >> pattern >> text;
    string combined = pattern + '\x01' + text;       // separator not in either string
    int m = (int)pattern.size();
    vector<int> z(combined.size(), 0);
    for (int i = 1, l = 0, r = 0; i < (int)combined.size(); ++i) {
        if (i < r) z[i] = min(r - i, z[i - l]);
        while (i + z[i] < (int)combined.size() && combined[z[i]] == combined[i + z[i]]) ++z[i];
        if (i + z[i] > r) { l = i; r = i + z[i]; }
        if (z[i] >= m) cout << i - m << '\n';        // 0-based start in text
    }
}
```

A match is exactly `z[i] == m`; the separator stops a prefix from running through the pattern.

---

## 3. Distinct Substrings Count

Suffix-array free version: for every suffix start `i`, sort the suffixes by the pair `(rank[i], rank ...)` — the practical route is hashing or a suffix automaton. The Z-algorithm alone gives the LCP of each suffix with a **fixed** prefix, not with its predecessor.

---

## 4. Z-Algorithm vs KMP

- Same complexity, different information: `z` is "match length with the prefix at each position", KMP's `pi` is "partial match state".
- For pattern matching with a separator, Z reads naturally; for prefix counts, `pi` does.
- Building `combined` copies the text — watch memory at $10^6$ characters ($2$ MB, fine).

---

## 5. Complexity Notes

- $O(n + m)$ time, $O(n + m)$ memory.
- The `min(r - i, z[i - l])` clamp is what prevents a re-scan; dropping it gives the naive $O(n^2)$.
- `\x01` separator must not occur in the text (with lowercase letters any value below `'a'` works).