---
tags:
  - cp/general-advice
  - cp/strategy
---

[[Home|🏠 Dashboard]] ❯ **Module 00: General Advice and Practice Philosophy**

---

# General Advice and Practice Philosophy

Competitive programming (CP) is fundamentally about **problem-solving efficiency and pattern recognition**, not simply knowing algorithm trivia. This section distills wisdom from the most celebrated tutorials in the [[12_Reference_and_Catalog/codeforces_catalog_full.md|Codeforces Catalog]].

---

## 💡 How to Come Up with Solutions

### 1. Read Problem Statements with Precision
*Reference: [How to read problem statements by Um_nik](https://codeforces.com/blog/entry/62730)*
- Read the statement slowly and identify the **exact constraints**: $N \le 10^5$, $A_i \le 10^9$, or $N \le 20$.
- Write down what is invariant (what never changes) and what is flexible.
- Check edge cases: $N = 1$, empty arrays, all elements equal, negative values, maximum possible answer overflow.

### 2. Identify Problem Archetypes
*Reference: [How to come up with solutions: techniques by MikeMirzayanov](https://codeforces.com/blog/entry/20548)*
- **Small constraints ($N \le 20$):** Bitmask DP, brute force search, meet-in-the-middle.
- **Medium constraints ($N \le 2000$):** $O(N^2)$ DP, all-pairs graphs, Floyd-Warshall.
- **Standard constraints ($N \le 2 \times 10^5$):** $O(N \log N)$ or $O(N)$ with sorting, two pointers, binary search, segment trees, or hash maps.
- **Large constraints ($N \le 10^9$):** $O(\log N)$ or $O(\sqrt{N})$ with binary search, math, matrix exponentiation, or number theory.

### 3. Characteristics of the Optimal Solution
*Reference: [Characteristics of the optimal solution by Proofy](https://codeforces.com/blog/entry/99291)*
- Ask yourself: *"If I already knew the optimal answer, what properties must it have?"*
- Can the answer be sorted? Can we process elements from left to right?
- Does an exchange argument hold (i.e. if we swap two adjacent elements, does the cost improve or degrade)?

### 4. Greedy vs. Dynamic Programming
*Reference: [On "is this greedy or DP", forcing and rubber bands by -is-this-fft-](https://codeforces.com/blog/entry/106346)*
- **Greedy:** Local decisions are globally irrevocable. Requires proving that choosing the best current step never closes off an optimal future outcome.
- **DP:** Future decisions depend on the current state, but not on *how* that state was reached (optimal substructure + overlapping subproblems).

---

## 📈 How to Practice Effectively

### The Deliberate Practice Protocol
*References:*
- [My opinion on how to practice CP by Radewoosh](https://codeforces.com/blog/entry/91114)
- [How to practice CP (Um_nik version)](https://codeforces.com/blog/entry/98806)
- [A way to practice CP: From Rating 1000 to 2400+ by E869120](https://codeforces.com/blog/entry/66909)
- [How to Effectively Practice CP by SuperJ6](https://codeforces.com/blog/entry/116371)

1. **Practice Problems slightly above your current level (+100 to +200 rating points).**
   - Solving problems you already find easy reinforces speed, but does not increase problem-solving breadth.
   - Solving problems +400 above your rating leads to cognitive overload and demotivation.
2. **The 30-Minute Rule:**
   - Attempt a problem independently for 30–45 minutes.
   - If completely stuck after writing ideas and testing small examples, open the **editorial/tutorial**.
   - Read only the first hint or first paragraph. Try again.
   - If you still need the full solution, read it, close it, and **implement the code from scratch yourself in Python without looking**.
3. **Upsolving is Mandatory:**
   - After every contest, solve at least the first problem you failed to solve during the live contest.
   - This single habit separates competitors who plateau from those who steadily rise in rating.

---

## 🤝 How to Ask for Help & Debugging

*References:*
- [How to ask for help in PM by -is-this-fft-](https://codeforces.com/blog/entry/83672)
- [Asking for help FAQ by Errichto](https://codeforces.com/blog/entry/64993)

When debugging code that gets **Wrong Answer (WA)** or **Time Limit Exceeded (TLE)**:
1. Don't say *"Why is my code WA?"*
2. Generate small hand-crafted edge cases: minimum inputs ($N=1$), duplicates, negative numbers, maximal constraints.
3. Write a slow brute-force solution ($O(N^2)$) and compare its output against your fast solution on 100 randomly generated inputs using a small Python script.

---

> [!note] In-Depth Companion Guides
> - 🐍 [[00_General_Advice_and_Practice/python_cp_guide.md|Python in Competitive Programming Guide]]
> - ⚔️ [[00_General_Advice_and_Practice/codeforces_platform_guide.md|Codeforces Platform, Divisions & Hacking Guide]]

---

🏠 [[Home|Dashboard]] | ⏭️ Next: [[01_Foundations_and_Complexity/README|01 Foundations & Complexity]]
