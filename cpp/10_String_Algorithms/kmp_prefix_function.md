# KMP and the Prefix Function

The prefix function `pi[i]` is the length of the longest proper prefix of `s[0..i]` that is also a suffix. It is the reusable "shift target" after a mismatch, which turns naive matching into $O(n + m)$.

---

## 1. Computing `pi`

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> prefixed(const string &s) {
    vector<int> pi(s.size(), 0);
    for (int i = 1, k = 0; i < (int)s.size(); ++i) {
        while (k && s[i] != s[k]) k = pi[k - 1];
        if (s[i] == s[k]) ++k;
        pi[i] = k;
    }
    return pi;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string s;
    cin >> s;
    for (int value : prefixed(s)) cout << value << ' ';
    cout << '\n';
}
```

---

## 2. Occurrence Search

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string pattern, text;
    cin >> pattern >> text;
    int m = (int)pattern.size();
    vector<int> pi(m, 0);
    for (int i = 1, k = 0; i < m; ++i) {
        while (k && pattern[i] != pattern[k]) k = pi[k - 1];
        if (pattern[i] == pattern[k]) ++k;
        pi[i] = k;
    }
    for (int i = 0, k = 0; i < (int)text.size(); ++i) {
        while (k && text[i] != pattern[k]) k = pi[k - 1];
        if (text[i] == pattern[k]) ++k;
        if (k == m) { cout << i - m + 2 << '\n'; k = pi[k - 1]; }
    }
}
```

`k = pi[k - 1]` after a match keeps overlapping occurrences; the output index is 1-based.

---

## 3. Shortest Period of a String

If `n % (n - pi[n - 1]) == 0`, the string is exactly `n / (n - pi[n - 1])` copies of a shorter block. Otherwise the shortest period is `n`.

```cpp
int n = (int)s.size();
int period = n - pi[n - 1];
cout << (n % period == 0 ? n / period : 1) << '\n';
```

---

## 4. Counting Prefix Occurrences

Every prefix of length `x` that `pi` can reach appears `1 + sum` of the `pi` chain from longer positions. Counting from the end upwards gives all prefix counts in $O(n)$:

```cpp
vector<long long> count(n + 1, 0);
for (int i = 0; i < n; ++i) ++count[pi[i]];
for (int i = n - 1; i >= 1; --i) count[pi[i - 1]] += count[i];
// count[length] is the number of occurrences of the prefix of that length
```

---

## 5. Complexity Notes

- Both phases are $O(n + m)$; `k` increases at most once per character and the `while` total is bounded by the increments.
- Memory $O(m)$ for the pattern array.
- The same array powers periodicity, borders, and "shortest compressible string" answers.