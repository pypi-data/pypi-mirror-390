import pandas as pd
import pytest

from ephemerista.analysis.visibility import Visibility, Window
from ephemerista.time import Time


@pytest.fixture
def contacts(resources) -> list[Window]:
    path = resources.joinpath("lunar/contacts.csv")
    df = pd.read_csv(path, delimiter=",", converters={"start": Time.from_utc, "stop": Time.from_utc})
    windows = []
    for _, row in df.iterrows():
        start, stop = row.array
        window = Window(start=start, stop=stop)
        windows.append(window)
    return windows


def test_visibility(lunar_scenario, contacts):
    sc = lunar_scenario["Lunar Transfer"]
    gs = lunar_scenario["CEBR"]
    vis = Visibility(scenario=lunar_scenario)
    results = vis.analyze()
    windows = results[gs, sc]
    assert len(windows) == len(contacts)
    for actual, expected in zip(windows, contacts, strict=False):
        assert actual.window.start.isclose(expected.start, rtol=1e-4)
        assert actual.window.stop.isclose(expected.stop, rtol=1e-4)


def test_visibility_parallel_vs_sequential(lunar_scenario):
    """Test that parallel and sequential visibility analysis produce identical results."""
    sc = lunar_scenario["Lunar Transfer"]
    gs = lunar_scenario["CEBR"]

    # Run sequential analysis
    vis_sequential = Visibility(scenario=lunar_scenario, parallel=False)
    results_sequential = vis_sequential.analyze()

    # Run parallel analysis
    vis_parallel = Visibility(scenario=lunar_scenario, parallel=True)
    results_parallel = vis_parallel.analyze()

    # Get windows for comparison
    windows_sequential = results_sequential[gs, sc]
    windows_parallel = results_parallel[gs, sc]

    # Verify same number of windows
    assert len(windows_sequential) == len(windows_parallel)

    # Compare each window
    for seq_pass, par_pass in zip(windows_sequential, windows_parallel, strict=True):
        # Compare window times
        assert seq_pass.window.start.isclose(par_pass.window.start, rtol=1e-10)
        assert seq_pass.window.stop.isclose(par_pass.window.stop, rtol=1e-10)
        assert seq_pass.window.duration == par_pass.window.duration

        # Compare number of time steps
        assert len(seq_pass.times) == len(par_pass.times)
        assert len(seq_pass.observables) == len(par_pass.observables)

        # Compare observables at each time step
        for seq_obs, par_obs in zip(seq_pass.observables, par_pass.observables, strict=True):
            assert abs(seq_obs.rng - par_obs.rng) < 1e-10
            assert abs(seq_obs.rng_rate - par_obs.rng_rate) < 1e-10
            assert abs(seq_obs.azimuth.radians - par_obs.azimuth.radians) < 1e-10
            assert abs(seq_obs.elevation.radians - par_obs.elevation.radians) < 1e-10
