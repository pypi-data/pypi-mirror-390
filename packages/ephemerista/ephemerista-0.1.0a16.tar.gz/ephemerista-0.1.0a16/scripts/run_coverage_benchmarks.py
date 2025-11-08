#!/usr/bin/env python3
"""
Run coverage analysis benchmarks using pytest-benchmark.

This script provides convenient ways to run coverage benchmarks with
pytest-benchmark for performance tracking and comparison.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_benchmarks(
    *,
    save_name: str | None = None,
    compare_name: str | None = None,
    group_by: str | None = None,
    include_slow: bool = False,
    verbose: bool = True,
    output_format: str = "table",
) -> int:
    """
    Run coverage benchmarks using pytest-benchmark.

    Parameters
    ----------
    save_name : str, optional
        Name to save benchmark results for later comparison
    compare_name : str, optional
        Name of saved benchmark results to compare against
    group_by : str, optional
        How to group benchmark results (e.g., 'group', 'name', 'param')
    include_slow : bool
        Whether to include slow benchmarks (marked with @pytest.mark.slow)
    verbose : bool
        Whether to run with verbose output
    output_format : str
        Output format for benchmark results ('table', 'json', 'csv')

    Returns
    -------
    int
        Exit code from pytest
    """
    # Base command
    cmd = ["uv", "run", "pytest", "tests/test_coverage_benchmarks.py", "--benchmark-only"]

    # Add verbose flag
    if verbose:
        cmd.append("-v")

    # Include slow tests if requested
    if include_slow:
        cmd.append("-m")
        cmd.append("")  # Include all marks
    else:
        cmd.append("-m")
        cmd.append("not slow")  # Exclude slow tests

    # Add benchmark-specific options
    if save_name:
        cmd.extend(["--benchmark-save", save_name])

    if compare_name:
        cmd.extend(["--benchmark-compare", compare_name])

    if group_by:
        cmd.extend(["--benchmark-group-by", group_by])

    # Set output format
    if output_format != "table":
        cmd.extend([f"--benchmark-json={output_format}.json"])

    # Add histogram generation for detailed analysis (only if pygal is available)
    try:
        import pygal  # noqa: F401

        cmd.append("--benchmark-histogram")
    except ImportError:
        # Skip histogram generation if pygal is not installed
        pass

    print(f"Running command: {' '.join(cmd)}")
    print("=" * 80)

    # Run the command
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent, check=False)  # noqa: S603
    return result.returncode


def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Run coverage analysis benchmarks with pytest-benchmark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run fast benchmarks only
  python scripts/run_coverage_benchmarks.py

  # Run all benchmarks including slow ones
  python scripts/run_coverage_benchmarks.py --include-slow

  # Save benchmark results as baseline
  python scripts/run_coverage_benchmarks.py --save baseline

  # Compare against baseline
  python scripts/run_coverage_benchmarks.py --compare baseline

  # Group results by benchmark group
  python scripts/run_coverage_benchmarks.py --group-by group

  # Run and save results for comparison
  python scripts/run_coverage_benchmarks.py --save optimized --compare baseline

  # Generate JSON output
  python scripts/run_coverage_benchmarks.py --format json
        """,
    )

    parser.add_argument(
        "--save", metavar="NAME", help="Save benchmark results with the given name for later comparison"
    )

    parser.add_argument(
        "--compare", metavar="NAME", help="Compare results against previously saved benchmark with the given name"
    )

    parser.add_argument(
        "--group-by",
        choices=["group", "name", "param", "func"],
        help="Group benchmark results by the specified criteria",
    )

    parser.add_argument(
        "--include-slow", action="store_true", help="Include slow benchmarks (marked with @pytest.mark.slow)"
    )

    parser.add_argument("--quiet", action="store_true", help="Run with minimal output")

    parser.add_argument(
        "--format",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format for benchmark results (default: table)",
    )

    args = parser.parse_args()

    # Run benchmarks
    exit_code = run_benchmarks(
        save_name=args.save,
        compare_name=args.compare,
        group_by=args.group_by,
        include_slow=args.include_slow,
        verbose=not args.quiet,
        output_format=args.format,
    )

    if exit_code == 0:
        print("\n" + "=" * 80)
        print("✅ Benchmarks completed successfully!")

        if args.save:
            print(f"📊 Results saved as '{args.save}' for future comparison")
            print(f"    Use --compare {args.save} to compare against these results")

        if args.compare:
            print(f"📈 Results compared against '{args.compare}'")

        print("\n🔍 Benchmark files saved in .benchmarks/ directory")
        print("📊 View detailed results: .benchmarks/*/benchmark.json")
        print("📈 View histograms: .benchmarks/*/*.svg")

        print("\n💡 Tips:")
        print("  - Use --save <name> to create performance baselines")
        print("  - Use --compare <name> to track improvements")
        print("  - Use --group-by group to organize results by test type")
        print("  - Add --include-slow for comprehensive testing")

    else:
        print(f"\n❌ Benchmarks failed with exit code {exit_code}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
