"""
Benchmark tests for visibility analysis performance using pytest-benchmark.

This module contains benchmark tests to compare performance between sequential
and parallel visibility analysis implementations.
"""

import pytest

import ephemerista
from ephemerista.analysis.visibility import Visibility
from ephemerista.assets import Asset, GroundStation, Spacecraft
from ephemerista.constellation.design import Constellation, WalkerStar
from ephemerista.propagators.sgp4 import SGP4
from ephemerista.scenarios import Scenario
from ephemerista.time import Time, TimeDelta


@pytest.fixture(scope="session", autouse=True)
def init_ephemerista():
    """Initialize ephemerista with test data."""
    ephemerista.init(eop_path="tests/resources/finals2000A.all.csv", spk_path="tests/resources/de440s.bsp")


@pytest.fixture
def phasma_spacecraft():
    """Create PHASMA spacecraft for testing."""
    tle = """SENTINEL-6
1 46984U 20086A   24319.21552651 -.00000061  00000+0  71254-6 0  9995
2 46984  66.0411 259.6585 0007844 270.2444  89.7673 12.80930600186045
"""
    propagator = SGP4(tle=tle)
    return Asset(model=Spacecraft(propagator=propagator), name="PHASMA")


@pytest.fixture
def small_walker_star_constellation():
    """Create small Walker Star constellation for testing."""
    return WalkerStar(
        time=Time.from_iso("TDB", "2016-05-30T12:00:00"),
        nsats=6,
        nplanes=2,
        semi_major_axis=7000,
        inclination=45,
        eccentricity=0.0,
        periapsis_argument=90,
    )


@pytest.fixture
def medium_walker_star_constellation():
    """Create medium Walker Star constellation for testing."""
    return WalkerStar(
        time=Time.from_iso("TDB", "2016-05-30T12:00:00"),
        nsats=12,
        nplanes=4,
        semi_major_axis=7000,
        inclination=45,
        eccentricity=0.0,
        periapsis_argument=90,
    )


@pytest.fixture
def ground_stations():
    """Create ground stations for testing."""
    return [
        Asset(
            model=GroundStation.from_lla(-77.0369, 38.9072),  # Washington DC
            name="Washington DC",
        ),
        Asset(
            model=GroundStation.from_lla(-0.1278, 51.5074),  # London
            name="London",
        ),
        Asset(
            model=GroundStation.from_lla(139.6503, 35.6762),  # Tokyo
            name="Tokyo",
        ),
        Asset(
            model=GroundStation.from_lla(151.2093, -33.8688),  # Sydney
            name="Sydney",
        ),
    ]


def run_visibility_analysis_sequential(scenario: Scenario):
    """Helper function to run sequential visibility analysis."""
    visibility = Visibility(scenario=scenario, parallel=False)
    results = visibility.analyze()
    return results


def run_visibility_analysis_parallel(scenario: Scenario):
    """Helper function to run parallel visibility analysis."""
    visibility = Visibility(scenario=scenario, parallel=True)
    results = visibility.analyze()
    return results


@pytest.mark.benchmark
class TestVisibilityBenchmarks:
    """Benchmark tests for visibility analysis using pytest-benchmark."""

    def test_benchmark_single_sat_sequential(self, benchmark, phasma_spacecraft, ground_stations):
        """Benchmark single satellite sequential visibility analysis."""
        start_time = phasma_spacecraft.model.propagator.time
        end_time = start_time + TimeDelta.from_hours(12)

        scenario = Scenario(
            assets=[phasma_spacecraft, *ground_stations],
            name="Single satellite sequential visibility",
            start_time=start_time,
            end_time=end_time,
        )

        # Use pytest-benchmark to measure performance
        result = benchmark(run_visibility_analysis_sequential, scenario)

        # Validate results
        assert result is not None
        assert hasattr(result, "passes")

        # Print scenario statistics for reference
        print("\nSequential - Single satellite scenario stats:")
        print(f"  Spacecraft: {len([a for a in scenario.all_assets if isinstance(a.model, Spacecraft)])}")
        print(f"  Ground stations: {len([a for a in scenario.all_assets if isinstance(a.model, GroundStation)])}")
        print(f"  Duration: {end_time - start_time}")

    def test_benchmark_single_sat_parallel(self, benchmark, phasma_spacecraft, ground_stations):
        """Benchmark single satellite parallel visibility analysis."""
        start_time = phasma_spacecraft.model.propagator.time
        end_time = start_time + TimeDelta.from_hours(12)

        scenario = Scenario(
            assets=[phasma_spacecraft, *ground_stations],
            name="Single satellite parallel visibility",
            start_time=start_time,
            end_time=end_time,
        )

        # Use pytest-benchmark to measure performance
        result = benchmark(run_visibility_analysis_parallel, scenario)

        # Validate results
        assert result is not None
        assert hasattr(result, "passes")

        # Print scenario statistics for reference
        print("\nParallel - Single satellite scenario stats:")
        print(f"  Spacecraft: {len([a for a in scenario.all_assets if isinstance(a.model, Spacecraft)])}")
        print(f"  Ground stations: {len([a for a in scenario.all_assets if isinstance(a.model, GroundStation)])}")
        print(f"  Duration: {end_time - start_time}")

    def test_benchmark_small_constellation_sequential(
        self, benchmark, small_walker_star_constellation, ground_stations
    ):
        """Benchmark small constellation sequential visibility analysis."""
        start_time = Time.from_iso("TDB", "2016-05-30T12:00:00")
        end_time = start_time + TimeDelta.from_hours(8)

        scenario = Scenario(
            name="Small constellation sequential visibility",
            start_time=start_time,
            end_time=end_time,
            assets=ground_stations,
            constellations=[Constellation(model=small_walker_star_constellation)],
        )

        result = benchmark(run_visibility_analysis_sequential, scenario)

        # Validate results
        assert result is not None
        assert hasattr(result, "passes")

        print("\nSequential - Small constellation scenario stats:")
        print(f"  Spacecraft: {len([a for a in scenario.all_assets if isinstance(a.model, Spacecraft)])}")
        print(f"  Ground stations: {len([a for a in scenario.all_assets if isinstance(a.model, GroundStation)])}")
        print(f"  Duration: {end_time - start_time}")

    def test_benchmark_small_constellation_parallel(self, benchmark, small_walker_star_constellation, ground_stations):
        """Benchmark small constellation parallel visibility analysis."""
        start_time = Time.from_iso("TDB", "2016-05-30T12:00:00")
        end_time = start_time + TimeDelta.from_hours(8)

        scenario = Scenario(
            name="Small constellation parallel visibility",
            start_time=start_time,
            end_time=end_time,
            assets=ground_stations,
            constellations=[Constellation(model=small_walker_star_constellation)],
        )

        result = benchmark(run_visibility_analysis_parallel, scenario)

        # Validate results
        assert result is not None
        assert hasattr(result, "passes")

        print("\nParallel - Small constellation scenario stats:")
        print(f"  Spacecraft: {len([a for a in scenario.all_assets if isinstance(a.model, Spacecraft)])}")
        print(f"  Ground stations: {len([a for a in scenario.all_assets if isinstance(a.model, GroundStation)])}")
        print(f"  Duration: {end_time - start_time}")

    def test_benchmark_medium_constellation_sequential(
        self, benchmark, medium_walker_star_constellation, ground_stations
    ):
        """Benchmark medium constellation sequential visibility analysis."""
        start_time = Time.from_iso("TDB", "2016-05-30T12:00:00")
        end_time = start_time + TimeDelta.from_hours(6)

        scenario = Scenario(
            name="Medium constellation sequential visibility",
            start_time=start_time,
            end_time=end_time,
            assets=ground_stations,
            constellations=[Constellation(model=medium_walker_star_constellation)],
        )

        result = benchmark(run_visibility_analysis_sequential, scenario)

        # Validate results
        assert result is not None
        assert hasattr(result, "passes")

        print("\nSequential - Medium constellation scenario stats:")
        print(f"  Spacecraft: {len([a for a in scenario.all_assets if isinstance(a.model, Spacecraft)])}")
        print(f"  Ground stations: {len([a for a in scenario.all_assets if isinstance(a.model, GroundStation)])}")
        print(f"  Duration: {end_time - start_time}")

    def test_benchmark_medium_constellation_parallel(
        self, benchmark, medium_walker_star_constellation, ground_stations
    ):
        """Benchmark medium constellation parallel visibility analysis."""
        start_time = Time.from_iso("TDB", "2016-05-30T12:00:00")
        end_time = start_time + TimeDelta.from_hours(6)

        scenario = Scenario(
            name="Medium constellation parallel visibility",
            start_time=start_time,
            end_time=end_time,
            assets=ground_stations,
            constellations=[Constellation(model=medium_walker_star_constellation)],
        )

        result = benchmark(run_visibility_analysis_parallel, scenario)

        # Validate results
        assert result is not None
        assert hasattr(result, "passes")

        print("\nParallel - Medium constellation scenario stats:")
        print(f"  Spacecraft: {len([a for a in scenario.all_assets if isinstance(a.model, Spacecraft)])}")
        print(f"  Ground stations: {len([a for a in scenario.all_assets if isinstance(a.model, GroundStation)])}")
        print(f"  Duration: {end_time - start_time}")


# Grouped benchmarks for easy comparison
@pytest.mark.benchmark
def test_benchmark_group_sequential(benchmark, phasma_spacecraft, ground_stations):
    """Group for sequential visibility benchmarks."""
    start_time = phasma_spacecraft.model.propagator.time
    end_time = start_time + TimeDelta.from_hours(8)

    scenario = Scenario(
        assets=[phasma_spacecraft, *ground_stations],
        name="Sequential group test",
        start_time=start_time,
        end_time=end_time,
    )

    # Add custom metadata for benchmark grouping
    benchmark.group = "sequential"
    result = benchmark(run_visibility_analysis_sequential, scenario)
    assert result is not None


@pytest.mark.benchmark
def test_benchmark_group_parallel(benchmark, phasma_spacecraft, ground_stations):
    """Group for parallel visibility benchmarks."""
    start_time = phasma_spacecraft.model.propagator.time
    end_time = start_time + TimeDelta.from_hours(8)

    scenario = Scenario(
        assets=[phasma_spacecraft, *ground_stations],
        name="Parallel group test",
        start_time=start_time,
        end_time=end_time,
    )

    # Add custom metadata for benchmark grouping
    benchmark.group = "parallel"
    result = benchmark(run_visibility_analysis_parallel, scenario)
    assert result is not None


# Utility for running specific benchmark subsets
if __name__ == "__main__":
    # Examples of running specific benchmark groups:
    # pytest tests/test_visibility_benchmarks.py -v --benchmark-only
    # pytest tests/test_visibility_benchmarks.py -v --benchmark-only --benchmark-group-by=group
    # pytest tests/test_visibility_benchmarks.py -v --benchmark-only --benchmark-save=baseline
    # pytest tests/test_visibility_benchmarks.py -v --benchmark-only --benchmark-compare=baseline
    pytest.main([__file__, "-v", "--benchmark-only"])
