# Session Card: Test Cases

```cpp
#include <bits/stdc++.h>
using namespace std;

struct Case { string input, expected; };

vector<Case> cases = {
    {"5\n-1 -2 -3 -4 -5\n", "-1"},          // all negative
    {"1\n-8\n", "-8"},                       // single element
    {"3\n2 -1 2\n", "3"},                    // reset on every negative is wrong
    {"4\n1000000000 1000000000 1000000000 1000000000\n", "4000000000"},  // 32-bit overflow
};

int main() {
    ios::sync_with_stdio(false);
    int main() {
    int failures = 0;
    for (const auto &test : cases) {
        FILE *pipe = popen("./main", "w");   // POSIX; on Windows use _popen
        fputs(test.input.c_str(), pipe);
        pclose(pipe);
    }
    return failures;
}
```

- Include the constraint extremes: $n = 1$, the largest value, the smallest value, all-equal input.
- Include the case a named failure mode produces (see the statement's pitfalls).
- One case per pitfall, not five random ones.
- Print the input when a case fails so it is reproducible.
- Keep cases in the repository, not in a scratch file.