#!/usr/bin/env python3
"""
Performance optimization analysis for the slow scenario.

Based on profiling results, this script creates optimized versions of the slow scenario
and compares their performance characteristics.
"""

import json
import time
from pathlib import Path

import ephemerista
from ephemerista.scenarios import Scenario


def create_optimized_scenarios():
    """Create optimized versions of the slow scenario."""
    print("🔧 Creating Optimized Scenario Variations")
    print("=" * 60)

    # Load original scenario
    original_json = json.loads(Path("tests/resources/slow_scenario.json").read_text())
    print(f"📄 Original scenario loaded: {original_json['name']}")

    scenarios = {}

    # Original scenario
    scenarios["original"] = {
        "description": "Original slow scenario",
        "discretization": 1.0,
        "data": original_json.copy(),
    }

    # Optimization 1: Reduce discretization resolution
    opt1 = original_json.copy()
    opt1["discretizationResolution"] = 2.0
    opt1["name"] = "Optimized - 2° Resolution"
    scenarios["resolution_2deg"] = {"description": "Reduced discretization to 2°", "discretization": 2.0, "data": opt1}

    # Optimization 2: Further reduce discretization
    opt2 = original_json.copy()
    opt2["discretizationResolution"] = 3.0
    opt2["name"] = "Optimized - 3° Resolution"
    scenarios["resolution_3deg"] = {"description": "Reduced discretization to 3°", "discretization": 3.0, "data": opt2}

    # Optimization 3: Reduce duration
    opt3 = original_json.copy()
    opt3["endTime"]["timestamp"]["value"] = "2025-06-16T12:00:00.000Z"  # 12 hours instead of 24
    opt3["discretizationResolution"] = 2.0
    opt3["name"] = "Optimized - 12h + 2° Resolution"
    scenarios["duration_12h_res2"] = {
        "description": "12-hour duration + 2° resolution",
        "discretization": 2.0,
        "data": opt3,
    }

    # Optimization 4: Reduce satellite count
    opt4 = original_json.copy()
    opt4["constellations"][0]["model"]["nsats"] = 12  # Half the satellites
    opt4["discretizationResolution"] = 2.0
    opt4["name"] = "Optimized - 12 Satellites + 2° Resolution"
    scenarios["sats_12_res2"] = {"description": "12 satellites + 2° resolution", "discretization": 2.0, "data": opt4}

    return scenarios


def analyze_scenario_performance(scenario_data, name):
    """Analyze the performance characteristics of a scenario."""
    print(f"\n🔍 Analyzing: {name}")
    print("-" * 40)

    start_time = time.time()

    # Parse scenario
    scenario = Scenario.model_validate_json(json.dumps(scenario_data))
    parse_time = time.time() - start_time

    # Get assets
    assets_start = time.time()
    assets = scenario.all_assets
    assets_time = time.time() - assets_start

    # Get discretized areas
    areas_start = time.time()
    areas = scenario.discretized_areas
    areas_time = time.time() - areas_start

    # Get ground locations
    locations_start = time.time()
    locations = scenario.ground_locations
    locations_time = time.time() - locations_start

    # Calculate complexity
    n_assets = len(assets)
    n_locations = len(locations)
    duration_delta = scenario.end_time - scenario.start_time
    duration_seconds = float(duration_delta)
    duration_hours = duration_seconds / 3600

    visibility_pairs = n_assets * n_locations
    time_steps = duration_hours * 60  # 1-minute steps
    total_operations = visibility_pairs * time_steps

    total_setup_time = parse_time + assets_time + areas_time + locations_time

    return {
        "name": name,
        "parse_time": parse_time,
        "assets_time": assets_time,
        "areas_time": areas_time,
        "locations_time": locations_time,
        "total_setup_time": total_setup_time,
        "n_assets": n_assets,
        "n_areas": len(areas),
        "n_locations": n_locations,
        "duration_hours": duration_hours,
        "visibility_pairs": visibility_pairs,
        "total_operations": total_operations,
        "discretization_resolution": scenario.discretization_resolution,
    }


def compare_scenarios():
    """Compare all scenario variations."""
    print("📊 Scenario Performance Comparison")
    print("=" * 80)

    # Initialize once
    ephemerista.init(eop_path="tests/resources/finals2000A.all.csv", spk_path="tests/resources/de440s.bsp")

    scenarios = create_optimized_scenarios()
    results = []

    for key, scenario_info in scenarios.items():
        try:
            result = analyze_scenario_performance(scenario_info["data"], scenario_info["description"])
            result["key"] = key
            result["discretization"] = scenario_info["discretization"]
            results.append(result)

            print(f"   ✅ {result['name']}: {result['total_setup_time']:.2f}s setup")

        except Exception as e:
            print(f"   ❌ Failed {scenario_info['description']}: {e}")

    # Detailed comparison table
    print("\n📋 Detailed Performance Comparison:")
    print("=" * 80)

    # Header
    print(
        f"{'Scenario':<25} {'Res':<4} {'Assets':<7} {'Areas':<6} "
        f"{'Locations':<9} {'Duration':<8} {'Operations':<12} {'Setup':<7}"
    )
    print("-" * 80)

    for result in results:
        ops_str = (
            f"{result['total_operations'] / 1e6:.1f}M"
            if result["total_operations"] > 1e6
            else f"{result['total_operations'] / 1e3:.0f}K"
        )

        print(
            f"{result['name'][:24]:<25} "
            f"{result['discretization_resolution']:<4.0f} "
            f"{result['n_assets']:<7} "
            f"{result['n_areas']:<6} "
            f"{result['n_locations']:<9} "
            f"{result['duration_hours']:<8.1f} "
            f"{ops_str:<12} "
            f"{result['total_setup_time']:<7.2f}"
        )

    # Performance improvement analysis
    if len(results) > 1:
        baseline = results[0]  # Original scenario

        print("\n📈 Performance Improvements vs Original:")
        print("=" * 80)

        for result in results[1:]:
            ops_improvement = baseline["total_operations"] / result["total_operations"]
            setup_improvement = baseline["total_setup_time"] / result["total_setup_time"]
            area_reduction = baseline["n_areas"] / result["n_areas"]

            print(f"\n🎯 {result['name']}:")
            print(
                f"   Operations:  {ops_improvement:.1f}x faster "
                f"({result['total_operations'] / 1e6:.1f}M vs {baseline['total_operations'] / 1e6:.1f}M)"
            )
            print(
                f"   Setup time:  {setup_improvement:.1f}x faster "
                f"({result['total_setup_time']:.2f}s vs {baseline['total_setup_time']:.2f}s)"
            )
            print(f"   Areas:       {area_reduction:.1f}x fewer ({result['n_areas']} vs {baseline['n_areas']})")

            if ops_improvement > 4:
                print("   🟢 Excellent improvement!")
            elif ops_improvement > 2:
                print("   🟡 Good improvement")
            else:
                print("   🔴 Modest improvement")

    # Recommendations
    print("\n💡 Optimization Recommendations:")
    print("=" * 80)

    best_balanced = None
    best_ops = float("inf")

    for result in results[1:]:  # Skip original
        if result["total_operations"] < best_ops and result["total_operations"] < 10e6:  # Under 10M operations
            best_ops = result["total_operations"]
            best_balanced = result

    if best_balanced:
        print(f"🏆 Recommended optimization: {best_balanced['name']}")
        print(f"   - Operations: {best_balanced['total_operations'] / 1e6:.1f}M (manageable)")
        print(f"   - Setup time: {best_balanced['total_setup_time']:.2f}s")
        print(f"   - Estimated runtime: {best_balanced['total_operations'] / 1000 / 60:.1f} minutes")

    # Save optimized scenario
    if best_balanced:
        optimized_data = None
        for _key, scenario_info in scenarios.items():
            if scenario_info["description"] == best_balanced["name"]:
                optimized_data = scenario_info["data"]
                break

        if optimized_data:
            output_file = "tests/resources/optimized_scenario.json"
            Path(output_file).write_text(json.dumps(optimized_data, indent=2))
            print(f"\n💾 Saved optimized scenario to: {output_file}")

    return results


def main():
    """Main optimization analysis."""
    try:
        results = compare_scenarios()

        print("\n✅ Optimization analysis complete!")
        print(f"📊 Analyzed {len(results)} scenario variations")
        print("🎯 Check recommendations above for best performance")

        return 0

    except Exception as e:
        print(f"\n❌ Optimization analysis failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
