#!/usr/bin/env python3
"""
Quick analysis of the slow scenario to understand bottlenecks.

This script performs a targeted analysis to identify where the performance
issues come from in the slow scenario benchmark.
"""

import sys
import time
from pathlib import Path

import ephemerista
from ephemerista.scenarios import Scenario


def analyze_slow_scenario():
    """Analyze the slow scenario step by step."""
    print("🔍 Quick Analysis of Slow Scenario Performance")
    print("=" * 70)

    total_start = time.time()

    # Step 1: Initialize ephemerista
    print("1️⃣  Initializing ephemerista...")
    init_start = time.time()
    ephemerista.init(eop_path="tests/resources/finals2000A.all.csv", spk_path="tests/resources/de440s.bsp")
    init_time = time.time() - init_start
    print(f"   ✅ Initialization: {init_time:.2f} seconds")

    # Step 2: Load and parse scenario
    print("\n2️⃣  Loading scenario JSON...")
    load_start = time.time()
    scn_json = Path("tests/resources/slow_scenario.json").read_text()
    scenario = Scenario.model_validate_json(scn_json)
    load_time = time.time() - load_start
    print(f"   ✅ JSON loading: {load_time:.2f} seconds")

    # Step 3: Analyze scenario structure without computation
    print("\n3️⃣  Analyzing scenario structure...")
    print(f"   Scenario name: {scenario.name}")
    print(f"   Duration: {scenario.end_time - scenario.start_time}")
    print(f"   Discretization resolution: {scenario.discretization_resolution}°")
    print(f"   Constellations: {len(scenario.constellations)}")
    print(f"   Areas of interest: {len(scenario.areas_of_interest)}")

    # Step 4: Asset generation (this involves Orekit propagators)
    print("\n4️⃣  Generating assets (Orekit propagators)...")
    assets_start = time.time()
    assets = scenario.all_assets
    assets_time = time.time() - assets_start
    print(f"   ✅ Asset generation: {assets_time:.2f} seconds")
    print(f"   📡 Generated {len(assets)} satellites")

    # Step 5: Area discretization
    print("\n5️⃣  Discretizing areas of interest...")
    areas_start = time.time()
    areas = scenario.discretized_areas
    areas_time = time.time() - areas_start
    print(f"   ✅ Area discretization: {areas_time:.2f} seconds")
    print(f"   🌍 Generated {len(areas)} discretized areas")

    # Step 6: Ground locations
    print("\n6️⃣  Generating ground locations...")
    locations_start = time.time()
    locations = scenario.ground_locations
    locations_time = time.time() - locations_start
    print(f"   ✅ Ground locations: {locations_time:.2f} seconds")
    print(f"   📍 Generated {len(locations)} ground locations")

    # Calculate computational complexity
    print("\n📊 Computational Complexity Analysis:")
    print("=" * 70)

    n_assets = len(assets)
    n_locations = len(locations)
    duration_delta = scenario.end_time - scenario.start_time
    print(f"   Duration type: {type(duration_delta)}")
    print(f"   Duration value: {duration_delta}")

    # Handle different duration types
    if hasattr(duration_delta, "seconds"):
        if callable(duration_delta.seconds):
            duration_seconds = duration_delta.seconds()
        else:
            duration_seconds = duration_delta.seconds
    else:
        # Fallback - try to convert to float
        duration_seconds = float(duration_delta)

    duration_hours = duration_seconds / 3600

    # Estimate visibility computation complexity
    visibility_pairs = n_assets * n_locations
    # Assume 1-minute time steps for coverage analysis
    time_steps = duration_hours * 60
    total_operations = visibility_pairs * time_steps

    print(f"   Assets x Locations: {n_assets} x {n_locations} = {visibility_pairs:,} pairs")
    print(f"   Duration: {duration_hours:.1f} hours")
    print(f"   Estimated time steps (1-min): {time_steps:.0f}")
    print(f"   Total operations estimate: {total_operations:,.0f}")

    # Complexity analysis
    if total_operations > 1e8:
        complexity_level = "🔴 VERY HIGH"
    elif total_operations > 1e7:
        complexity_level = "🟠 HIGH"
    elif total_operations > 1e6:
        complexity_level = "🟡 MEDIUM"
    else:
        complexity_level = "🟢 LOW"

    print(f"   Complexity level: {complexity_level}")

    # Performance breakdown
    total_setup = init_time + load_time + assets_time + areas_time + locations_time
    total_elapsed = time.time() - total_start

    print("\n⏱️  Performance Breakdown:")
    print("=" * 70)
    print(f"   Initialization:     {init_time:8.2f}s ({init_time / total_setup * 100:5.1f}%)")
    print(f"   JSON Loading:       {load_time:8.2f}s ({load_time / total_setup * 100:5.1f}%)")
    print(f"   Asset Generation:   {assets_time:8.2f}s ({assets_time / total_setup * 100:5.1f}%)")
    print(f"   Area Discretization:{areas_time:8.2f}s ({areas_time / total_setup * 100:5.1f}%)")
    print(f"   Ground Locations:   {locations_time:8.2f}s ({locations_time / total_setup * 100:5.1f}%)")
    print(f"   {'=' * 35}")
    print(f"   Total Setup:        {total_setup:8.2f}s")
    print(f"   Total Elapsed:      {total_elapsed:8.2f}s")

    # Identify bottlenecks
    components = [
        ("Initialization", init_time),
        ("JSON Loading", load_time),
        ("Asset Generation", assets_time),
        ("Area Discretization", areas_time),
        ("Ground Locations", locations_time),
    ]

    slowest = max(components, key=lambda x: x[1])
    print(f"\n🐌 Biggest setup bottleneck: {slowest[0]} ({slowest[1]:.2f}s)")

    # Performance recommendations
    print("\n💡 Performance Analysis & Recommendations:")
    print("=" * 70)

    if areas_time > 5:
        print(f"   🌍 Area discretization is slow ({areas_time:.1f}s)")
        print(
            f"      → Consider increasing discretization resolution (currently {scenario.discretization_resolution}°)"
        )
        print(f"      → Current: {len(areas)} areas, try resolution = 2° or 3°")

    if assets_time > 5:
        print(f"   📡 Asset generation is slow ({assets_time:.1f}s)")
        print(f"      → {n_assets} satellites require Orekit propagator setup")
        print("      → Consider using fewer satellites or simpler propagators")

    if total_operations > 1e8:
        print("   🚨 CRITICAL: Very high computational complexity!")
        print(f"      → {total_operations:,.0f} operations estimated")
        print(f"      → Reduce: satellites ({n_assets}), areas ({len(areas)}), or duration ({duration_hours:.1f}h)")
    elif total_operations > 1e7:
        print(f"   ⚠️  High computational complexity: {total_operations:,.0f} operations")
        print("      → Consider optimizations or reduced scope")

    if n_locations > 2000:
        print(f"   📍 High ground location count ({n_locations})")
        print(f"      → Discretization resolution of {scenario.discretization_resolution}° creates many points")
        print("      → Try 2° or 3° resolution to reduce computational load")

    # Estimate total runtime
    if total_operations > 1e7:
        # Very rough estimate: assume 1000 operations per second
        estimated_runtime = total_operations / 1000
        print(f"\n⏰ Estimated total coverage analysis runtime: {estimated_runtime / 60:.1f} minutes")
        if estimated_runtime > 300:  # 5 minutes
            print("   🔴 This is likely too slow for practical use!")

    return scenario, total_setup


def main():
    """Main analysis function."""
    try:
        _, setup_time = analyze_slow_scenario()

        print("\n✅ Quick analysis complete!")
        print(f"📊 Setup time: {setup_time:.1f} seconds")
        print("🎯 Main bottleneck identified - check recommendations above")

        return 0

    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
