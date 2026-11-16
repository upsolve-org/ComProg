import sys
import time
import io
from contextlib import redirect_stdout

"""
Lightweight Test Runner for Competitive Programming Solutions in Python.

Usage:
    python3 run_tests.py <solution_file.py>

How to use in your solution files:
    Each solution file can define a list of `TEST_CASES = [(input_str, expected_output_str), ...]`.
    This runner executes the solution against each test case, captures stdout,
    measures execution time, and checks if the output matches.
"""

def run_tests_for_file(filepath: str):
    import importlib.util

    print(f"\n=======================================================")
    print(f" Testing: {filepath}")
    print(f"=======================================================")

    spec = importlib.util.spec_from_file_location("solution_module", filepath)
    if not spec or not spec.loader:
        print(f"Error: Could not load {filepath}")
        return

    mod = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        print(f"Error executing module: {e}")
        return

    test_cases = getattr(mod, "TEST_CASES", None)
    solve_func = getattr(mod, "solve", None)

    if not test_cases:
        print("Note: No `TEST_CASES` list found in the file. Running `solve()` once if present...")
        if callable(solve_func):
            try:
                solve_func()
            except Exception as e:
                print(f"Execution error: {e}")
        else:
            print("No `solve()` function found. Direct module execution finished.")
        return

    passed = 0
    total = len(test_cases)
    original_stdin = sys.stdin

    for idx, (inp, expected) in enumerate(test_cases, 1):
        inp_clean = inp.strip()
        exp_clean = expected.strip()

        stdout_stream = io.StringIO()
        start_time = time.perf_counter()
        err = None

        try:
            sys.stdin = io.StringIO(inp_clean + "\n")
            with redirect_stdout(stdout_stream):
                if callable(solve_func):
                    solve_func()
                else:
                    spec.loader.exec_module(mod)
        except Exception as e:
            err = e
        finally:
            sys.stdin = original_stdin

        elapsed = (time.perf_counter() - start_time) * 1000
        actual_output = stdout_stream.getvalue().strip()

        if err:
            print(f"  [Case {idx}/{total}] ❌ RUNTIME ERROR in {elapsed:.2f} ms")
            print(f"     Exception: {err}")
        elif actual_output == exp_clean:
            print(f"  [Case {idx}/{total}] ✅ PASSED in {elapsed:.2f} ms")
            passed += 1
        else:
            print(f"  [Case {idx}/{total}] ❌ FAILED in {elapsed:.2f} ms")
            print(f"     Input:\n{indent(inp_clean)}")
            print(f"     Expected:\n{indent(exp_clean)}")
            print(f"     Actual:\n{indent(actual_output)}")

    print(f"-------------------------------------------------------")
    print(f" Result: {passed}/{total} Passed")
    print(f"=======================================================\n")

def indent(s: str, spaces: int = 8) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + line for line in s.splitlines())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 run_tests.py <path_to_solution.py>")
        sys.exit(1)
    run_tests_for_file(sys.argv[1])
