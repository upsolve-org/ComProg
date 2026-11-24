# Session Card: Local Stress Testing

```cpp
// gen.cpp — small random cases
#include <bits/stdc++.h>
using namespace std;

int main() {
    mt19937_64 rng(chrono::steady_clock::now().time_since_epoch().count());
    int n = 1 + rng() % 10;
    cout << n << '\n';
    for (int i = 0; i < n; ++i) cout << (long long)(rng() % 21) - 10 << " \n"[i + 1 == n];
}
```

```cpp
// brute.cpp — the obviously correct O(n^3) version
```

```sh
g++ -std=gnu++20 -O2 main.cpp -o main && g++ -std=gnu++20 -O2 brute.cpp -o brute && g++ -std=gnu++20 -O2 gen.cpp -o gen
for i in $(seq 1 500); do ./gen > in; ./main < in > out1; ./brute < in > out2; cmp -s out1 out2 || { echo "diff at $i"; break; }; done
```

- A fixed seed reproduces a failure; a random seed finds new ones. Keep the last failing input.
- Compare with `cmp`, then shrink the failing case by hand.
- Once a failure is found, run both binaries under `-fsanitize=address,undefined`.
- The brute force must be a different algorithm, not a faster copy of yours.