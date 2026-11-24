# Bitwise Operations and `<bit>`

Signed-shift behaviour is defined in C++20, but `unsigned long long` is still the safe home for masks: no sign bit, no widening surprises.

---

## 1. Mask Building

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int low, high;
    cin >> low >> high;                              // inclusive, 0 <= low <= high < 64
    unsigned long long mask = (1ULL << (high - low + 1)) - 1;
    mask <<= low;
    cout << mask << '\n';
}
```

`1ULL << 64` would be undefined; for the full 64-bit mask use `~0ULL`.

---

## 2. Isolating and Clearing Bits

```cpp
unsigned lowbit = x & -x;                         // lowest set bit (wrap-around negation)
x &= x - 1;                                       // clear the lowest set bit
bool isPowerOfTwo = x && !(x & (x - 1));
```

`x & -x` relies on two's complement modulo arithmetic; with `unsigned` the negation is `~x + 1` with the same result.

---

## 3. Subset Enumeration

```cpp
for (unsigned sub = mask; sub; sub = (sub - 1) & mask)
    visit(sub);
visit(0);                                          // the empty set, outside the loop
```

---

## 4. `<bit>` in C++20

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    unsigned long long x, y;
    cin >> x >> y;
    cout << popcount(x) << '\n';                   // set bits
    cout << countr_zero(x) << '\n';                // trailing zeros, 64 for x = 0
    cout << countl_zero(x) << '\n';                // leading zeros, 64 for x = 0
    cout << bit_ceil(x) << '\n';                   // next power of two >= x
    cout << rotl(y, 5) << '\n';                    // rotate left by 5
}
```

`countr_zero(0)` and `countl_zero(0)` return the width, which is exactly the sentinel a search wants.

---

## 5. XOR Cascades

XOR is its own inverse: `x ^ y ^ y == x`. Prefix-XOR range queries use it (`prefix[r] ^ prefix[l - 1]`), and each value appearing twice cancels.

---

## 6. Complexity Notes

- Every bitwise operator and every `<bit>` function is a single instruction on x86-64.
- `std::popcount` compiles to `popcnt` with `-mpopcnt`; without it the call costs a few more ticks.
- Bitboard DP over `bitset<64>` beats a `bool[64]` array by 64×.