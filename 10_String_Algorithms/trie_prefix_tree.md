---
tags:
  - cp/code
  - cp/string
---

[[ComProg/Home|🏠 Dashboard]] ❯ [[ComProg/10_String_Algorithms/README|10_String_Algorithms]] ❯ **Trie Prefix Tree**

---

# Trie Prefix Tree

> [!abstract] Implementation Note
> This note contains the complete, battle-tested Python implementation of **Trie Prefix Tree**.
> Source file: `ComProg/10_String_Algorithms/trie_prefix_tree.py`
> Run test runner: `python3 run_tests.py ComProg/10_String_Algorithms/trie_prefix_tree.py`

---

## 🐍 Python Implementation

```python
"""
Trie (Prefix Tree) & Binary Trie in Python
1. String Trie: Word insertion & prefix matching
2. Binary Trie: Maximum XOR with a query number in O(bits)
"""

import sys

class StringTrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class StringTrie:
    def __init__(self):
        self.root = StringTrieNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = StringTrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end

    def starts_with(self, prefix):
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True

class BinaryTrie:
    """
    Binary Trie for non-negative integers up to 2^BITS.
    Supports inserting numbers and querying max XOR with x in O(BITS).
    """
    def __init__(self, bits=30):
        self.bits = bits
        # children[0] and children[1] represented as lists of length 2
        # Use flat list or dict for nodes
        self.trie = [{0: None, 1: None}]

    def insert(self, num):
        node = 0
        for b in range(self.bits - 1, -1, -1):
            bit = (num >> b) & 1
            if self.trie[node][bit] is None:
                self.trie[node][bit] = len(self.trie)
                self.trie.append({0: None, 1: None})
            node = self.trie[node][bit]

    def query_max_xor(self, x):
        """Finds max(x ^ val) for all val inserted into trie."""
        node = 0
        ans = 0
        for b in range(self.bits - 1, -1, -1):
            bit = (x >> b) & 1
            desired = 1 - bit
            if self.trie[node][desired] is not None:
                ans |= (1 << b)
                node = self.trie[node][desired]
            else:
                node = self.trie[node][bit]
        return ans

TEST_CASES = [
    (
        "3 1\n3 10 5\n5",
        "15"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    it = iter(tokens)
    n = int(next(it))
    q = int(next(it))
    trie = BinaryTrie(30)
    for _ in range(n):
        val = int(next(it))
        trie.insert(val)
    out = []
    for _ in range(q):
        x = int(next(it))
        out.append(str(trie.query_max_xor(x)))
    sys.stdout.write("\n".join(out) + "\n")

if __name__ == "__main__":
    solve()
```

---

## ⚡ Complexity & Analysis
- **Time Complexity:** See docstrings and implementation above.
- **Space Complexity:** See docstrings and implementation above.

---

⏮️ [[ComProg/10_String_Algorithms/README|Back to 10_String_Algorithms]] | 🏠 [[ComProg/Home|Dashboard]]
