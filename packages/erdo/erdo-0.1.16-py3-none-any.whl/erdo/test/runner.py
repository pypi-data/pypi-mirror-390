"""Agent test runner that discovers and runs agent_test_* functions in parallel.

This module provides a test runner that:
1. Discovers all agent_test_*() functions in a Python file
2. Invokes all agents in parallel (fast)
3. Runs assertions sequentially (already fast)
4. Reports results in a clean format

Usage:
    python -m erdo.test.runner path/to/test_file.py

Or via CLI:
    erdo agent-test path/to/test_file.py
"""

import concurrent.futures
import importlib.util
import inspect
import sys
import time
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Tuple


@dataclass
class TestResult:
    """Result from running a single test."""

    name: str
    passed: bool
    duration: float
    error: Optional[str] = None
    assertion_error: Optional[str] = None


@dataclass
class TestSummary:
    """Summary of all test results."""

    total: int
    passed: int
    failed: int
    duration: float
    results: List[TestResult]


def discover_tests(file_path: str) -> List[Tuple[str, Callable]]:
    """Discover all agent_test_* functions in a Python file.

    Args:
        file_path: Path to the Python file

    Returns:
        List of (test_name, test_function) tuples
    """
    # Load the module
    spec = importlib.util.spec_from_file_location("test_module", file_path)
    if not spec or not spec.loader:
        raise ImportError(f"Cannot load module from {file_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules["test_module"] = module
    spec.loader.exec_module(module)

    # Find all agent_test_* functions
    tests = []
    for name, obj in inspect.getmembers(module):
        if name.startswith("agent_test_") and callable(obj):
            tests.append((name, obj))

    return tests


def run_test(test_name: str, test_func: Callable) -> TestResult:
    """Run a single test function.

    Args:
        test_name: Name of the test
        test_func: Test function to run

    Returns:
        TestResult with outcome
    """
    start_time = time.time()

    try:
        # Run the test function
        test_func()

        # If we get here, test passed
        duration = time.time() - start_time
        return TestResult(name=test_name, passed=True, duration=duration)

    except AssertionError as e:
        # Assertion failed
        duration = time.time() - start_time
        return TestResult(
            name=test_name,
            passed=False,
            duration=duration,
            assertion_error=str(e),
        )

    except Exception:
        # Other error (invocation failed, etc.)
        duration = time.time() - start_time
        tb = traceback.format_exc()
        return TestResult(name=test_name, passed=False, duration=duration, error=tb)


def run_tests_parallel(
    tests: List[Tuple[str, Callable]], max_workers: Optional[int] = None
) -> TestSummary:
    """Run all tests in parallel.

    Args:
        tests: List of (test_name, test_function) tuples
        max_workers: Maximum number of parallel workers

    Returns:
        TestSummary with all results
    """
    start_time = time.time()
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tests
        futures = {executor.submit(run_test, name, func): name for name, func in tests}

        # Collect results as they complete
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)

    duration = time.time() - start_time
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    return TestSummary(
        total=len(results),
        passed=passed,
        failed=failed,
        duration=duration,
        results=sorted(
            results, key=lambda r: r.name
        ),  # Sort by name for consistent output
    )


def print_summary(summary: TestSummary, verbose: bool = False):
    """Print test results summary.

    Args:
        summary: TestSummary to print
        verbose: Whether to show detailed error messages
    """
    print()
    print("=" * 70)
    print("AGENT TEST RESULTS")
    print("=" * 70)
    print()

    # Print each test result
    for result in summary.results:
        if result.passed:
            print(f"✅ {result.name} ({result.duration:.2f}s)")
        else:
            print(f"❌ {result.name} ({result.duration:.2f}s)")
            if verbose:
                if result.assertion_error:
                    print(f"   Assertion: {result.assertion_error}")
                if result.error:
                    print(f"   Error:\n{result.error}")

    # Print summary
    print()
    print("-" * 70)
    print(
        f"Total: {summary.total} | "
        f"Passed: {summary.passed} | "
        f"Failed: {summary.failed} | "
        f"Duration: {summary.duration:.2f}s"
    )
    print("-" * 70)
    print()

    # Print failed test details if not verbose
    if not verbose and summary.failed > 0:
        print("Failed tests:")
        for result in summary.results:
            if not result.passed:
                print(f"\n{result.name}:")
                if result.assertion_error:
                    print(f"  {result.assertion_error}")
                if result.error:
                    # Print just the last line of the error
                    error_lines = result.error.strip().split("\n")
                    print(f"  {error_lines[-1]}")
        print("\n(Use --verbose for full error traces)")
        print()


def main(
    file_path: str, verbose: bool = False, max_workers: Optional[int] = None
) -> int:
    """Main entry point for the test runner.

    Args:
        file_path: Path to the test file
        verbose: Whether to show detailed output
        max_workers: Maximum number of parallel workers

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Check file exists
        if not Path(file_path).exists():
            print(f"Error: File not found: {file_path}")
            return 1

        # Discover tests
        print(f"Discovering tests in {file_path}...")
        tests = discover_tests(file_path)

        if not tests:
            print("No tests found (looking for agent_test_* functions)")
            return 1

        print(f"Found {len(tests)} tests")
        print()

        # Run tests
        print("Running tests in parallel...")
        summary = run_tests_parallel(tests, max_workers=max_workers)

        # Print results
        print_summary(summary, verbose=verbose)

        # Return exit code
        return 0 if summary.failed == 0 else 1

    except Exception as e:
        print(f"Error running tests: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run agent tests")
    parser.add_argument("file", help="Path to test file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "-j", "--jobs", type=int, default=None, help="Number of parallel jobs"
    )

    args = parser.parse_args()

    sys.exit(main(args.file, verbose=args.verbose, max_workers=args.jobs))
