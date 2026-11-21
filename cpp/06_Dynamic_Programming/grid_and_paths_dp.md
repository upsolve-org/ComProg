# Grid and Path DP

Grid DP counts or optimises paths where every move goes forward (right/down). The state is the cell, the transition is the two predecessors, and the answer lands in the last cell.

---

## 1. Counting Open Right/Down Paths

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int h, w;
    cin >> h >> w;
    constexpr int MOD = 1'000'000'007;
    vector<vector<int>> ways(h, vector<int>(w, 0));
    for (int r = 0; r < h; ++r) {
        string line;
        cin >> line;
        for (int c = 0; c < w; ++c) {
            if (line[c] == '#') continue;                    // wall: ways stays 0
            if (r == 0 && c == 0) { ways[r][c] = 1; continue; }
            long long sum = 0;
            if (r > 0) sum += ways[r - 1][c];
            if (c > 0) sum += ways[r][c - 1];
            ways[r][c] = (int)(sum % MOD);
        }
    }
    cout << ways[h - 1][w - 1] << '\n';
}
```

A wall is never relaxed, so it contributes 0 to both successors.

---

## 2. Rolling Rows

Only the previous row is needed, so one row of width `w` suffices:

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int h, w;
    cin >> h >> w;
    constexpr int MOD = 1'000'000'007;
    vector<long long> row(w, 0);
    vector<string> grid(h);
    for (auto &line : grid) cin >> line;

    row[0] = 1;
    for (int r = 0; r < h; ++r) {
        for (int c = 0; c < w; ++c) {
            if (grid[r][c] == '#' || (r == 0 && c == 0)) { if (!(r == 0 && c == 0 && grid[r][c] != '#')) row[c] = 0; continue; }
            if (c > 0) row[c] = (row[c] + row[c - 1]) % MOD;   // row[c] still holds the row above
        }
    }
    cout << row[w - 1] << '\n';
}
```

`row[c]` is read before it is overwritten, so it is always the value from the row above at that point in the loop.

---

## 3. Minimising Cost with a Large Cell

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int h, w;
    cin >> h >> w;
    vector<vector<long long>> cost(h, vector<long long>(w));
    for (auto &row : cost) for (auto &x : row) cin >> x;
    for (int r = 0; r < h; ++r)
        for (int c = 0; c < w; ++c) {
            if (r == 0 && c == 0) continue;
            long long from = LLONG_MAX;
            if (r > 0) from = min(from, cost[r - 1][c]);
            if (c > 0) from = min(from, cost[r][c - 1]);
            cost[r][c] += from;
        }
    cout << cost[h - 1][w - 1] << '\n';
}
```

Reusing the input matrix as the DP table is fine when the input is not needed again.

---

## 4. When the Move Set Changes

- Four-directional moves on a walled grid are not a DP; BFS with 0/1 costs (`deque`) or Dijkstra is needed.
- Diagonal moves add the two or three extra predecessors.
- Moves up/right/left but exactly once: profile DP or a layered graph.

---

## 5. Complexity Notes

- $O(hw)$ states and constant transitions; memory $O(hw)$ or $O(w)$ with a rolling row.
- Cell counts above $10^7$ need the rolling row.
- Modulo every addition keeps `int`; unmolded sums need `long long`.