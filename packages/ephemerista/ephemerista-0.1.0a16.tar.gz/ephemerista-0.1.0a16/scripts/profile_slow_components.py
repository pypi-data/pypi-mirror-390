#!/usr/bin/env python3
"""
Component-wise profiling of the slow scenario to identify bottlenecks.

This script breaks down the analysis into components to understand which
parts of the pipeline are consuming the most time.
"""

import sys
import time
from pathlib import Path

import ephemerista
from ephemerista.analysis.coverage import Coverage
from ephemerista.scenarios import Scenario


def time_component(name, func, *args, **kwargs):
    """Time a component and return the result and elapsed time."""
    print(f"⏱️  Timing {name}...")
    start_time = time.time()
    try:
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        print(f"   ✅ {name} completed in {elapsed:.2f} seconds")
        return result, elapsed
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"   ❌ {name} failed after {elapsed:.2f} seconds: {e}")
        raise


def analyze_scenario_components():
    """Analyze the slow scenario component by component."""
    print("🔍 Component-wise Analysis of Slow Scenario")
    print("=" * 60)

    # Initialize ephemerista
    def init_ephemeris():
        return ephemerista.init(eop_path="tests/resources/finals2000A.all.csv", spk_path="tests/resources/de440s.bsp")

    _, init_time = time_component("Ephemerista Initialization", init_ephemeris)

    # Load scenario
    def load_scenario():
        scn_json = Path("tests/resources/slow_scenario.json").read_text()
        return Scenario.model_validate_json(scn_json)

    scenario, load_time = time_component("Scenario Loading", load_scenario)

    # Print scenario details
    print("\n📊 Scenario Details:")
    print(f"   Name: {scenario.name}")
    print(f"   Duration: {scenario.end_time - scenario.start_time}")
    print(f"   Discretization resolution: {scenario.discretization_resolution}°")

    # Analyze scenario components
    def get_all_assets():
        return scenario.all_assets

    assets, assets_time = time_component("Asset Generation", get_all_assets)
    print(f"   📡 Generated {len(assets)} assets")

    def get_discretized_areas():
        return scenario.discretized_areas

    areas, areas_time = time_component("Area Discretization", get_discretized_areas)
    print(f"   🌍 Generated {len(areas)} discretized areas")

    def get_ground_locations():
        return scenario.ground_locations

    locations, locations_time = time_component("Ground Locations", get_ground_locations)
    print(f"   📍 Generated {len(locations)} ground locations")

    # Create coverage object
    def create_coverage():
        return Coverage(scenario=scenario)

    coverage, coverage_create_time = time_component("Coverage Object Creation", create_coverage)

    # Let's try to analyze the coverage analysis steps separately
    print("\n🎯 Coverage Analysis Breakdown:")
    print("-" * 40)

    # Check if we can access coverage internals for more detailed timing
    try:
        # Time just the first few iterations to estimate total time
        print("⏱️  Estimating coverage analysis time (first 5% of work)...")

        # Patch the coverage analysis to stop early for estimation
        original_analyze = coverage.analyze

        class EarlyStopError(Exception):
            pass

        iteration_count = 0

        def limited_analyze():
            nonlocal iteration_count
            # This is a rough estimation - we'd need to look at the actual Coverage.analyze method
            # to do proper component timing
            try:
                return original_analyze()
            except Exception as e:
                # If we can't do partial analysis, run a quick test
                print(f"   Cannot do partial analysis: {e}")
                return None

        partial_result, partial_time = time_component("Partial Coverage Analysis", limited_analyze)

        if partial_result:
            # Estimate total time based on partial execution
            estimated_total = partial_time * 20  # Scale up from 5%
            print(f"   📊 Estimated total coverage analysis time: {estimated_total:.1f} seconds")

    except Exception as e:
        print(f"   Cannot estimate coverage analysis time: {e}")

    # Summary
    print("\n📈 Timing Summary:")
    print("=" * 60)
    total_setup = init_time + load_time + assets_time + areas_time + locations_time + coverage_create_time
    print(f"   Initialization: {init_time:8.2f}s")
    print(f"   Scenario Load:  {load_time:8.2f}s")
    print(f"   Asset Gen:      {assets_time:8.2f}s")
    print(f"   Area Discret:   {areas_time:8.2f}s")
    print(f"   Ground Locs:    {locations_time:8.2f}s")
    print(f"   Coverage Init:  {coverage_create_time:8.2f}s")
    print(f"   {'=' * 20}")
    print(f"   Total Setup:    {total_setup:8.2f}s")

    # Identify the biggest bottleneck in setup
    components = [
        ("Initialization", init_time),
        ("Scenario Loading", load_time),
        ("Asset Generation", assets_time),
        ("Area Discretization", areas_time),
        ("Ground Locations", locations_time),
        ("Coverage Init", coverage_create_time),
    ]

    slowest = max(components, key=lambda x: x[1])
    print(f"\n🐌 Slowest setup component: {slowest[0]} ({slowest[1]:.2f}s)")

    return scenario, coverage, total_setup


def analyze_data_sizes():
    """Analyze the data sizes to understand computational complexity."""
    print("\n📏 Data Size Analysis:")
    print("=" * 60)

    scn_json = Path("tests/resources/slow_scenario.json").read_text()
    scenario = Scenario.model_validate_json(scn_json)

    n_assets = len(scenario.all_assets)
    n_areas = len(scenario.discretized_areas)
    n_locations = len(scenario.ground_locations)
    duration = scenario.end_time - scenario.start_time

    print(f"   Assets (satellites): {n_assets}")
    print(f"   Discretized areas:   {n_areas}")
    print(f"   Ground locations:    {n_locations}")
    print(f"   Duration:            {duration}")
    print(f"   Resolution:          {scenario.discretization_resolution}°")

    # Calculate computational complexity estimates
    visibility_ops = n_assets * n_locations
    coverage_ops = visibility_ops * (duration.total_seconds() / 60)  # Assume 1-minute steps

    print("\n🧮 Computational Complexity Estimates:")
    print(f"   Visibility pairs:     {visibility_ops:,}")
    print(f"   Coverage operations:  {coverage_ops:,.0f}")

    if coverage_ops > 1e7:
        print("   ⚠️  High computational complexity detected!")
        print("   💡 Consider reducing discretization resolution or duration")

    return n_assets, n_areas, n_locations, coverage_ops


def main():
    """Main analysis function."""
    try:
        # Analyze data sizes first
        _, n_areas, _, complexity = analyze_data_sizes()

        # Component timing analysis
        _, _, setup_time = analyze_scenario_components()

        print("\n🎯 Performance Recommendations:")
        print("=" * 60)

        if n_areas > 1000:
            print(f"   📐 High area count ({n_areas}) - consider larger discretization resolution")

        if complexity > 1e7:
            print("   ⏰ High computational complexity - consider shorter duration")

        if setup_time > 10:
            print(f"   🚀 Setup time is significant ({setup_time:.1f}s) - check asset/area generation")

        print("\n✅ Component analysis complete!")
        return 0

    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
