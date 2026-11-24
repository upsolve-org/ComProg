# Session Card: Debugging under Time Pressure

1. **Read the verdict literally.** WA logic, TLE cost, RE memory access or depth, CE the first line only.
2. **Spray the samples.** Run every sample from a file, not by hand-typed input.
3. **Bisect the test.** Binary search the failing index in your own generator until a small case reproduces.
4. **Add asserts behind a flag.**

```cpp
#ifdef LOCAL
#define CHECK(x) do { if (!(x)) { cerr << "fail: " #x " at line " << __LINE__ << '\n'; abort(); } } while (0)
#else
#define CHECK(x) ((void)0)
#endif
```

5. **Sanitizer build** once the case is small: `-fsanitize=address,undefined -g -O1`.
6. **Re-read the statement** when the fix keeps failing; most long WA streaks are a misread rule, not a code bug.

- Print to `cerr`, never `cout`, for debug output; the judge ignores `cerr`.
- Remove or `#ifdef` the prints before submitting.
- Compare answer formats character by character after the fix.