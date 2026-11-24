---
tags:
  - cpp/strings
---

[[Home|🏠 Dashboard]] ❯ **C++ Module 10: String Algorithms**

---

# C++ Module 10: String Algorithms

String work in C++ is bulk work: `std::string` scans are vectorised, and a per-character loop is only worth it when the algorithm needs the inner structure. All algorithms here are linear; the danger is a hidden quadratic, such as `s = s + c` or `find` in a loop.

---

## 🎯 KMP Prefix Function

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string pattern, text;
    cin >> pattern >> text;
    int m = (int)pattern.size();
    vector<int> failure(m, 0);
    for (int i = 1, k = 0; i < m; ++i) {
        while (k && pattern[i] != pattern[k]) k = failure[k - 1];
        if (pattern[i] == pattern[k]) ++k;
        failure[i] = k;
    }
    int count = 0;
    for (int i = 0, k = 0; i < (int)text.size(); ++i) {
        while (k && text[i] != pattern[k]) k = failure[k - 1];
        if (text[i] == pattern[k]) ++k;
        if (k == m) { ++count; k = failure[k - 1]; }        // overlaps allowed
    }
    cout << count << '\n';
}
```

---

## 🧭 Z-Algorithm

`z[i]` is the longest common prefix of `s` and `s[i:]`.

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

The `if (i < r)` copy is what keeps the total work linear.

---

## 🪢 Polynomial Rolling Hash

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string s;
    cin >> s;
    constexpr unsigned long long BASE = 131, MOD = (1ULL << 61) - 1;
    auto multiply = [](unsigned long long a, unsigned long long b) {
        __uint128_t product = (__uint128_t)a * b;
        unsigned long long reduced = (unsigned long long)(product >> 61) + (unsigned long long)(product & MOD);
        return reduced >= MOD ? reduced - MOD : reduced;
    };
    vector<unsigned long long> prefix(s.size() + 1, 0);
    for (size_t i = 0; i < s.size(); ++i) prefix[i + 1] = (multiply(prefix[i], BASE) + s[i]) % MOD;
    cout << prefix[s.size()] << '\n';
}
```

For substrings precompute `power[i] = BASE^i mod MOD` once, then `(prefix[r] + MOD - prefix[l] * power[r - l] % MOD) % MOD`.

---

## 🌳 Trie

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int q;
    cin >> q;
    vector<array<int, 26>> children(1);
    children[0].fill(-1);
    vector<int> count(1, 0);
    while (q--) {
        char type;
        string word;
        cin >> type >> word;
        if (type == 'i') {
            int node = 0;
            for (char c : word) {
                int &next = children[node][c - 'a'];
                if (next == -1) { next = (int)children.size(); children.push_back({}); children.back().fill(-1); count.push_back(0); }
                node = next;
            }
            ++count[node];
        } else {
            int node = 0;
            for (char c : word) node = node == -1 ? -1 : children[node][c - 'a'];
            cout << (node == -1 ? 0 : count[node]) << '\n';
        }
    }
}
```

A `vector<array<int,26>>` indexes without hashing; for a binary alphabet the array shrinks to two.

---

## 📄 String Building

`reserve` and `append` keep a build linear; `s = s + c` inside a loop reallocates each time and is quadratic.

```cpp
string out;
out.reserve(text.size());
for (char c : text) if (c != ' ') out.push_back(c);
```

---

## ⏱️ Complexity Notes

- KMP and Z are $O(n + m)$; KMP's failure array is the reusable overlap structure.
- Hashing is $O(n)$ with one or two 64-bit moduli; a single 64-bit modulus is hackable, twins are not in practice.
- A trie costs one node per character inserted, $O(total length)$.
- `std::string::find` in a loop is $O(nm)$ worst case; KMP is the linear replacement.

---

## ✅ Checklist

- Pattern length `m = 0` handled before indexing `pattern[0]`.
- KMP resets `k = failure[k - 1]` after a full match.
- Hash power tables computed once, not per substring.

---

## Included Source Files

- `polynomial_rolling_hash.md`, `kmp_prefix_function.md`, `z_algorithm.md`, `trie_prefix_tree.md`