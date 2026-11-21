# Greedy Templates and Exchange Arguments

A greedy algorithm is only correct when a local choice can be exchanged for the first choice of an optimal solution. Each template below ships with its argument; copy the argument, not just the code.

---

## 1. Earliest Finish Time

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<pair<long long, long long>> events(n);          // (end, start)
    for (auto &[end, start] : events) cin >> start >> end;
    sort(events.begin(), events.end());
    long long last = LLONG_MIN;
    int taken = 0;
    for (auto [end, start] : events)
        if (start >= last) { last = end; ++taken; }
    cout << taken << '\n';
}
```

**Exchange.** Let $e$ be the first interval of an optimal set and $g$ the one with the smallest end. $g$ ends not later than $e$, so replacing $e$ by $g$ keeps every later interval feasible.

---

## 2. Deadline Scheduling with a Min-Heap

Maximise the number of jobs finished before their deadlines.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<pair<long long, long long>> jobs(n);            // (deadline, duration)
    for (auto &[deadline, duration] : jobs) cin >> duration >> deadline;
    sort(jobs.begin(), jobs.end());
    priority_queue<long long> chosen;                       // durations, largest on top
    long long total = 0;
    for (auto [deadline, duration] : jobs) {
        total += duration;
        chosen.push(duration);
        if (total > deadline) { total -= chosen.top(); chosen.pop(); }
    }
    cout << chosen.size() << '\n';
}
```

**Exchange.** Keep the shortest set for every prefix. A longer job that finishes later can always be swapped for a shorter one without losing feasibility.

`std::priority_queue<long long>` is a max-heap; `priority_queue<long long, vector<long long>, greater<long long>>` is the min-heap.

---

## 3. Sorting by Ratio

Least cost per unit first:

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    long long budget;
    cin >> n >> budget;
    vector<pair<long long, long long>> items(n);            // (cost, value)
    for (auto &[cost, value] : items) cin >> cost >> value;
    sort(items.begin(), items.end(), [](const auto &a, const auto &b) {
        return (__int128)a.first * b.second < (__int128)b.first * a.second;   // cost/value
    });
    long long value = 0;
    for (auto [cost, v] : items)
        if (cost <= budget) { budget -= cost; value += v; }
    cout << value << '\n';
}
```

`__int128` avoids a floating-point ratio and its rounding ties.

---

## 4. When Greedy Is Wrong

- 0/1 knapsack by value density (a greedy fill misses better combinations) — needs DP.
- Shortest path with arbitrary weights by "fewest hops" — needs Dijkstra.
- Coin change with non-canonical coins — needs DP.

Test the greedy against a brute force on small random data before trusting it.

---

## 5. Complexity Notes

- Greedy plus sort is $O(n \log n)$; the heap variant adds a log per item.
- A contrast with DP is the usual interview test: greedy has no table and cannot backtrack.
- Overflow in the exchanged cost keeps a `long long`, and the cross-product ratio check needs `__int128`.