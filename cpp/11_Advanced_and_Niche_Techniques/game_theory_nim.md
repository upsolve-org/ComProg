# Nim and the Grundy Number

Normal-play impartial games reduce to the XOR of their component Grundy numbers. For a Nim pile of size $s$ the Grundy number is $s$, so the position is losing exactly when the XOR of all piles is zero.

---

## 1. Winner Test

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    long long xorSum = 0;
    for (int i = 0, x; i < n; ++i) { cin >> x; xorSum ^= x; }
    cout << (xorSum ? "First" : "Second") << '\n';
}
```

---

## 2. Why the Zero XOR Loses

- Non-zero XOR: take the pile whose highest set bit matches the XOR's highest set bit and reduce it to `pile ^ xorSum < pile`. The new XOR is 0.
- Zero XOR: any move from pile `s` to `t < s` makes the XOR `s ^ t > 0`.

The two statements make "zero XOR" exactly the losing positions.

---

## 3. Misère Nim

The same XOR test, except that when **every** pile has size 1 the winner is inverted:

```cpp
bool allOnes = ranges::all_of(pile, [](long long p) { return p == 1; });
bool firstWins = allOnes ? (n % 2 == 0) : xorSum != 0;
```

---

## 4. Grundy Numbers for Other Moves

A pile where you may remove up to $k$ stones has Grundy $s \bmod (k + 1)$. Compute Grundy numbers with the mex rule:

```cpp
constexpr int LIMIT = 1000;
vector<int> grundy(LIMIT + 1, 0);
for (int s = 1; s <= LIMIT; ++s) {
    vector<char> seen(LIMIT + 2, 0);
    for (int move = 1; move <= min(s, 3); ++move) seen[grundy[s - move]] = 1;
    while (seen[grundy[s]]) ++grundy[s];
}
```

The whole position is the XOR of its pile Grundies.

---

## 5. Complexity Notes

- Winner test $O(n)$; Grundy precomputation $O(\text{limit} \cdot k)$.
- Sprague–Grundy splits a game into independent parts; dependent parts are not a plain XOR.
- Normal play versus misère changes the all-ones rule; check which the statement asks for.
- `ranges::all_of` needs a range, not a size; `pile` is a `vector<long long>`.