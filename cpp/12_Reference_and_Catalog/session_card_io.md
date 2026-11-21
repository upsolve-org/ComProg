# Session Card: Input Parsing

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    long long m;
    cin >> n >> m;                                   // n declared first, then m
    vector<long long> a(n);
    for (auto &x : a) cin >> x;                      // one value per token
    string s;
    cin >> s;                                        // strings read whole, up to whitespace
    cout << a.size() << ' ' << m << ' ' << s << '\n';
}
```

- `>>` stops at whitespace; `getline(cin, s)` after a `>>` needs one `cin.ignore()`.
- Read `int` only when the value bound fits 32 bits; otherwise `long long`.
- Token order is the statement's order — read ahead before any logic.
- `'\n'` output, never `endl`, outside interactive problems.
- Interactive: `cout << flush` before each `cin >>`.