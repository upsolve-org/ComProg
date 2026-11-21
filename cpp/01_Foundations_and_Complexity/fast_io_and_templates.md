# Fast I/O and the Submission Template

## 1. The Untied Streams

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<int> a(n);
    for (auto &x : a) cin >> x;
    cout << accumulate(a.begin(), a.end(), 0LL) << '\n';
}
```

- `sync_with_stdio(false)` removes the per-operation lock between `cin` and C `stdin`.
- `tie(nullptr)` removes the pre-read `cout` flush.
- Together they make `cin`/`cout` competitive with `scanf`/`printf` on $10^6$ tokens.

## 2. One Output Write per Token Is Slow

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string out;
    out.reserve(1 << 20);                       // one megabyte of head room
    int n;
    cin >> n;
    for (int i = 1, x; i <= n; ++i) {
        cin >> x;
        out += to_string(x);
        out += (i == n ? '\n' : ' ');
    }
    cout << out;                                // single write at the end
}
```

An `ostringstream` with `.str()` works the same way.

## 3. Bulk Reading When the Format Allows It

If the whole input is integers, reading tokens in bulk avoids `operator>>` formatting overhead.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string data((istreambuf_iterator<char>(cin)), istreambuf_iterator<char>());
    long long sum = 0;
    bool inNumber = false, negative = false;
    long long value = 0;
    for (char c : data) {
        if (c == '-') { negative = true; continue; }
        if (isdigit((unsigned char)c)) {
            inNumber = true;
            value = value * 10 + (c - '0');
            continue;
        }
        if (inNumber) {
            sum += negative ? -value : value;
            inNumber = false;
            negative = false;
            value = 0;
        }
    }
    if (inNumber) sum += negative ? -value : value;
    cout << sum << '\n';
}
```

## 4. What the Template Should Not Do

- Do not `#define int long long` globally: memory doubles for big vectors and `std::sort` loses throughput.
- Do not put `#include`s inside `main`.
- Do not leave `-D_GLIBCXX_DEBUG` on for submission; it is fine while stress testing.

## 5. Complexity Notes

- Text parsing is $\Theta(\text{bytes})$; storing the whole input costs as many bytes.
- Build the output in one buffer, then a single `cout <<` — flushing per line is $\Theta(n)$ syscalls.
- `'\n'` is a byte; `endl` adds a flush.