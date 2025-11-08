#!/usr/bin/env python3
"""
Profile the slow scenario benchmark to identify performance bottlenecks.

This script profiles the coverage analysis for the slow_scenario.json to understand
where the computation time is spent and identify optimization opportunities.
"""

import cProfile
import pstats
import sys
import time
from io import StringIO
from pathlib import Path

import ephemerista
from ephemerista.analysis.coverage import Coverage
from ephemerista.scenarios import Scenario


def load_slow_scenario():
    """Load the slow scenario from JSON."""
    scn_json = Path("tests/resources/slow_scenario.json").read_text()
    return Scenario.model_validate_json(scn_json)


def run_coverage_analysis(scenario: Scenario):
    """Run coverage analysis on the scenario."""
    coverage = Coverage(scenario=scenario)
    results = coverage.analyze()
    return results


def profile_slow_scenario():
    """Profile the slow scenario benchmark with detailed analysis."""
    print("🚀 Starting profiling of slow scenario benchmark...")
    print("=" * 80)

    # Initialize ephemerista
    print("📚 Initializing ephemerista...")
    start_time = time.time()
    ephemerista.init(eop_path="tests/resources/finals2000A.all.csv", spk_path="tests/resources/de440s.bsp")
    init_time = time.time() - start_time
    print(f"   Initialization took: {init_time:.2f} seconds")

    # Load scenario
    print("\n📄 Loading slow scenario...")
    start_time = time.time()
    scenario = load_slow_scenario()
    load_time = time.time() - start_time
    print(f"   Scenario loading took: {load_time:.2f} seconds")

    # Print scenario info
    print("\n📊 Scenario Information:")
    print(f"   Name: {scenario.name}")
    print(f"   Duration: {scenario.end_time - scenario.start_time}")
    print(f"   Assets: {len(scenario.all_assets)}")
    print(f"   Areas: {len(scenario.discretized_areas)}")
    print(f"   Ground locations: {len(scenario.ground_locations)}")
    print(f"   Discretization resolution: {scenario.discretization_resolution}°")

    # Profile the coverage analysis
    print("\n🔍 Profiling coverage analysis...")
    profiler = cProfile.Profile()

    start_time = time.time()
    profiler.enable()

    try:
        results = run_coverage_analysis(scenario)
        analysis_time = time.time() - start_time

        profiler.disable()

        print(f"   ✅ Coverage analysis completed in {analysis_time:.2f} seconds")
        print(f"   Coverage results: {len(results.coverage_percent)} data points")

        # Save profiling results
        stats = pstats.Stats(profiler)

        # Save detailed stats to file
        profile_file = "slow_scenario_profile.prof"
        stats.dump_stats(profile_file)
        print(f"   📁 Detailed profile saved to: {profile_file}")

        # Print top functions by cumulative time
        print("\n📈 Top 20 Functions by Cumulative Time:")
        print("=" * 80)
        s = StringIO()
        stats = pstats.Stats(profiler, stream=s)
        stats.sort_stats("cumulative").print_stats(20)
        print(s.getvalue())

        # Print top functions by total time
        print("\n⏱️  Top 20 Functions by Total Time:")
        print("=" * 80)
        s = StringIO()
        stats = pstats.Stats(profiler, stream=s)
        stats.sort_stats("tottime").print_stats(20)
        print(s.getvalue())

        # Print coverage-specific functions
        print("\n🎯 Coverage Analysis Functions:")
        print("=" * 80)
        s = StringIO()
        stats = pstats.Stats(profiler, stream=s)
        stats.sort_stats("cumulative").print_stats("coverage|visibility|ephemerista")
        coverage_stats = s.getvalue()
        if coverage_stats.strip():
            print(coverage_stats)
        else:
            print("   No coverage-specific functions found in top results")

        # Memory analysis note
        print("\n💾 Memory usage information not available (tracemalloc not used)")

        return analysis_time, stats

    except Exception as e:
        profiler.disable()
        print(f"   ❌ Error during profiling: {e}")
        raise


def analyze_bottlenecks(stats):
    """Analyze the profiling statistics to identify specific bottlenecks."""
    print("\n🔬 Bottleneck Analysis:")
    print("=" * 80)

    # Get statistics as a sortable format
    s = StringIO()
    ps = pstats.Stats(stats, stream=s)

    # Look for specific patterns that might indicate bottlenecks
    bottleneck_patterns = [
        "propagate",
        "ephemeris",
        "orbital",
        "visibility",
        "coverage",
        "analyze",
        "numpy",
        "scipy",
        "matrix",
        "array",
        "java",
        "orekit",
        "jni",
    ]

    print("🎯 Searching for common bottleneck patterns...")
    for pattern in bottleneck_patterns:
        s = StringIO()
        ps = pstats.Stats(stats, stream=s)
        ps.sort_stats("cumulative").print_stats(pattern)
        pattern_stats = s.getvalue()

        if pattern_stats.strip() and "ncalls" in pattern_stats:
            print(f"\n📌 Functions matching '{pattern}':")
            print("-" * 40)
            print(pattern_stats)


def main():
    """Main profiling function."""
    try:
        analysis_time, stats = profile_slow_scenario()
        analyze_bottlenecks(stats)

        print("\n🎉 Profiling Complete!")
        print("=" * 80)
        print(f"📊 Total analysis time: {analysis_time:.2f} seconds")
        print("📁 Detailed profile saved to: slow_scenario_profile.prof")
        print("\n💡 To view interactive profile:")
        print("   python -m pstats slow_scenario_profile.prof")
        print("\n💡 To generate visualization (if snakeviz is installed):")
        print("   pip install snakeviz")
        print("   snakeviz slow_scenario_profile.prof")

        return 0

    except Exception as e:
        print(f"\n❌ Profiling failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
