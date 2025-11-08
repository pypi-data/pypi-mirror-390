import json
from pathlib import Path

import numpy as np
import pytest

from ephemerista.constellation.design import (
    AbstractWalkerOrSocConstellation,
    Constellation,
    Flower,
    StreetOfCoverage,
    WalkerDelta,
    WalkerStar,
)
from ephemerista.coords.twobody import Keplerian
from ephemerista.propagators.orekit.numerical import NumericalPropagator
from ephemerista.propagators.orekit.semianalytical import SemiAnalyticalPropagator
from ephemerista.scenarios import Scenario
from ephemerista.time import Time, TimeDelta


def test_walker_star_not_physical():
    time = Time.from_iso("TDB", "2016-05-30T12:00:00")

    # Case 2. Invalid constellation, not physical
    with pytest.raises(ValueError, match="The constellation is not physical: Perigee crosses Earth's Radius!"):
        WalkerStar(
            time=time,
            nsats=10,
            nplanes=2,
            semi_major_axis=3000,
            inclination=45,
            eccentricity=0.0,
            periapsis_argument=90,
        )


def test_walker_star_wrong_nplanes_nsats_multiple():
    time = Time.from_iso("TDB", "2016-05-30T12:00:00")

    # Case 3. Invalid constellation, wrong number of planes
    with pytest.raises(
        ValueError,
        match=r"The number of satellites per plane must be a multiple of the number of planes for a constellation\.",
    ):
        WalkerStar(
            time=time,
            nsats=47,
            nplanes=6,
            semi_major_axis=7000,
            inclination=45,
            eccentricity=0.0,
            periapsis_argument=90,
        )


def test_walker_star_wrong_phasing():
    time = Time.from_iso("TDB", "2016-05-30T12:00:00")

    # Case 2. Invalid constellation, not physical
    with pytest.raises(
        ValueError,
        match=r"The number of satellites per plane must be a multiple of the number of planes for a constellation\.",
    ):
        WalkerStar(
            time=time,
            nsats=64,
            nplanes=6,
            semi_major_axis=7000,
            inclination=45,
            eccentricity=0.0,
            periapsis_argument=90,
            phasing=10,
        )


OREKIT_PROP_CLASSES = [NumericalPropagator, SemiAnalyticalPropagator]


def test_scenario_minimal():
    start_time = Time.from_iso("TDB", "2016-05-30T12:00:00")
    duration_hours = 2.0

    nsats = 16
    ws = WalkerStar(
        time=start_time,
        nsats=nsats,
        nplanes=8,
        semi_major_axis=7000,
        inclination=45,
        eccentricity=0.0,
        periapsis_argument=90,
    )

    scenario = Scenario(
        name="Constellation",
        constellations=[Constellation(model=ws)],
        start_time=start_time,
        end_time=start_time + TimeDelta.from_hours(duration_hours),
    )

    assert len(scenario.all_assets) == nsats


def compare_against_matlab_json(json_path: Path, constellation: AbstractWalkerOrSocConstellation):
    with open(json_path) as f:
        ws_matlab_json_raw = json.load(f)
        ws_matlab_satellites = ws_matlab_json_raw["satellites"]

    for i, matlab_sat_dict in enumerate(ws_matlab_satellites):
        matlab_sat = Keplerian.model_validate(matlab_sat_dict)
        # Overwriting satellite name because Matlab uses different naming conventions for constellation satellites
        assert matlab_sat == list(constellation.satellites.values())[i]


def test_against_matlab_ws_1(resources):
    start_time = Time.from_iso("TDB", "2016-05-30T12:00:00")
    ws_ephemerista = WalkerStar(
        time=start_time,
        nsats=64,
        nplanes=8,
        semi_major_axis=7000,
        inclination=45,
        eccentricity=0.0,
        periapsis_argument=0,
        phasing=2,
        name="constellation1",
    )

    compare_against_matlab_json(resources / "constellation" / "constellation1_walker_star_matlab.json", ws_ephemerista)


def test_against_matlab_ws_oneweb(resources):
    start_time = Time.from_iso("TDB", "2016-05-30T12:00:00")
    ws_ephemerista = WalkerStar(
        time=start_time,
        nsats=648,
        nplanes=18,
        semi_major_axis=7578,
        inclination=86.4,
        eccentricity=0.0,
        periapsis_argument=0,
        name="oneweb",
    )

    compare_against_matlab_json(resources / "constellation" / "oneweb_walker_star_matlab.json", ws_ephemerista)


def test_against_matlab_wd_1(resources):
    start_time = Time.from_iso("TDB", "2016-05-30T12:00:00")
    wd_ephemerista = WalkerDelta(
        time=start_time,
        nsats=72,
        nplanes=9,
        semi_major_axis=7000,
        inclination=98.0,
        eccentricity=0.0,
        periapsis_argument=0,
        phasing=4,
        name="constellation2",
    )

    compare_against_matlab_json(resources / "constellation" / "constellation2_walker_delta_matlab.json", wd_ephemerista)


def test_against_matlab_wd_galileo_like(resources):
    start_time = Time.from_iso("TDB", "2016-05-30T12:00:00")
    wd_ephemerista = WalkerDelta(
        time=start_time,
        nsats=24,
        nplanes=3,
        semi_major_axis=29599.8,
        inclination=56.0,
        eccentricity=0.0,
        periapsis_argument=0,
        phasing=1,
        name="galileo",
    )

    compare_against_matlab_json(resources / "constellation" / "galileo_walker_delta_matlab.json", wd_ephemerista)


def test_soc_too_little_sats():
    with pytest.raises(
        ValueError,
        match="This Street-of-Coverage constellation has too little satellites to provide 1-fold coverage",
    ):
        StreetOfCoverage(
            time=Time.from_iso("TDB", "2016-05-30T12:00:00"),
            nsats=8,
            nplanes=4,
            semi_major_axis=7158,
            inclination=86.4,
            eccentricity=0.00001,
            periapsis_argument=90,
            coverage_fold=1,
        )


@pytest.mark.parametrize("inclination", [0, 180])
def test_soc_zero_inclination(inclination):
    with pytest.raises(
        ValueError,
        match="A Street-of-Coverage constellation cannot be used for equatorial orbits",
    ):
        StreetOfCoverage(
            time=Time.from_iso("TDB", "2016-05-30T12:00:00"),
            nsats=66,
            nplanes=6,
            semi_major_axis=7158,
            inclination=inclination,
            eccentricity=0.00001,
            periapsis_argument=90,
            coverage_fold=1,
        )


def test_soc_iridium_huang_et_al_2021():
    """
    Checks our implementation of a SOC constellation against the Iridium constellation parameters presented in table 4
    of Huang et al 2021 (see full citation in the StreetOfCoverage docstring).
    """
    constel = StreetOfCoverage(
        time=Time.from_iso("TDB", "2016-05-30T12:00:00"),
        nsats=66,
        nplanes=6,
        semi_major_axis=7158,
        inclination=86.4,
        eccentricity=0.0,
        periapsis_argument=0,
        coverage_fold=1,
    )
    assert np.rad2deg(constel._nu_optimal_rad) == pytest.approx(20.0, abs=0.05)
    assert np.rad2deg(constel._raan_spacing_co_rotating()) == pytest.approx(31.6, abs=0.05)
    assert np.rad2deg(constel._raan_spacing_counter_rotating()) == pytest.approx(158.0, abs=0.05)
    assert np.rad2deg(constel._anom_spacing_intra_plane()) == pytest.approx(32.7, abs=0.05)
    assert np.rad2deg(constel._anom_spacing_inter_plane()) == pytest.approx(14.3, abs=0.05)


# Reference data from [1] and [2] (see Flower docstring)
max_sats_test = [9, 1028, 4, 4, 7, 4, 110, 342, 343]
raan_spacing_test = [-40, -90, -90, -90, -51.42, -180, -252, -113.68, -168.97]
ma_spacing_test = [320, 269.2, 360, 270, 154.28, 270, 350.18, 233.68, 2.099]


@pytest.mark.parametrize(
    """num_petals, num_days, num_sats, phasing_n, phasing_d, perigee_argument, inclination, perigee_altitude,
    beam_width, nsats_max, raan_spacing, ma_spacing""",
    [
        (8, 1, 9, 1, 9, 0, 0, 2500, 20, max_sats_test[0], raan_spacing_test[0], ma_spacing_test[0]),
        (769, 257, 4, 1, 4, 0, 0, 600, 20, max_sats_test[1], raan_spacing_test[1], ma_spacing_test[1]),
        (4, 1, 4, 1, 4, 0, 0, 600, 20, max_sats_test[2], raan_spacing_test[2], ma_spacing_test[2]),
        (3, 1, 4, 1, 4, 0, 0, 600, 20, max_sats_test[3], raan_spacing_test[3], ma_spacing_test[3]),
        (3, 1, 4, 1, 7, 0, 0, 600, 20, max_sats_test[4], raan_spacing_test[4], ma_spacing_test[4]),
        (3, 2, 4, 1, 2, 0, 0, 600, 20, max_sats_test[5], raan_spacing_test[5], ma_spacing_test[5]),
        (31, 11, 30, 7, 10, 0, 0, 9000, 20, max_sats_test[6], raan_spacing_test[6], ma_spacing_test[6]),
        (37, 18, 57, 6, 19, 0, 0, 19702, 20, max_sats_test[7], raan_spacing_test[7], ma_spacing_test[7]),
        (15, 7, 49, 23, 49, 0, 0, 19702, 20, max_sats_test[8], raan_spacing_test[8], ma_spacing_test[8]),
    ],
)
def test_flower(
    num_petals,
    num_days,
    num_sats,
    phasing_n,
    phasing_d,
    perigee_argument,
    inclination,
    perigee_altitude,
    beam_width,  # noqa: ARG001
    nsats_max,
    raan_spacing,
    ma_spacing,
):
    """
    Tests the Flower constellation against reference data from [1] and [2] (see Flower docstring)
    """
    start_time = Time.from_iso("TDB", "2016-05-30T12:00:00")

    constel = Flower(
        time=start_time,
        inclination=inclination,
        periapsis_argument=perigee_argument,
        perigee_altitude=perigee_altitude,
        nsats=num_sats,
        n_petals=num_petals,
        n_days=num_days,
        phasing_n=phasing_n,
        phasing_d=phasing_d,
    )
    assert constel._nsats_max == nsats_max
    assert constel._raan_spacing == pytest.approx(raan_spacing, abs=0.1)
    assert constel._anomaly_spacing == pytest.approx(ma_spacing, abs=0.1)
