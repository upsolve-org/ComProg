# ComProg

ComProg is a self-paced competitive programming course in Python. Its 12 teaching chapters follow a sequence of concepts, worked implementations, and an assignment. Use the lesson menu or the previous and next controls to move through a chapter. Drafts, lesson positions, and accepted assignments are saved in the browser.

## Run the website

Requires Node.js 24 or later.

```sh
npm ci
npm run dev
```

Open [localhost:3000](http://127.0.0.1:3000). For a production build, run `npm run build` followed by `npm start` behind your reverse proxy. Run executes Python with your custom input in an isolated browser worker using Pyodide from jsDelivr.

### Enable submissions

Use a dedicated host with a rootless Linux Docker engine, load a trusted Python image such as `python:3.12-slim`, and set `JUDGE_IMAGE` in `.env` to the loaded image tag or digest. The course server uses that Docker context. Restart it after configuring the image.

Submit runs each hidden input in a fresh, resource-limited container. The browser receives only a verdict and, when applicable, whether the failure occurred during a correctness or large-input check. Large inputs can catch approaches that do too much work. Passing them does not prove an asymptotic bound. With no judge image configured, learners can still read lessons and run custom inputs.

To enable OpenCode hint selection, copy `.env.example` to `.env` and provide a server-side OpenCode Console API key. The default endpoint uses the chat-completions API. Override `OPENCODE_ENDPOINT` and `OPENCODE_MODEL` together if your deployment uses a different compatible endpoint. OpenCode receives the question, exercise statement, and available hints. The UI displays a reviewed question selected by the model, or a course hint if inference is unavailable.

Run `npm test` to verify tutor and judge behavior.

## Edit the course

Every taught guide across all 13 modules includes a full-width Manim video with Gemini narration, English WebVTT captions, clickable chapter timestamps, narration transcripts, and the full written lesson. Each chapter also includes interactive multiple-choice concept quizzes alongside the end-of-chapter coding assignment. The rendered media ships with the website. Playback uses the local assets and requires no Gemini credential.

To regenerate the videos, edit the scripts in `site/video/lessons.json`. With `GEMINI_API_KEY` set in your shell, run `node site/video/narrate.mjs <audio-directory>`. Set `AUDIO_DIR` to that directory, then render scenes from `site/video/scenes.py` with `manim -qm` using Manim Community 0.22. Copy the rendered MP4s into `site/public` and rebuild. Rendering also refreshes the WebVTT captions there.

The site reads the numbered folders' `README.md` and individual notes. Duplicate module indexes, vault navigation, raw Python files, and planning documents are outside the built site. Edit chapter quizzes in [site/quizzes.mjs](site/quizzes.mjs), exercise statements and tutor hints in [site/labs.mjs](site/labs.mjs), and additional hidden checks in [site/judge-cases.mjs](site/judge-cases.mjs). Rebuild when course content changes.

## Original curriculum
Welcome to your complete, hands-on Competitive Programming repository built from scratch in Python!

This repository is modeled directly on the curated knowledge tree of the **[Codeforces Catalog](https://codeforces.com/catalog)**. It provides structured folders, battle-tested Python templates, clear explanations, complexity guides, and practical test cases for every core topic in competitive programming.

---

## 🎯 Learning Path & Progression Roadmap

| Phase | Target Rating | Focus Topics | Recommended Problem Sources |
|---|---|---|---|
| **Phase 0: Foundations** | 0 – 1000 (Newbie) | Fast I/O, Basic Math, Arrays, Strings, Simulation, Big-O Complexity | Codeforces Div 4 (A–C), AtCoder ABC (A–B) |
| **Phase 1: Core Techniques** | 1000 – 1200 (Pupil) | Two Pointers, Sliding Window, Binary Search on Answer, Prefix Sums, Greedy | Codeforces Div 3 (A–D), CSES Sorting & Searching |
| **Phase 2: Fundamental DS & Algorithms** | 1200 – 1400 (Specialist) | DSU, Fenwick Tree, BFS/DFS, Shortest Paths (Dijkstra), Basic DP (Knapsack, LIS), Number Theory | Codeforces Div 3 (D–F) / Div 2 (A–C), CSES Graph & DP |
| **Phase 3: Advanced Problem Solving** | 1400 – 1600 (Expert) | Segment Trees, Trees & LCA, Tree DP, Bitmask DP, String Hashing/KMP, Combinatorics | Codeforces Div 2 (C–E), CSES Advanced Sections |
| **Phase 4: Expert Mastery** | 1600 – 1900+ (Candidate Master) | Lazy Segment Trees, Sqrt Decomposition (Mo's), Flow, Game Theory, Advanced Math | Codeforces Div 1/2 (D–F), AtCoder ARC |

---

## 📁 Repository Structure

Each module corresponds to a specific branch of the Codeforces Catalog with focused explanations, templates, and problem walk-throughs:

```
ComProg/
├── 00_General_Advice_and_Practice/      # Contest strategy, practice philosophy, Python CP survival guide
├── 01_Foundations_and_Complexity/        # Big-O time/space complexity, Fast I/O, prefix sums, difference arrays
├── 02_Binary_and_Ternary_Search/         # Binary search invariants, bisect, search on answer, ternary search
├── 03_Two_Pointers_and_Sliding_Window/   # Inward pointers, caterpillar technique, variable/fixed sliding windows
├── 04_Sorting_and_Greedy/                # Custom comparator sorting, coordinate compression, exchange arguments
├── 05_Data_Structures/                   # DSU, Fenwick Tree, Segment Tree, Monotonic Stack/Queue, Ordered Set
├── 06_Dynamic_Programming/               # 0/1 Knapsack, Grid DP, LIS O(N log N), Range DP, Tree DP, Bitmask DP
├── 07_Graph_Algorithms/                  # BFS/DFS, TopoSort, Dijkstra, Bellman-Ford, Floyd-Warshall, MST, Bridges
├── 08_Trees_and_LCA/                     # Tree diameter, Euler Tour subtree queries, Binary Lifting LCA
├── 09_Mathematics_and_Number_Theory/     # Sieve, modular inverse, combinatorics (nCr mod p), extended GCD, bitwise tricks
├── 10_String_Algorithms/                 # Polynomial double rolling hash, KMP prefix function, Z-algorithm, Trie
├── 11_Advanced_and_Niche_Techniques/     # Constructive heuristics, Mo's algorithm, 2D Sweep line, Game Theory (Nim)
└── 12_Reference_and_Catalog/             # Complete parsed archive of 388+ Codeforces Catalog blog posts & tutorials
```

---

## ⚡ The Python Survival Guide for Competitive Programming

Python is expressive and clean, but in competitive programming, default execution is slower than C++. To reach high performance in Python without hitting Time Limit Exceeded (TLE):

1. **Always Submit in PyPy 3 on Codeforces**
   - PyPy's Just-In-Time (JIT) compiler accelerates tight loops by 5× to 10×.
   - *Exception*: Deep recursion can occasionally be memory-heavy or slower on PyPy; prefer iterative solutions or increase recursion limit with caution.

2. **Master Fast I/O (`sys.stdin.read().split()`)**
   - Standard `input()` can take 0.5s–1.0s just to read $2 \times 10^5$ lines.
   - Reading all tokens at once via `sys.stdin.read().split()` takes ~0.05s.

3. **Avoid $O(N)$ Traps**
   - `x in list` is $O(N)$. Use `set` or `dict` for $O(1)$ lookups.
   - `list.pop(0)` is $O(N)$. Use `collections.deque.popleft()` for $O(1)$ queue operations.
   - String concatenation in a loop (`s += ch`) creates a new string each time ($O(N^2)$ total). Collect characters or tokens in a list and use `"".join(...)`.

4. **Defend Against Anti-Hash Tests (Hacking)**
   - In Codeforces contests, users can inspect your code and submit custom inputs designed to force hash collisions on Python dictionaries and sets ($O(N^2)$ blowup).
   - *Defense*: XOR all dictionary/set keys with a fixed pseudo-random 64-bit integer.

5. **Set Recursion Limit for DFS**
   - Python's default recursion limit is 1,000. For tree/graph DFS with up to $2 \times 10^5$ nodes, always add:
     ```python
     import sys
     sys.setrecursionlimit(300000)
     ```

---

## 🛠️ Testing Your Solutions

You can test any Python solution file locally using the included test runner:
```bash
python3 run_tests.py <path_to_solution.py>
```
For example:
```bash
python3 run_tests.py 01_Foundations_and_Complexity/prefix_sums_and_diff_arrays.py
```

---

## 📚 References & Codeforces Catalog

All modules link back to the comprehensive [Codeforces Catalog Archive](12_Reference_and_Catalog/codeforces_catalog_full.md) compiled in this repository, featuring tutorials written by world champions, Legendary Grandmasters (e.g. Um_nik, Radewoosh, MikeMirzayanov), and renowned coaches.
