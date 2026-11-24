# Session Card: Output

- One `'\n'` per line; never `endl`.
- Build big output in a `string` with `reserve`, then one `cout <<`.
- "Any valid answer" still needs the exact format.
- Floats: `fixed << setprecision(n)` with a stated precision.
- Empty result: print whatever the statement says (`0`, `-1`, nothing plus a newline).
- Interactive: flush after each line (`cout << ... << flush`) and read the reply immediately.
- Space-or-newline between values: `" \n"[i + 1 == n]` is shorter than a branch.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    string out;
    out.reserve(n * 8);
    for (int i = 1; i <= n; ++i) { out += to_string(i); out += (i == n ? '\n' : ' '); }
    cout << out;
}
```

Trailing spaces are tolerated by almost every checker; trailing text is not.