"""
Benchmark tests for coverage analysis performance using pytest-benchmark.

This module contains benchmark tests based on scenarios from the constellations.ipynb
and coverage.ipynb notebooks to measure performance and detect regressions.
"""

import pytest

import ephemerista
from ephemerista.analysis.coverage import Coverage
from ephemerista.assets import Asset, Spacecraft
from ephemerista.constellation.design import Constellation, StreetOfCoverage, WalkerStar
from ephemerista.propagators.sgp4 import SGP4
from ephemerista.scenarios import Scenario, polygonize_aoi
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
def walker_star_constellation():
    """Create Walker Star constellation for testing."""
    return WalkerStar(
        time=Time.from_iso("TDB", "2016-05-30T12:00:00"),
        nsats=18,
        nplanes=6,
        semi_major_axis=7000,
        inclination=45,
        eccentricity=0.0,
        periapsis_argument=90,
    )


@pytest.fixture
def small_walker_star_constellation():
    """Create smaller Walker Star constellation for faster testing."""
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
def iridium_constellation():
    """Create Iridium-like StreetOfCoverage constellation for testing."""
    return StreetOfCoverage(
        time=Time.from_iso("TDB", "2016-05-30T12:00:00"),
        nsats=66,
        nplanes=6,
        semi_major_axis=7158,
        inclination=86.4,
        eccentricity=0.0,
        periapsis_argument=0,
        coverage_fold=1,
    )


@pytest.fixture
def small_aoi():
    """Create small area of interest for testing."""
    # Simple polygon around Europe
    aoi_geom = {
        "type": "Polygon",
        "coordinates": [[[-10.0, 35.0], [30.0, 35.0], [30.0, 70.0], [-10.0, 70.0], [-10.0, 35.0]]],
    }
    return polygonize_aoi(aoi_geom_dict=aoi_geom, res=2, min_elevation_deg=45.0)


@pytest.fixture
def large_aoi():
    """Create large area of interest for testing."""
    # Half earth polygon
    aoi_geom = {
        "type": "Polygon",
        "coordinates": [[[-140.0, 60.0], [20.0, 60.0], [20.0, -20.0], [-140.0, -20.0], [-140.0, 60.0]]],
    }
    return polygonize_aoi(aoi_geom_dict=aoi_geom, res=1, min_elevation_deg=45.0)


@pytest.fixture
def medium_aoi():
    """Create medium area of interest for testing."""
    # Regional polygon
    aoi_geom = {
        "type": "Polygon",
        "coordinates": [[[-50.0, 30.0], [10.0, 30.0], [10.0, 70.0], [-50.0, 70.0], [-50.0, 30.0]]],
    }
    return polygonize_aoi(aoi_geom_dict=aoi_geom, res=1, min_elevation_deg=30.0)


def run_coverage_analysis(scenario: Scenario):
    """Helper function to run coverage analysis."""
    coverage = Coverage(scenario=scenario)
    results = coverage.analyze()
    return results


@pytest.mark.benchmark
class TestCoverageBenchmarks:
    """Benchmark tests for coverage analysis using pytest-benchmark."""

    def test_benchmark_single_sat_small_aoi(self, benchmark, phasma_spacecraft, small_aoi):
        """Benchmark single satellite over small area - baseline test."""
        start_time = phasma_spacecraft.model.propagator.time
        end_time = start_time + TimeDelta.from_hours(24)

        scenario = Scenario(
            assets=[phasma_spacecraft],
            name="Single satellite small AOI",
            start_time=start_time,
            end_time=end_time,
            areas_of_interest=small_aoi,
            auto_discretize=False,
        )

        # Use pytest-benchmark to measure performance
        result = benchmark(run_coverage_analysis, scenario)

        # Validate results
        assert result.coverage_percent is not None
        assert len(result.coverage_percent) > 0
        assert all(0 <= p <= 1 for p in result.coverage_percent)

        # Print scenario statistics for reference
        print("\nScenario stats:")
        print(f"  Assets: {len(scenario.all_assets)}")
        print(f"  Ground locations: {len(scenario.ground_locations)}")
        print(f"  Areas: {len(scenario.discretized_areas)}")

    def test_benchmark_single_sat_medium_aoi(self, benchmark, phasma_spacecraft, medium_aoi):
        """Benchmark single satellite over medium area."""
        start_time = phasma_spacecraft.model.propagator.time
        end_time = start_time + TimeDelta.from_hours(12)  # Shorter duration for medium test

        scenario = Scenario(
            assets=[phasma_spacecraft],
            name="Single satellite medium AOI",
            start_time=start_time,
            end_time=end_time,
            areas_of_interest=medium_aoi,
            auto_discretize=False,
        )

        result = benchmark(run_coverage_analysis, scenario)

        # Validate results
        assert result.coverage_percent is not None
        assert len(result.coverage_percent) > 0

        print("\nScenario stats:")
        print(f"  Assets: {len(scenario.all_assets)}")
        print(f"  Ground locations: {len(scenario.ground_locations)}")
        print(f"  Areas: {len(scenario.discretized_areas)}")

    def test_benchmark_single_sat_large_aoi(self, benchmark, phasma_spacecraft, large_aoi):
        """Benchmark single satellite over large area - stress test."""
        start_time = phasma_spacecraft.model.propagator.time
        end_time = start_time + TimeDelta.from_hours(6)  # Shorter duration for large area

        scenario = Scenario(
            assets=[phasma_spacecraft],
            name="Single satellite large AOI",
            start_time=start_time,
            end_time=end_time,
            areas_of_interest=large_aoi,
            auto_discretize=False,
        )

        result = benchmark(run_coverage_analysis, scenario)

        # Validate results
        assert result.coverage_percent is not None
        assert len(result.coverage_percent) > 0

        print("\nScenario stats:")
        print(f"  Assets: {len(scenario.all_assets)}")
        print(f"  Ground locations: {len(scenario.ground_locations)}")
        print(f"  Areas: {len(scenario.discretized_areas)}")

    def test_benchmark_small_walker_star_constellation(self, benchmark, small_walker_star_constellation, medium_aoi):
        """Benchmark small Walker Star constellation - for faster testing."""
        start_time = Time.from_iso("TDB", "2016-05-30T12:00:00")
        end_time = start_time + TimeDelta.from_hours(6)

        scenario = Scenario(
            name="Small Walker Star Constellation",
            start_time=start_time,
            end_time=end_time,
            areas_of_interest=medium_aoi,
            constellations=[Constellation(model=small_walker_star_constellation)],
            auto_discretize=False,
        )

        result = benchmark(run_coverage_analysis, scenario)

        # Validate results
        assert result.coverage_percent is not None
        assert len(result.coverage_percent) > 0

        print("\nScenario stats:")
        print(f"  Assets: {len(scenario.all_assets)}")
        print(f"  Ground locations: {len(scenario.ground_locations)}")
        print(f"  Areas: {len(scenario.discretized_areas)}")

    def test_benchmark_walker_star_constellation(self, benchmark, walker_star_constellation, large_aoi):
        """Benchmark Walker Star constellation - from constellations.ipynb."""
        start_time = Time.from_iso("TDB", "2016-05-30T12:00:00")
        end_time = start_time + TimeDelta.from_hours(6)  # Shorter for benchmark

        scenario = Scenario(
            name="Walker Star Constellation",
            start_time=start_time,
            end_time=end_time,
            areas_of_interest=large_aoi,
            constellations=[Constellation(model=walker_star_constellation)],
            auto_discretize=False,
        )

        result = benchmark(run_coverage_analysis, scenario)

        # Validate results
        assert result.coverage_percent is not None
        assert len(result.coverage_percent) > 0
        assert len(scenario.all_assets) == 18, "Wrong number of satellites"

        print("\nScenario stats:")
        print(f"  Assets: {len(scenario.all_assets)}")
        print(f"  Ground locations: {len(scenario.ground_locations)}")
        print(f"  Areas: {len(scenario.discretized_areas)}")

    @pytest.mark.slow
    def test_benchmark_iridium_constellation_short(self, benchmark, iridium_constellation, large_aoi):
        """Benchmark Iridium constellation short duration - from constellations.ipynb."""
        start_time = Time.from_iso("TDB", "2016-05-30T12:00:00")
        end_time = start_time + TimeDelta.from_hours(2)

        scenario = Scenario(
            name="Iridium Constellation Short",
            start_time=start_time,
            end_time=end_time,
            areas_of_interest=large_aoi,
            constellations=[Constellation(model=iridium_constellation)],
            auto_discretize=False,
        )

        result = benchmark(run_coverage_analysis, scenario)

        # Validate results
        assert result.coverage_percent is not None
        assert len(result.coverage_percent) > 0
        assert len(scenario.all_assets) == 66, "Wrong number of satellites"

        print("\nScenario stats:")
        print(f"  Assets: {len(scenario.all_assets)}")
        print(f"  Ground locations: {len(scenario.ground_locations)}")
        print(f"  Areas: {len(scenario.discretized_areas)}")

    @pytest.mark.slow
    def test_benchmark_iridium_constellation_long(self, benchmark, iridium_constellation, medium_aoi):
        """Benchmark Iridium constellation long duration - most demanding test."""
        start_time = Time.from_iso("TDB", "2016-05-30T12:00:00")
        end_time = start_time + TimeDelta.from_hours(12)  # Reduced from 24h for practical benchmarking

        scenario = Scenario(
            name="Iridium Constellation Long",
            start_time=start_time,
            end_time=end_time,
            areas_of_interest=medium_aoi,  # Use medium AOI to keep runtime reasonable
            constellations=[Constellation(model=iridium_constellation)],
            auto_discretize=False,
        )

        result = benchmark(run_coverage_analysis, scenario)

        # Validate results
        assert result.coverage_percent is not None
        assert len(result.coverage_percent) > 0
        assert len(scenario.all_assets) == 66, "Wrong number of satellites"

        print("\nScenario stats:")
        print(f"  Assets: {len(scenario.all_assets)}")
        print(f"  Ground locations: {len(scenario.ground_locations)}")
        print(f"  Areas: {len(scenario.discretized_areas)}")

    # @pytest.mark.slow
    # def test_benchmark_slow_scenario(self, benchmark):
    #     """Benchmark slow scenario from slow_scenario.json - complex constellation with high discretization."""
    #     # Load the slow scenario from JSON
    #     scn_json = Path("tests/resources/slow_scenario.json").read_text()
    #     scenario = Scenario.model_validate_json(scn_json)

    #     # Ensure the scenario has reasonable parameters for benchmarking
    #     # (the original scenario has 24 satellites over Europe with 1-degree discretization)

    #     result = benchmark(run_coverage_analysis, scenario)

    #     # Validate results
    #     assert result.coverage_percent is not None
    #     assert len(result.coverage_percent) > 0
    #     assert all(0 <= p <= 1 for p in result.coverage_percent)

    #     # Validate that we have the expected constellation size
    #     assert len(scenario.all_assets) == 24, f"Expected 24 satellites, got {len(scenario.all_assets)}"

    #     print("\nSlow scenario stats:")
    #     print(f"  Scenario name: {scenario.name}")
    #     print(f"  Assets: {len(scenario.all_assets)}")
    #     print(f"  Ground locations: {len(scenario.ground_locations)}")
    #     print(f"  Areas: {len(scenario.discretized_areas)}")
    #     print(f"  Discretization resolution: {scenario.discretization_resolution}")
    #     print(f"  Duration: {scenario.end_time - scenario.start_time}")

    # def test_benchmark_optimized_scenario(self, benchmark):
    #     """Benchmark optimized scenario - reduced complexity version of slow_scenario.json."""
    #     # Load the optimized scenario from JSON
    #     scn_json = Path("tests/resources/optimized_scenario.json").read_text()
    #     scenario = Scenario.model_validate_json(scn_json)

    #     # This should be much faster than the slow scenario due to optimizations:
    #     # - 3° discretization resolution (vs 1°)
    #     # - Reduced computational complexity

    #     result = benchmark(run_coverage_analysis, scenario)

    #     # Validate results
    #     assert result.coverage_percent is not None
    #     assert len(result.coverage_percent) > 0
    #     assert all(0 <= p <= 1 for p in result.coverage_percent)

    #     # Validate that we have the expected constellation size
    #     assert len(scenario.all_assets) == 24, f"Expected 24 satellites, got {len(scenario.all_assets)}"

    #     print("\nOptimized scenario stats:")
    #     print(f"  Scenario name: {scenario.name}")
    #     print(f"  Assets: {len(scenario.all_assets)}")
    #     print(f"  Ground locations: {len(scenario.ground_locations)}")
    #     print(f"  Areas: {len(scenario.discretized_areas)}")
    #     print(f"  Discretization resolution: {scenario.discretization_resolution}")
    #     print(f"  Duration: {scenario.end_time - scenario.start_time}")


# Custom benchmark groups for different types of tests
@pytest.mark.benchmark
def test_benchmark_group_single_satellite(benchmark, phasma_spacecraft, small_aoi):
    """Group for single satellite benchmarks."""
    start_time = phasma_spacecraft.model.propagator.time
    end_time = start_time + TimeDelta.from_hours(12)

    scenario = Scenario(
        assets=[phasma_spacecraft],
        name="Single satellite group test",
        start_time=start_time,
        end_time=end_time,
        areas_of_interest=small_aoi,
        auto_discretize=False,
    )

    # Add custom metadata for benchmark grouping
    benchmark.group = "single_satellite"
    result = benchmark(run_coverage_analysis, scenario)
    assert result.coverage_percent is not None


@pytest.mark.benchmark
def test_benchmark_group_constellation(benchmark, small_walker_star_constellation, small_aoi):
    """Group for constellation benchmarks."""
    start_time = Time.from_iso("TDB", "2016-05-30T12:00:00")
    end_time = start_time + TimeDelta.from_hours(4)

    scenario = Scenario(
        name="Constellation group test",
        start_time=start_time,
        end_time=end_time,
        areas_of_interest=small_aoi,
        constellations=[Constellation(model=small_walker_star_constellation)],
        auto_discretize=False,
    )

    # Add custom metadata for benchmark grouping
    benchmark.group = "constellation"
    result = benchmark(run_coverage_analysis, scenario)
    assert result.coverage_percent is not None


# Utility for running specific benchmark subsets
if __name__ == "__main__":
    # Examples of running specific benchmark groups:
    # pytest tests/test_coverage_benchmarks.py -v --benchmark-only
    # pytest tests/test_coverage_benchmarks.py -v --benchmark-only --benchmark-group-by=group
    # pytest tests/test_coverage_benchmarks.py -v --benchmark-only --benchmark-save=baseline
    # pytest tests/test_coverage_benchmarks.py -v --benchmark-only --benchmark-compare=baseline
    pytest.main([__file__, "-v", "--benchmark-only"])
