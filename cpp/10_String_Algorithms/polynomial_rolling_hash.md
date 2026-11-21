# Polynomial Rolling Hash

A rolling hash maps a string to an integer so substring equality becomes an integer comparison. Use two independent 64-bit hashes (or one mod $2^{61}-1$ with two bases) — a single 64-bit hash is brute-forceable by anyone who reads it.

---

## 1. Build Prefix Hashes

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string s;
    cin >> s;
    constexpr unsigned long long BASE = 131;
    vector<unsigned long long> prefix(s.size() + 1, 0), power(s.size() + 1, 1);
    for (size_t i = 0; i < s.size(); ++i) {
        prefix[i + 1] = prefix[i] * BASE + (unsigned char)s[i];   // wraps mod 2^64
        power[i + 1] = power[i] * BASE;
    }
    auto hashOf = [&](size_t l, size_t r) { return prefix[r] - prefix[l] * power[r - l]; };
    // hashOf(l, r) == hashOf(l2, r2) when the substrings are equal (almost surely)
    cout << hashOf(0, s.size()) << '\n';
}
```

`unsigned` wrap-around replaces the modulus; `(unsigned char)` keeps signed `char` values stable.

---

## 2. Double Hash

```cpp
pair<unsigned long long, unsigned long long> hashOf(size_t l, size_t r) {
    return {first[r] - first[l] * power1[r - l],
            second[r] - second[l] * power2[r - l]};
}
```

Two different bases over the same wrap-around modulus already give a $2^{128}$ collision space; compare pairs.

---

## 3. Counting Distinct Substrings of a Given Length

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string s;
    cin >> s;
    int k;
    cin >> k;
    constexpr unsigned long long BASE = 131;
    vector<unsigned long long> prefix(s.size() + 1, 0), power(s.size() + 1, 1);
    for (size_t i = 0; i < s.size(); ++i) {
        prefix[i + 1] = prefix[i] * BASE + (unsigned char)s[i];
        power[i + 1] = power[i] * BASE;
    }
    vector<unsigned long long> hashes;
    for (size_t i = 0; i + k <= s.size(); ++i) hashes.push_back(prefix[i + k] - prefix[i] * power[k]);
    sort(hashes.begin(), hashes.end());
    cout << unique(hashes.begin(), hashes.end()) - hashes.begin() << '\n';
}
```

---

## 4. Anti-Hash Defence

- Fixed bases are known; use two random odd bases chosen at run time (`chrono` seed, `mt19937`).
- Mod $2^{64}$ is still susceptible to the Thue–Morse construction for small bases.
- For parity with C++ judges, `__uint128`-reduced mod $2^{61}-1$ plus a random base removes the Thue–Morse family.

---

## 5. Complexity Notes

- Build $O(n)$, substring hash $O(1)$, memory $O(n)$.
- Verify the final answer by comparing the actual substring before printing when a collision would be fatal.
- `unsigned long long` overflow is defined modulo $2^{64}$; `long long` would be UB.