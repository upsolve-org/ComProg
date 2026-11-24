# Trie (Prefix Tree)

A trie stores a string set by shared prefixes: each node is a character step, and the path from the root spells the stored string. Insert and lookup are $O(\text{length})$.

---

## 1. Counting Inserted Words

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int q;
    cin >> q;
    vector<array<int, 26>> children(1);
    children[0].fill(-1);
    vector<int> count(1, 0);
    while (q--) {
        char type;
        string word;
        cin >> type >> word;
        if (type == 'i') {
            int node = 0;
            for (char c : word) {
                int next = children[node][c - 'a'];
                if (next == -1) {
                    next = (int)children.size();
                    children.push_back({});
                    children.back().fill(-1);
                    count.push_back(0);
                    children[node][c - 'a'] = next;      // re-index after the possible reallocation
                }
                node = next;
            }
            ++count[node];
        } else {
            int node = 0;
            for (char c : word) { node = children[node][c - 'a']; if (node == -1) break; }
            cout << (node == -1 ? 0 : count[node]) << '\n';
        }
    }
}
```

`vector<array<int,26>>` is compact to index, but `push_back` can reallocate and invalidate references. The insert loop copies the child index out of the array before pushing:

---

## 2. Array-of-Arrays vs Flat Pointers

The `array` form has a fixed 26-wide node (104 bytes); a `map<char,int>` node is smaller for sparse alphabets. A flat `vector<int> head, nextEdge` layout is the fastest but needs a struct for readability.

---

## 3. Longest Common Prefix Queries

Walk down as long as exactly one child exists and no word ends; the depth is the shared prefix of all words. A Trie + DFS also enumerates an alphabetically ordered set.

---

## 4. Memory Guard

Total node count is the total word length, not the word count. $2 \times 10^5$ words of 10 characters need $2 \times 10^6$ nodes — about 200 MB with 26-wide arrays. Switch to a sorted-vector-per-node or a `map` when the memory limit is 256 MB.

---

## 5. Complexity Notes

- Insert and lookup $O(L)$; total $O(\sum L)$.
- The 26-wide array makes the character step a single index operation.
- A `bitset` and a DFS over the trie answers "is any word accepted" style automaton questions.