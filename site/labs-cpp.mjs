// Phase 5a: C++20 assignments. Cases live here and reach the judge, which also
// stacks the shared private cases from judge-cases.mjs on top.
const lab = (title, task, cases, hints, starter) => ({ title, task, cases, hints, starter, language: 'cpp' })

const skeleton = `#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    // Read n, then the n values.

    // Print the answer.
}
`

export const cppLabs = [
  lab('Sum two 64-bit integers',
    'Read two signed integers on one line and print their sum. Each integer is between −10⁹ and 10⁹.',
    [['7 -2', '5'], ['0 0', '0'], ['-1000000000 -1000000000', '-2000000000']],
    ['What type does `cin >> n` store into, and how wide is that type?', 'What is the largest possible sum, and does `int` hold it?', 'Does `cin >> a >> b` split on whitespace or on the line?'],
    `#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    long long a, b;
    cin >> a >> b;
    // Print the sum.
}
`),
  lab('Maximum subarray sum (Kadane)',
    'Read n (1 ≤ n ≤ 10⁶), then n integers in [−10⁹, 10⁹] on the next line. Print the largest sum of any non-empty contiguous subarray. Aim for O(n) time.',
    [['9\n-2 1 -3 4 -1 2 1 -5 4', '6'], ['5\n-1 -2 -3 -4 -5', '-1'], ['3\n-5 -2 -3', '-2'], ['3\n2 -1 2', '3'],
      ['4\n1000000000 1000000000 1000000000 1000000000', '4000000000'], ['1\n-8', '-8'], ['3\n0 0 0', '0']],
    ['List the subarrays ending at the third value of `2 -1 2`. What do they share?', 'If every value is negative, what does the non-empty requirement forbid?', 'Which type keeps 4000000000 intact, and what happens to it in an `int` accumulator?'],
    skeleton),
  lab('First value at least x',
    'Read n and q, followed by n sorted integers on the second line and q query values on the third. For each query x, print the zero-based index of the first value at least x, or −1 if none exists. Print one answer per line. 1 ≤ n, q ≤ 200,000. Aim for O(log n) per query after reading.',
    [['5 3\n1 4 4 6 8\n4 5 0', '1\n3\n0'], ['1 2\n3\n3 4', '0\n-1'], ['3 1\n1 2 4\n5', '-1']],
    ['How does the truth of "value ≥ x" change as you move right?', 'If several values equal x, which boundary do you need?', 'Which STL call returns the first element not less than x, and what iterator marks "none"?'],
    skeleton),
  lab('Best fixed window',
    'Read n and k, then n signed integers on the next line. Print the maximum sum of a contiguous block of exactly k integers. 1 ≤ k ≤ n ≤ 200,000. Aim for O(n) time.',
    [['5 3\n2 -1 4 3 -2', '6'], ['3 2\n-5 -2 -1', '-3'], ['2 2\n7 -4', '3']],
    ['Which elements do two adjacent windows of length three share?', 'How many values change membership when the window moves one step?', 'What should happen when k equals n, and how does a naive sum handle that?'],
    skeleton),
  lab('Attend the most events',
    'Read n (1 ≤ n ≤ 200,000), then n lines with start and end times (start < end). Print the largest number of events one person can attend. An event may start when the previous one ends. Aim for O(n log n) time.',
    [['4\n1 5\n2 3\n3 4\n4 6', '3'], ['3\n1 5\n2 5\n3 5', '1'], ['3\n4 6\n1 2\n2 4', '3']],
    ['Draw a long event that starts before two short events. What happens if you pick it first?', 'Which key do you sort by so the next choice is always safe?', 'Which of `start < end` and `start <= end` matches "may start when the previous ends"?'],
    skeleton),
  lab('Track connected groups with DSU',
    'Read n and q, then q lines with two people to connect, numbered 1 through n. Print the number of groups after each connection, one per line. 1 ≤ n, q ≤ 200,000. Aim for near-linear total time.',
    [['4 4\n1 2\n3 4\n2 3\n1 4', '3\n2\n1\n1'], ['1 2\n1 1\n1 1', '1\n1'], ['3 2\n2 3\n3 2', '2\n2']],
    ['How many groups exist before the first connection?', 'When does a connection leave the count unchanged, and how do you detect it?', 'What two DSU optimisations keep the tree shallow, and what array holds the group size?'],
    skeleton),
  lab('Count open grid paths',
    'Read h and w (1 ≤ h,w ≤ 100), then h rows containing dots and walls (#). Count paths from top-left to bottom-right moving right or down through dots. Print the count modulo 1,000,000,007. Aim for O(h × w) time.',
    [['3 3\n...\n.#.\n...', '2'], ['1 1\n.', '1'], ['1 2\n#.', '0'], ['2 2\n..\n.#', '0']],
    ['Which cells could immediately precede an open cell?', 'What should a wall contribute to later cells?', 'Where do you apply the modulus, and why before the value leaves `int`?'],
    skeleton),
  lab('Shortest route',
    'Read n and m, then m undirected edges between vertices numbered 1 through n. Print the minimum number of edges from 1 to n, or −1 if unreachable. 1 ≤ n ≤ 200,000 and 0 ≤ m ≤ 200,000. Aim for O(n + m) time.',
    [['5 5\n1 2\n2 3\n3 5\n1 4\n4 5', '2'], ['4 1\n1 2', '-1'], ['1 0', '0']],
    ['Which vertices are reachable in one step, and how do you separate the next layer?', 'Can a vertex be enqueued twice, and how does a distance array prevent it?', 'What distance do you assign the start, and how do you print the unreachable case?'],
    skeleton),
  lab('Count descendants',
    'Read n (1 ≤ n ≤ 200,000), then the parent of each vertex 2 through n in order on the next line. The root is 1. Print the number of proper descendants of each vertex in vertex order, separated by spaces. Aim for O(n) time.',
    [['5\n1 1 3 3', '4 0 2 0 0'], ['1', '0'], ['4\n4 1 1', '3 0 0 1']],
    ['How many proper descendants does a leaf have?', 'Which order lets every vertex add its count into its parent exactly once?', 'Can a child have a smaller label than its parent, so is the input order a post-order?'],
    skeleton),
  lab('Count coprime values',
    'Read n and k (1 ≤ n ≤ 200,000, 1 ≤ k ≤ 10⁹), then n integers in [1, 10⁹] on one line. Print how many have greatest common divisor 1 with k.',
    [['5 12\n1 5 6 7 18', '3'], ['3 1\n1 4 10', '3'], ['3 30\n2 3 5', '0']],
    ['What does coprime tell you about shared prime factors?', 'Compare gcd(18, 12) with gcd(12, 6). Why do their common divisors agree?', 'What happens when k is 1, and does `std::gcd` need `long long` here?'],
    skeleton),
  lab('Find pattern occurrences',
    'Read the text and pattern on two non-empty lines of lowercase letters, each at most 200,000 characters. Print how many times the pattern occurs in the text. Count overlapping occurrences. Aim for O(text length + pattern length) time.',
    [['aaaa\naa', '3'], ['banana\nana', '2'], ['ab\nabc', '0'], ['xyz\nxyz', '1']],
    ['Mark every match start in aaaa. Which ones overlap?', 'After a mismatch, which prefix of your pattern can still be reused?', 'Which array stores those reusable prefix lengths, and what index steps back into it?'],
    skeleton),
  lab('Decide a Nim game',
    'Read n (1 ≤ n ≤ 200,000), then n pile sizes in [0, 10⁹] on one line. Players alternate removing a positive number of stones from one pile. A player who cannot move loses. Print First if the first player can force a win, or Second otherwise.',
    [['3\n1 2 3', 'Second'], ['2\n2 3', 'First'], ['1\n0', 'Second'], ['2\n7 7', 'Second']],
    ['What happens if the two piles have the same size?', 'Write three small piles in binary and compare the columns.', 'Which bitwise fold over the pile sizes decides the winner?'],
    skeleton)
]