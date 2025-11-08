import json
from pathlib import Path

import pytest
from geojson_pydantic import Feature, Polygon

from ephemerista.coords.trajectories import Trajectory
from ephemerista.scenarios import CURRENT_SCENARIO_VERSION, Scenario
from ephemerista.time import Time

TEST_DIR = Path(__file__).parent


def test_deserialization():
    scn_json = TEST_DIR.joinpath("resources/lunar/scenario.json").resolve().read_text()
    scn = Scenario.model_validate_json(scn_json)
    assert isinstance(scn, Scenario)


def test_propagation(lunar_scenario):
    asset = lunar_scenario["Lunar Transfer"]
    ensemble = lunar_scenario.propagate()
    assert isinstance(ensemble[asset], Trajectory)


def test_area_discretization_mapping():
    """Test that area discretization correctly tracks original area mapping."""

    # Create two simple areas
    area1 = Feature[Polygon, dict](
        geometry=Polygon(
            coordinates=[[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], type="Polygon"
        ),
        properties={"name": "Area1"},
        type="Feature",
    )

    area2 = Feature[Polygon, dict](
        geometry=Polygon(
            coordinates=[[[20.0, 20.0], [30.0, 20.0], [30.0, 30.0], [20.0, 30.0], [20.0, 20.0]]], type="Polygon"
        ),
        properties={"name": "Area2"},
        type="Feature",
    )

    # Test with discretization
    scenario = Scenario(
        name="Test Scenario",
        start_time=Time.from_iso("TDB", "2024-01-01T00:00:00"),
        end_time=Time.from_iso("TDB", "2024-01-01T01:00:00"),
        areas_of_interest=[area1, area2],
        discretization_method="rectangles",
        discretization_resolution=5.0,
        auto_discretize=True,
    )

    # Verify basic properties
    assert len(scenario.areas_of_interest) == 2
    assert len(scenario.discretized_areas) > 2  # Should be discretized

    # Test mapping functions
    original_to_discretized = scenario.get_original_to_discretized_mapping()
    discretized_to_original = scenario.get_discretized_to_original_mapping()

    # Verify mappings are consistent
    assert len(original_to_discretized) == 2
    assert 0 in original_to_discretized
    assert 1 in original_to_discretized

    # Check that all discretized polygons are accounted for
    all_discretized_ids = set()
    for polygon_ids in original_to_discretized.values():
        all_discretized_ids.update(polygon_ids)
    assert len(all_discretized_ids) == len(scenario.discretized_areas)

    # Verify reverse mapping consistency
    for discretized_id, original_id in discretized_to_original.items():
        assert discretized_id in original_to_discretized[original_id]

    # Verify original_area_id is stored in polygon properties
    for _i, polygon in enumerate(scenario.discretized_areas):
        assert "original_area_id" in polygon.properties  # type: ignore
        original_id = polygon.properties["original_area_id"]  # type: ignore
        assert original_id in [0, 1]


def test_area_discretization_without_auto_discretize():
    """Test that area mapping works correctly when auto_discretize is False."""

    area1 = Feature[Polygon, dict](
        geometry=Polygon(
            coordinates=[[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], type="Polygon"
        ),
        properties={"name": "Area1"},
        type="Feature",
    )

    scenario = Scenario(
        name="Test Scenario",
        start_time=Time.from_iso("TDB", "2024-01-01T00:00:00"),
        end_time=Time.from_iso("TDB", "2024-01-01T01:00:00"),
        areas_of_interest=[area1],
        auto_discretize=False,
    )

    # Should have 1:1 mapping
    assert len(scenario.areas_of_interest) == 1
    assert len(scenario.discretized_areas) == 1

    original_to_discretized = scenario.get_original_to_discretized_mapping()
    discretized_to_original = scenario.get_discretized_to_original_mapping()

    assert original_to_discretized[0] == [0]
    assert discretized_to_original[0] == 0

    # Verify original_area_id is still stored
    assert scenario.discretized_areas[0].properties["original_area_id"] == 0  # type: ignore


def test_scenario_version_field():
    """Test that new scenarios have the version field with the correct default value."""
    scenario = Scenario(
        name="Test Scenario",
        start_time=Time.from_iso("TDB", "2024-01-01T00:00:00"),
        end_time=Time.from_iso("TDB", "2024-01-01T01:00:00"),
    )
    assert scenario.version == CURRENT_SCENARIO_VERSION


def test_load_scenario_with_version():
    """Test loading a scenario JSON file that has a version field."""
    # The lunar scenario should now have version 1
    scenario = Scenario.load_from_file(TEST_DIR.joinpath("resources/lunar/scenario.json"))
    assert scenario.version == CURRENT_SCENARIO_VERSION
    assert scenario.name == "Lunar Scenario"


def test_load_legacy_scenario_without_version(tmp_path):
    """Test loading a legacy scenario JSON file without a version field."""
    # Create a legacy scenario without version field
    legacy_data = {
        "id": "8c65e3ad-780c-5b4a-8e5b-88131e928625",
        "name": "Legacy Scenario",
        "startTime": {
            "scale": "TAI",
            "timestamp": {"type": "utc", "value": "2022-02-01T00:00:00.000Z"},
        },
        "endTime": {
            "scale": "TAI",
            "timestamp": {"type": "utc", "value": "2022-02-02T00:00:00.000Z"},
        },
        "timeStep": 60.0,
    }

    # Write legacy scenario to temp file
    legacy_file = tmp_path / "legacy_scenario.json"
    legacy_file.write_text(json.dumps(legacy_data))

    # Load and verify it gets migrated to version 1
    scenario = Scenario.load_from_file(legacy_file)
    assert scenario.version == CURRENT_SCENARIO_VERSION
    assert scenario.name == "Legacy Scenario"


def test_load_future_version_scenario_fails(tmp_path):
    """Test that loading a scenario with a newer version than supported fails."""
    future_data = {
        "version": CURRENT_SCENARIO_VERSION + 1,  # Future version
        "id": "8c65e3ad-780c-5b4a-8e5b-88131e928625",
        "name": "Future Scenario",
        "startTime": {
            "scale": "TAI",
            "timestamp": {"type": "utc", "value": "2022-02-01T00:00:00.000Z"},
        },
        "endTime": {
            "scale": "TAI",
            "timestamp": {"type": "utc", "value": "2022-02-02T00:00:00.000Z"},
        },
        "timeStep": 60.0,
    }

    # Write future scenario to temp file
    future_file = tmp_path / "future_scenario.json"
    future_file.write_text(json.dumps(future_data))

    # Verify it raises an error
    with pytest.raises(ValueError, match=f"version {CURRENT_SCENARIO_VERSION + 1} is newer than supported"):
        Scenario.load_from_file(future_file)


def test_scenario_json_serialization_includes_version():
    """Test that serializing a scenario to JSON includes the version field."""
    scenario = Scenario(
        name="Test Scenario",
        start_time=Time.from_iso("TDB", "2024-01-01T00:00:00"),
        end_time=Time.from_iso("TDB", "2024-01-01T01:00:00"),
    )

    # Serialize to JSON
    json_str = scenario.model_dump_json()
    data = json.loads(json_str)

    # Verify version is included in JSON output
    assert "version" in data
    assert data["version"] == CURRENT_SCENARIO_VERSION
