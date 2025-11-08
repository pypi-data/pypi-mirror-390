import os
import uuid

import folium
import lox_space as lox
import numpy as np
import numpy.testing as npt
import plotly.graph_objects as go
import pytest
from geojson_pydantic import Feature, Polygon
from matplotlib.axes import Axes
from plotly.graph_objs import Figure

from ephemerista import BaseModel, ephemeris
from ephemerista.analysis.coverage import (
    Coverage,
    CoverageResults,
    load_geojson_multipolygon,
)
from ephemerista.analysis.link_budget import EnvironmentalLosses, Link, LinkBudget, LinkBudgetResults
from ephemerista.analysis.navigation import Navigation
from ephemerista.analysis.visibility import Visibility, VisibilityResults
from ephemerista.angles import Angle
from ephemerista.assets import Asset, GroundStation, Spacecraft
from ephemerista.bodies import Origin
from ephemerista.comms.antennas import ComplexAntenna, DipolePattern, MSIPattern, ParabolicPattern, SimpleAntenna
from ephemerista.comms.channels import Channel
from ephemerista.comms.frequencies import Frequency
from ephemerista.comms.receiver import ComplexReceiver, SimpleReceiver
from ephemerista.comms.systems import CommunicationSystem
from ephemerista.comms.transmitter import Transmitter
from ephemerista.comms.utils import wavelength
from ephemerista.constellation.design import Constellation, Flower, StreetOfCoverage, WalkerDelta, WalkerStar
from ephemerista.coords.events import ApsisDetector, ElevationDetector
from ephemerista.coords.trajectories import Trajectory
from ephemerista.coords.twobody import DEFAULT_FRAME, DEFAULT_ORIGIN, Cartesian, Keplerian
from ephemerista.frames import ReferenceFrame
from ephemerista.plot.groundtrack import GroundTrack
from ephemerista.propagators.orekit.ccsds import CcsdsFileFormat, parse_opm, write_oem
from ephemerista.propagators.orekit.numerical import NumericalPropagator
from ephemerista.propagators.orekit.semianalytical import SemiAnalyticalPropagator
from ephemerista.propagators.sgp4 import SGP4
from ephemerista.scenarios import Scenario, polygonize_aoi, polygonize_aoi_rectangles
from ephemerista.time import Time, TimeDelta
from ephemerista.uuid_utils import ASSET_NAMESPACE


def test_1_4_1():
    """The simulator shall use the ICRF as the default reference frame."""
    assert DEFAULT_FRAME == ReferenceFrame(abbreviation="ICRF")


@pytest.mark.parametrize(
    "frame",
    [
        "IAU_SUN",
        "IAU_MERCURY",
        "IAU_VENUS",
        "IAU_EARTH",
        "IAU_MARS",
        "IAU_JUPITER",
        "IAU_SATURN",
        "IAU_URANUS",
        "IAU_NEPTUNE",
        "IAU_PLUTO",
        "IAU_MOON",
        "IAU_PHOBOS",
        "IAU_DEIMOS",
        "IAU_IO",
        "IAU_EUROPA",
        "IAU_GANYMEDE",
        "IAU_CALLISTO",
        "IAU_AMALTHEA",
        "IAU_THEBE",
        "IAU_ADRASTEA",
        "IAU_METIS",
        "IAU_MIMAS",
        "IAU_ENCELADUS",
        "IAU_TETHYS",
        "IAU_DIONE",
        "IAU_RHEA",
        "IAU_TITAN",
        "IAU_IAPETUS",
        "IAU_PHOEBE",
        "IAU_JANUS",
        "IAU_EPIMETHEUS",
        "IAU_HELENE",
        "IAU_TELESTO",
        "IAU_CALYPSO",
        "IAU_ATLAS",
        "IAU_PROMETHEUS",
        "IAU_PANDORA",
        "IAU_PAN",
        "IAU_ARIEL",
        "IAU_UMBRIEL",
        "IAU_TITANIA",
        "IAU_OBERON",
        "IAU_MIRANDA",
        "IAU_CORDELIA",
        "IAU_OPHELIA",
        "IAU_BIANCA",
        "IAU_CRESSIDA",
        "IAU_DESDEMONA",
        "IAU_JULIET",
        "IAU_PORTIA",
        "IAU_ROSALIND",
        "IAU_BELINDA",
        "IAU_PUCK",
        "IAU_TRITON",
        "IAU_NAIAD",
        "IAU_THALASSA",
        "IAU_DESPINA",
        "IAU_GALATEA",
        "IAU_LARISSA",
        "IAU_PROTEUS",
        "IAU_CHARON",
        "IAU_GASPRA",
        "IAU_IDA",
        "IAU_CERES",
        "IAU_PALLAS",
        "IAU_VESTA",
        "IAU_LUTETIA",
        "IAU_EROS",
        "IAU_DAVIDA",
        "IAU_STEINS",
        "IAU_ITOKAWA",
    ],
)
def test_1_4_2(frame):
    """The simulator shall provide reference frame transformations from ICRF to body-fixed frames for all celestial
    bodies whose rotational elements are defined by the IAU WGCCRE reports."""
    frame = ReferenceFrame(abbreviation=frame)
    icrf = ReferenceFrame(abbreviation="ICRF")
    r0 = np.array([6068.27927, -1692.84394, -2516.61918])
    v0 = np.array([-0.660415582, 5.495938726, -5.303093233])
    time = Time.from_j2000("TDB", 0)
    s0 = Cartesian.from_rv(time, r0, v0)
    s1 = s0.to_frame(frame).to_frame(icrf)
    r1 = s1.position
    v1 = s1.velocity
    npt.assert_allclose(r0, r1, rtol=1e-7)
    npt.assert_allclose(v0, v1, rtol=1e-3)


@pytest.mark.skip("ITRF")
def test_1_4_3():
    """The simulator shall provide reference frame transformations from ICRF to ITRF and all intermediate frames."""
    raise AssertionError()


def test_1_4_4():
    """The simulator shall provide reference frame transformations from body-fixed reference frames to topocentric
    frames."""
    x_axis = np.array([0.6469358921661584, 0.07615519584215287, 0.7587320591443464])
    y_axis = np.array(
        [
            -0.049411020334552434,
            0.9970959763965771,
            -0.05794967578213965,
        ]
    )
    z_axis = np.array([-0.7609418522440956, 0.0, 0.6488200809957448])
    expected = np.vstack([x_axis, y_axis, z_axis])
    actual = GroundStation.from_lla(longitude=-4.3676, latitude=40.4527).rotation_to_topocentric()
    npt.assert_allclose(actual, expected)


def test_1_4_5():
    """The simulator shall provide reference frame transformations from ICRF to local and spacecraft-fixed reference
    frames (LVLH, etc.)."""
    r0 = np.array([6068.27927, -1692.84394, -2516.61918])
    v0 = np.array([-0.660415582, 5.495938726, -5.303093233])
    time = Time.from_j2000("TDB", 0)
    s0 = Cartesian.from_rv(time, r0, v0)
    rot = s0.rotation_lvlh()
    assert isinstance(rot, np.ndarray)


@pytest.mark.parametrize("scale", ["TAI", "TCB", "TCG", "TDB", "TT", "UT1"])
def test_1_5_1(scale):
    """The simulator shall provide transformations between the following continuous time scales:
    TAI, TT, TDB, TCG, UT1"""
    t0 = Time.from_j2000("TAI", 0)
    t1 = t0.to_scale(scale).to_scale("TAI")
    assert t0.isclose(t1)


def test_1_5_2():
    """The simulator shall provide dedicated unambiguous transformations between TAI and UTC, taking into account leap
    seconds."""
    t0 = Time.from_utc("2016-12-31T23:59:59")
    t1 = Time.from_utc("2017-01-01T00:00:00")
    assert float(t1 - t0) == 2.0


def test_1_5_3():
    """The simulator shall provide a time scale-aware epoch type."""
    time = Time.from_j2000("TAI", 0)
    assert time.scale == "TAI"


def test_1_5_4():
    """The simulator shall provide a duration type."""
    delta = TimeDelta(14.0)
    assert float(delta) == 14.0


def test_1_5_5():
    """The simulator shall support epoch-epoch and epoch-duration arithmetic."""
    t0 = Time.from_j2000("TAI", 0)
    t1 = Time.from_j2000("TAI", 1)
    assert t1 - t0 == TimeDelta.from_days(1)
    assert t0 + TimeDelta.from_days(1) == t1


def test_1_5_6():
    """The simulator shall support the following input and output formats for epochs:
    - Gregorian calendar date and time
    - Gregorian calendar day of year and time
    - Julian day number
    - J2000 Julian day number
    - Two-part Julian day numbers"""
    expected = Time.from_components("TAI", 2024, 7, 17, 12, 39, 13.14)
    actual = Time.from_day_of_year("TAI", 2024, expected.day_of_year, 12, 39, 13.14)
    assert expected.isclose(actual)
    actual = Time.from_j2000("TAI", expected.j2000)
    assert expected.isclose(actual)
    actual = Time.from_julian_date("TAI", expected.julian_date)
    assert expected.isclose(actual)
    actual = Time.from_two_part_julian_date("TAI", *expected.two_part_julian_date)
    assert expected.isclose(actual)


def test_1_6_1(lunar_transfer, lunar_visibility, phasma_link_budget):
    """The simulator shall support importing and exporting tabular data in CSV format."""
    assert hasattr(lunar_transfer, "to_csv")
    assert hasattr(lunar_transfer, "from_csv")
    assert hasattr(lunar_visibility, "to_dataframe")
    assert hasattr(phasma_link_budget, "to_dataframe")


def test_1_6_3(resources):
    """The simulator shall support importing CCSDS Orbit and Navigation Data Messages
    (CCSDS 502.0-B-2, CCSDS 505.0-B-2)."""
    opm_ex = resources / "ccsds" / "odm" / "opm" / "OPMExample5.txt"
    cart_act = parse_opm(opm_ex)

    cart_exp = Cartesian.from_rv(
        Time.from_utc("2006-06-03T00:00:00.000"),
        np.array([6655.9942, -40218.5751, -82.9177]),
        np.array([3.11548208, 0.47042605, -0.00101495]),
    )
    assert cart_act.time.isclose(cart_exp.time)
    assert cart_act.isclose(cart_exp)


def test_1_6_4(iss_trajectory):
    """The simulator shall support exporting CCSDS Orbit and Navigation Data Messages
    (CCSDS 502.0-B-2, CCSDS 505.0-B-2)."""
    dt = 300.0
    oem_file_out = "oem_tmp.txt"
    write_oem(iss_trajectory, oem_file_out, dt, CcsdsFileFormat.KVN)
    with open(oem_file_out) as f:
        first_line = f.readline()

    assert first_line.strip() == "CCSDS_OEM_VERS       = 3.0"

    if os.path.isfile(oem_file_out):
        os.remove(oem_file_out)


def test_1_6_5():
    """The simulator shall be able to read and evaluate planetary and spacecraft ephemerides in binary SPICE kernel
    format (SPK)."""
    assert isinstance(ephemeris(), lox.SPK)


def test_1_6_6():
    """The simulator shall support importing and exporting hierarchical data in JSON format."""
    assert issubclass(Scenario, BaseModel)
    assert issubclass(Visibility, BaseModel)
    assert issubclass(VisibilityResults, BaseModel)
    assert issubclass(LinkBudget, BaseModel)
    assert issubclass(LinkBudgetResults, BaseModel)


def test_1_8_1(c0):
    """The simulator shall provide semi-analytical propagators that consider the gravitational attraction of the
    central body as a point mass and with J2 and J4 coefficients."""

    # First disabling the Earth gravity harmonics so we only have a newtonian attraction
    prop1 = SemiAnalyticalPropagator(state_init=c0, grav_degree_order=None)
    assert len(prop1._orekit_prop.getAllForceModels()) == 1

    # Then enabling the Earth gravity harmonics with degree=4, order=4
    # This makes in total 3 force models because in the Orekit DSST implementation,
    # the zonal and tesseral terms have separate force models
    prop2 = SemiAnalyticalPropagator(state_init=c0, grav_degree_order=(4, 4))
    assert len(prop2._orekit_prop.getAllForceModels()) == 3


def test_1_8_2(iss_tle):
    """The simulator shall provide an SGP4 propagator."""

    propagator = SGP4(tle=iss_tle)
    start_time = propagator.time
    end_time = start_time + TimeDelta.from_hours(6)
    times = start_time.trange(end_time, step=float(TimeDelta.from_minutes(1)))
    trajectory = propagator.propagate(times)
    assert isinstance(trajectory, Trajectory)


def test_1_8_3(c0):
    """The simulator shall provide a numerical propagator with configurable force model based on a higher-order
    ODE solver."""

    # First disabling the Earth gravity harmonics so we only have a newtonian attraction
    num_prop1 = NumericalPropagator(state_init=c0, grav_degree_order=None)
    assert len(num_prop1._orekit_prop.getAllForceModels()) == 1

    # Then enabling the Earth gravity harmonics with degree=16, order=16
    num_prop2 = NumericalPropagator(state_init=c0, grav_degree_order=(16, 16))
    assert len(num_prop2._orekit_prop.getAllForceModels()) == 2


def test_1_8_4(c0):
    """The numerical propagators shall be able to consider the gravitational attraction of the central body as a point
    mass with J2 and J4 coefficients."""
    num_prop = NumericalPropagator(state_init=c0, grav_degree_order=(4, 4))
    assert len(num_prop._orekit_prop.getAllForceModels()) == 2


def test_1_8_5(resources, c0):
    """The numerical propagator can load gravity model coefficients from input files."""

    gravity_file = resources / "potential" / "ICGEM_GOCO06s.gfc"
    _prop = NumericalPropagator(state_init=c0, gravity_file=gravity_file)

    from org.orekit.forces.gravity.potential import GravityFieldFactory  # type: ignore  # noqa: PLC0415

    coeff_reader = GravityFieldFactory.readGravityField(300, 300)
    assert coeff_reader.getMaxAvailableDegree() == 300
    assert coeff_reader.getMaxAvailableOrder() == 300

    # Clear custom gravity file at the end
    GravityFieldFactory.clearPotentialCoefficientsReaders()
    GravityFieldFactory.addDefaultPotentialCoefficientsReaders()


def test_1_8_6(c0):
    """The numerical propagator shall be able to consider atmospheric drag."""
    num_prop = NumericalPropagator(state_init=c0, enable_drag=True)
    # The propagator has always 2 force models enabled by default: newtonian attraction and spherical harmonics of the
    # main attractor
    assert len(num_prop._orekit_prop.getAllForceModels()) == 3


def test_1_8_7(c0):
    """The numerical propagator shall be able to consider solar radiation pressure."""
    num_prop = NumericalPropagator(state_init=c0, enable_srp=True)

    # The propagator has always 2 force models enabled by default: newtonian attraction and spherical harmonics of the
    # main attractor
    assert len(num_prop._orekit_prop.getAllForceModels()) == 3


def test_1_8_8(c0):
    """The numerical propagator shall be able to consider third-body perturbations."""
    third_bodies = [
        Origin(name="sun"),
        Origin(name="luna"),
        Origin(name="mercury"),
        Origin(name="venus"),
        Origin(name="mars"),
        Origin(name="jupiter"),
        Origin(name="saturn"),
        Origin(name="uranus"),
        Origin(name="neptune"),
    ]
    num_prop = NumericalPropagator(state_init=c0, third_bodies=third_bodies)
    # The propagator has always 2 force models enabled by default: newtonian attraction and spherical harmonics of the
    # main attractor
    assert len(num_prop._orekit_prop.getAllForceModels()) == len(third_bodies) + 2


@pytest.mark.skip(reason="events")
def test_1_8_10():
    """The propagators shall be configurable with time-based and event-based stopping conditions."""
    raise AssertionError()


def test_1_9_1(iss_trajectory):
    """The simulator can detect user-defined events during propagation and precalculated trajectories."""

    def apsis_pass(s: Cartesian) -> float:
        return s.position @ s.velocity  # type: ignore

    events = iss_trajectory.find_events(apsis_pass)
    assert len(events) == 2


def test_1_9_2(iss_trajectory):
    """The simulator shall provide predefined events for periapsis and apoapsis passes."""
    detector = ApsisDetector()
    events = detector.detect(iss_trajectory)
    assert len(events) == 2
    detector = ApsisDetector(apsis="periapsis")
    events = detector.detect(iss_trajectory)
    assert len(events) == 1
    assert events[0].crossing == "up"
    assert iss_trajectory.interpolate(events[0].time).to_keplerian().true_anomaly == pytest.approx(0.0, abs=1e-6)
    detector = ApsisDetector(apsis="apoapsis")
    events = detector.detect(iss_trajectory)
    assert len(events) == 1
    assert events[0].crossing == "down"
    assert iss_trajectory.interpolate(events[0].time).to_keplerian().true_anomaly == pytest.approx(np.pi, rel=1e-6)


@pytest.mark.skip(reason="events")
def test_1_9_3():
    """The simulator shall provide predefined events for entering and exiting celestial body shadows."""
    raise AssertionError()


@pytest.mark.skip(reason="events")
def test_1_9_4():
    """The simulator shall provide predefined events for detecting unobstructed lines of sight between two objects."""
    raise AssertionError()


def test_1_9_5(lunar_scenario, lunar_transfer):
    """The simulator shall provide predefined events for an object rising above an elevation threshold for a certain
    location."""
    gs = lunar_scenario["CEBR"]
    detector = ElevationDetector(ground_station=gs.model)
    events = detector.detect(lunar_transfer)
    assert len(events) == 96


@pytest.mark.skip(reason="events")
def test_1_9_6():
    """The simulator shall provide predefined events for entering and exiting a celestial body's sphere of influence."""
    raise AssertionError()


def test_1_10_1():
    """The simulator shall allow the definition of orbits as Cartesian state vectors."""

    time = Time.from_iso("TAI", "2024-07-05T09:09:18.173")
    position = np.array([-5530.01774359, -3487.0895338, -1850.03476185])
    velocity = np.array([1.29534407, -5.02456882, 5.6391936])
    state = Cartesian.from_rv(time, position, velocity)
    assert state.frame == DEFAULT_FRAME
    assert state.origin == DEFAULT_ORIGIN


def test_1_10_2():
    """The simulator shall allow the definition of orbits as osculating Keplerian elements."""

    utc = Time.from_utc("2023-03-25T21:08:00.0")
    time = utc.to_scale("TDB")
    semi_major_axis = 24464.560
    eccentricity = 0.7311
    inclination = 0.122138
    longitude_of_ascending_node = 1.00681
    argument_of_periapsis = 3.10686
    true_anomaly = 0.44369564302687126
    orbit = Keplerian.from_elements(
        time,
        semi_major_axis,
        eccentricity,
        inclination,
        longitude_of_ascending_node,
        argument_of_periapsis,
        true_anomaly,
        angle_unit="radians",
    )
    assert float(orbit.orbital_period) == pytest.approx(38081.76755681076)


def test_1_10_3():
    """The simulator shall allow the definition of Keplerian elements in terms of true anomaly or mean anomaly."""
    utc = Time.from_utc("2023-03-25T21:08:00.0")
    time = utc.to_scale("TDB")
    semi_major_axis = 24464.560
    eccentricity = 0.7311
    inclination = 0.122138
    longitude_of_ascending_node = 1.00681
    argument_of_periapsis = 3.10686
    mean_anomaly = 0.048363
    orbit = Keplerian.from_elements(
        time,
        semi_major_axis,
        eccentricity,
        inclination,
        longitude_of_ascending_node,
        argument_of_periapsis,
        mean_anomaly,
        angle_unit="radians",
        anomaly_type="mean",
    )
    expected = 0.44369564302687126
    assert orbit.true_anomaly == pytest.approx(expected)


def test_1_10_4():
    """The simulator shall allow the definition of Keplerian elements in terms of semi-major axis or altitude or radius
    pairs."""
    utc = Time.from_utc("2023-03-25T21:08:00.0")
    time = utc.to_scale("TDB")
    apoapsis_radius = 42350.599816
    periapsis_radius = 6578.520184000001
    inclination = 0.122138
    longitude_of_ascending_node = 1.00681
    argument_of_periapsis = 3.10686
    mean_anomaly = 0.048363
    orbit = Keplerian.from_radii(
        time,
        apoapsis_radius,
        periapsis_radius,
        inclination,
        longitude_of_ascending_node,
        argument_of_periapsis,
        mean_anomaly,
        angle_unit="radians",
        anomaly_type="mean",
    )
    semi_major_axis = 24464.560
    eccentricity = 0.7311
    assert orbit.semi_major_axis == pytest.approx(semi_major_axis)
    assert orbit.eccentricity == pytest.approx(eccentricity)
    apoapsis_altitude = 35979.59144933333
    periapsis_altitude = 207.51181733333488
    inclination = 0.122138
    longitude_of_ascending_node = 1.00681
    argument_of_periapsis = 3.10686
    mean_anomaly = 0.048363
    orbit = Keplerian.from_altitudes(
        time,
        apoapsis_altitude,
        periapsis_altitude,
        inclination,
        longitude_of_ascending_node,
        argument_of_periapsis,
        mean_anomaly,
        angle_unit="radians",
        anomaly_type="mean",
    )
    assert orbit.semi_major_axis == pytest.approx(semi_major_axis)
    assert orbit.eccentricity == pytest.approx(eccentricity)


def test_1_10_5(lunar_transfer):
    """The simulator shall allow the definition of trajectories as vectors of epochs and associated state vectors."""

    assert len(lunar_transfer.cartesian_states) == 2367
    assert len(lunar_transfer.times) == 2367


def test_1_10_6(lunar_transfer):
    """The simulator shall be able to interpolate intermediate state vectors of trajectories."""

    times = lunar_transfer.times
    t0 = times[0]
    t1 = times[-1]
    dt = float(t1 - t0) / 2
    ti = t0 + TimeDelta(dt)
    state = lunar_transfer.interpolate(ti)
    assert isinstance(state, Cartesian)


def test_1_10_7(iss_trajectory):
    """The simulator shall be able to change the central body and/or reference frame of an orbit definition or
    trajectory and automatically transform the coordinates."""
    r_venus = np.array(
        [
            1.001977553295792e8,
            2.200234656010247e8,
            9.391473630346918e7,
        ]
    )
    v_venus = np.array([-59.08617935009049, 22.682387107225292, 12.05029567478702])
    r = np.array([6068279.27, -1692843.94, -2516619.18]) / 1e3

    v = np.array([-660.415582, 5495.938726, -5303.093233]) / 1e3

    r_exp = r - r_venus
    v_exp = v - v_venus
    tai = Time.from_utc("2016-05-30T12:00:00.000")

    venus = Origin(name="Venus")
    earth = Origin(name="Earth")

    icrf = ReferenceFrame(abbreviation="ICRF")
    iau_venus = ReferenceFrame(abbreviation="IAU_VENUS")

    s_earth = Cartesian.from_rv(tai, r, v)
    s_venus = s_earth.to_origin(venus)

    r_act = s_venus.position
    v_act = s_venus.velocity

    npt.assert_allclose(r_act, r_exp)
    npt.assert_allclose(v_act, v_exp)

    start_exp = iss_trajectory.cartesian_states[0]
    end_exp = iss_trajectory.cartesian_states[-1]

    tra = iss_trajectory.to_origin(venus).to_origin(earth)
    start_act = tra.cartesian_states[0]
    end_act = tra.cartesian_states[-1]

    assert start_act.isclose(start_exp)
    assert end_act.isclose(end_exp)

    tra = iss_trajectory.to_frame(iau_venus).to_frame(icrf)
    start_act = tra.cartesian_states[0]
    end_act = tra.cartesian_states[-1]

    assert start_act.isclose(start_exp)
    assert end_act.isclose(end_exp)


def test_1_11_1():
    """The simulator shall provide physical constants for all celestial bodies defined by the IAU WGCCRE reports."""

    # We are using a body from each category as a smoke test
    assert Origin(name="Sun").gravitational_parameter == pytest.approx(1.32712440018e11)
    assert Origin(name="Earth").gravitational_parameter == pytest.approx(3.986004418e5)
    assert Origin(name="Moon").gravitational_parameter == pytest.approx(4.902800066e3)
    assert Origin(name="Ceres").gravitational_parameter == pytest.approx(6.262888864440993e1)


def test_1_12_1(lunar_transfer):
    """The simulator can generate ground track plots for trajectories."""

    gt = GroundTrack(lunar_transfer)
    assert isinstance(gt, GroundTrack)


def test_1_12_2(iss_tle):
    """The simulator can generate 3D plots for one or more trajectories."""

    propagator = SGP4(tle=iss_tle)
    start_time = propagator.time
    end_time = start_time + TimeDelta.from_hours(6)
    times = start_time.trange(end_time, step=float(TimeDelta.from_minutes(1)))
    trajectory = propagator.propagate(times)
    scatter3d = trajectory.plot_3d()
    assert isinstance(scatter3d, go.Scatter3d)


def test_1_12_3(phasma_sc, aoi_geom_dict):
    """The simulator shall be able to plot areas of coverage."""
    feature_list = polygonize_aoi(aoi_geom_dict=aoi_geom_dict, res=1)
    results = coverage_analysis(
        sc=phasma_sc, start_time=phasma_sc.model.propagator.time, duration_hours=1.0, areas_of_interest=feature_list
    )

    # Matplotlib backend
    ax = results.plot_mpl(legend=True, cmap="viridis")  # All keyword arguments are passed to matplotlib
    assert isinstance(ax, Axes)

    # Plotly backend
    fig = results.plot_plotly(
        map_style="open-street-map", zoom=0, opacity=0.6, color_continuous_scale="Viridis"
    )  # All keyword arguments are passed to plotly
    assert isinstance(fig, Figure)


def test_1_12_4(c0):
    """The simulator shall be able to plot 3D visibility cones."""
    antenna = ComplexAntenna(pattern=ParabolicPattern(diameter=3.0, efficiency=0.6))
    assert isinstance(antenna.viz_cone_3d(frequency=Frequency.gigahertz(8.4), sc_state=c0), go.Surface)


def test_1_13_1(lunar_scenario):
    """Scenarios shall require a start and stop epoch."""
    assert isinstance(lunar_scenario.start_time, Time)
    assert isinstance(lunar_scenario.end_time, Time)


@pytest.mark.skip(reason="mission phases")
def test_1_13_2():
    """Scenarios shall require a global default propagator."""
    raise AssertionError()


def test_1_13_3(lunar_scenario):
    """Scenarios shall require a global default central body."""
    assert hasattr(lunar_scenario, "origin")


def test_1_13_4(lunar_scenario):
    """Scenarios shall require a global default propagation frame."""
    assert hasattr(lunar_scenario, "frame")


@pytest.mark.skip(reason="mission phases")
def test_1_13_5():
    """It shall be possible to define initial and intermediate orbits for all assets within a scenario."""
    raise AssertionError()


@pytest.mark.skip(reason="mission phases")
def test_1_13_6():
    """It shall be possible to modify the state vector of intermediate orbits with impulsive manoeuvres."""
    raise AssertionError()


@pytest.mark.skip(reason="mission phases")
def test_1_13_7():
    """It shall be possible to change propagators and propagation parameters between orbits."""
    raise AssertionError()


def test_1_13_8(lunar_scenario):
    """It shall be possible to define satellite assets within scenarios."""

    assert isinstance(lunar_scenario["Lunar Transfer"].model, Spacecraft)


def test_1_13_9(lunar_scenario):
    """It shall be possible to define ground assets within scenarios."""

    assert isinstance(lunar_scenario["CEBR"].model, GroundStation)


def test_1_13_10(phasma_scenario):
    """It shall be possible to define payloads within scenarios."""

    assert isinstance(phasma_scenario["PHASMA"].comms[0], CommunicationSystem)


def test_1_13_11():
    """It shall be possible to define elevation masks for ground assets."""
    gs = GroundStation.from_lla(
        0,
        0,
        minimum_elevation=(
            [Angle.from_degrees(-180), Angle.from_degrees(0), Angle.from_degrees(180)],
            [Angle.from_degrees(0), Angle.from_degrees(5), Angle.from_degrees(0)],
        ),
    )
    assert np.degrees(gs.get_minimum_elevation(np.pi / 2)) == pytest.approx(2.5)


def test_1_13_12(lunar_scenario):
    """It shall be possible to define areas or points of interest within scenarios."""
    assert hasattr(lunar_scenario, "areas_of_interest")
    assert hasattr(lunar_scenario, "points_of_interest")


def test_1_13_13():
    """It shall be possible to link payloads to assets within scenarios."""
    model = GroundStation.from_lla(longitude=-4.3676, latitude=40.4527)
    asset = Asset(model=model)
    assert hasattr(asset, "comms")


@pytest.mark.skip(reason="GUI")
def test_1_14_1():
    """The simulator shall provide a GUI that supports the configuration of assets."""
    raise AssertionError()


@pytest.mark.skip(reason="GUI")
def test_1_14_2():
    """The simulator shall provide a GUI that supports the configuration of analyses."""
    raise AssertionError()


@pytest.mark.skip(reason="GUI")
def test_1_14_3():
    """The simulator shall provide a GUI that supports the visualisation of propagation, optimisation, and analysis
    results."""
    raise AssertionError()


def test_1_15_1():
    """Communications payload objects shall consist of antenna, transmitter, and receiver models."""

    frequency = Frequency.megahertz(2308)
    antenna = SimpleAntenna(gain_db=6.5, beamwidth_deg=60, design_frequency=frequency)
    transmitter = Transmitter(power=1.348, frequency=Frequency.megahertz(2308), line_loss=1.0)
    receiver = SimpleReceiver(system_noise_temperature=429, frequency=Frequency.megahertz(2308))
    system = CommunicationSystem(
        channels=[],
        transmitter=transmitter,
        receiver=receiver,
        antenna=antenna,
    )
    assert hasattr(system, "antenna")
    assert hasattr(system, "transmitter")
    assert hasattr(system, "receiver")


def test_1_15_2():
    """The simulator shall model simple antennas defined by conic angles and pointing mode."""
    frequency = Frequency.megahertz(2308)
    sc_antenna = SimpleAntenna(gain_db=6.5, beamwidth_deg=60, design_frequency=frequency)
    assert hasattr(sc_antenna, "gain_db")
    assert hasattr(sc_antenna, "beamwidth_deg")


def test_1_15_3():
    """The simulator shall model complex antennas defined by radiation pattern, pointing mode, centre frequency, gain,
    efficiency, and gain-to-noise temperature (G/T)."""
    parabolic_antenna = ComplexAntenna(pattern=ParabolicPattern(diameter=3.0, efficiency=0.6))
    assert hasattr(parabolic_antenna, "pattern")
    assert hasattr(parabolic_antenna, "design_frequency")
    assert hasattr(parabolic_antenna, "gain")


def test_1_15_4():
    """The simulator shall model parabolic antennas radiation patterns."""
    pattern = ParabolicPattern(diameter=3.0, efficiency=0.6)
    assert isinstance(pattern, ParabolicPattern)


@pytest.mark.skip(reason="patterns")
def test_1_15_5():
    """The simulator shall model helix antennas radiation patterns."""
    raise AssertionError()


def test_1_15_6():
    """The simulator shall model dipole antennas radiation patterns."""

    frequency = 433e6
    pattern = DipolePattern(length=wavelength(frequency=frequency) / 2)
    assert isinstance(pattern, DipolePattern)


@pytest.mark.skip(reason="patterns")
def test_1_15_7():
    """The simulator shall model phased array antennas radiation patterns."""
    raise AssertionError()


def test_1_15_8(resources):
    """The simulator shall support custom file-based antenna radiation patterns."""
    msi_file = resources / "antennas" / "cylindricalDipole.pln"
    msi = MSIPattern.read_file(msi_file)
    freq = Frequency.megahertz(70)
    dipole = DipolePattern(length=2.0)
    ang = np.radians(12.4)
    dipole_gain = dipole.gain(freq, ang)
    msi_gain = msi.gain(freq, ang)
    assert msi_gain == pytest.approx(dipole_gain, rel=1)


def test_1_15_9():
    """The simulator shall model nadir antenna pointing for simple antennas."""
    antenna = SimpleAntenna(gain_db=6.5, beamwidth_deg=60)
    assert hasattr(antenna, "boresight_vector")


def test_1_15_10():
    """The simulator shall model zenith antenna pointing for simple antennas."""
    antenna = SimpleAntenna(gain_db=6.5, beamwidth_deg=60)
    assert hasattr(antenna, "boresight_vector")


def test_1_15_11():
    """The simulator shall model targeted antenna pointing for simple antennas."""
    antenna = SimpleAntenna(gain_db=6.5, beamwidth_deg=60)
    assert hasattr(antenna, "boresight_vector")


def test_1_15_12():
    """The simulator shall model nadir antenna pointing for complex antennas."""
    antenna = ComplexAntenna(pattern=ParabolicPattern(diameter=3.0, efficiency=0.6))
    assert hasattr(antenna, "boresight_vector")


def test_1_15_13():
    """The simulator shall model zenith antenna pointing for complex antennas."""
    antenna = ComplexAntenna(pattern=ParabolicPattern(diameter=3.0, efficiency=0.6))
    assert hasattr(antenna, "boresight_vector")


def test_1_15_14():
    """The simulator shall model targeted antenna pointing for complex antennas."""
    antenna = ComplexAntenna(pattern=ParabolicPattern(diameter=3.0, efficiency=0.6))
    assert hasattr(antenna, "boresight_vector")


@pytest.mark.filterwarnings(
    "ignore:The collections attribute was deprecated in Matplotlib 3.8 and will be removed in 3.10."
)
def test_1_15_15(c0):
    """The simulator shall be able to plot beam contours for any antenna object in both 2D and 3D representations.
    TODO: as of now, only 2D contour plots are supported because of the limitation of existing Python plotting tools;
        Implement 3D too
    """
    antenna = ComplexAntenna(pattern=ParabolicPattern(diameter=3.0, efficiency=0.6))
    geomap = antenna.plot_contour_2d(frequency=Frequency.gigahertz(31), sc_state=c0)
    assert isinstance(geomap, folium.Map)


def test_1_15_16(lunar_scenario):
    """The simulator shall require only the necessary parameters for conducting geometrical analyses
    (visibility and access) without the necessity to specify all parameters of the communications payload."""
    visibility = Visibility(scenario=lunar_scenario)
    results = visibility.analyze()
    for asset in lunar_scenario.assets:
        # Verify that the assets do not have any comms payloads defined
        assert not asset.comms
    assert isinstance(results, VisibilityResults)


def test_1_15_17():
    """Transmitters shall be defined by central frequency, transmitter gain, and transmitter losses."""

    transmitter = Transmitter(power=4, frequency=Frequency.megahertz(2308), line_loss=1.0)
    assert hasattr(transmitter, "power")
    assert hasattr(transmitter, "frequency")
    assert hasattr(transmitter, "line_loss")


def test_1_15_18():
    """Receivers shall be defined by central frequency, low-noise amplifier (LNA) gain, LNA noise,
    and receiver losses."""

    receiver = ComplexReceiver(
        lna_gain=4, lna_noise_figure=1, noise_figure=1, loss=1, frequency=Frequency.megahertz(2308)
    )
    assert hasattr(receiver, "lna_gain")
    assert hasattr(receiver, "lna_noise_figure")
    assert hasattr(receiver, "noise_figure")
    assert hasattr(receiver, "loss")
    assert hasattr(receiver, "frequency")


def test_1_15_19():
    """Payloads shall be connected via communication chains that are modelled as communications channel objects."""

    frequency = Frequency.megahertz(2308)
    antenna = SimpleAntenna(gain_db=6.5, beamwidth_deg=60, design_frequency=frequency)
    transmitter = Transmitter(power=1.348, frequency=Frequency.megahertz(2308), line_loss=1.0)
    receiver = SimpleReceiver(system_noise_temperature=429, frequency=Frequency.megahertz(2308))
    system = CommunicationSystem(
        channels=[],
        transmitter=transmitter,
        receiver=receiver,
        antenna=antenna,
    )
    assert hasattr(system, "channels")


def test_1_15_20():
    """Communications channels shall be defined by data rate, required figure of merit (Eb/N0 or C/N0),
    modulation scheme, roll-off factor, forward error correction, and margins."""
    channel = Channel(link_type="uplink", modulation="BPSK", data_rate=430502, required_eb_n0=2.3, margin=3)
    assert hasattr(channel, "modulation")
    assert hasattr(channel, "data_rate")
    assert hasattr(channel, "required_eb_n0")
    assert hasattr(channel, "margin")
    assert hasattr(channel, "roll_off")
    assert hasattr(channel, "forward_error_correction")


def test_1_16_1():
    """The simulator shall be able to create Walker Star constellations."""
    start_time = Time.from_iso("TDB", "2016-05-30T12:00:00")
    duration_hours = 2.0

    nsats = 16
    ws = WalkerStar(
        time=start_time,
        nsats=nsats,
        nplanes=8,
        semi_major_axis=7000,
        inclination=45,
        eccentricity=0.01,
        periapsis_argument=90,
    )

    scenario = Scenario(
        name="Constellation",
        start_time=start_time,
        end_time=start_time + TimeDelta.from_hours(duration_hours),
        constellations=[Constellation(model=ws)],
    )

    assert len(scenario.assets) == 0
    assert len(scenario.all_assets) == nsats


def test_1_16_2():
    """The simulator shall be able to create Walker Delta constellations."""
    start_time = Time.from_iso("TDB", "2016-05-30T12:00:00")
    duration_hours = 2.0

    nsats = 56
    wd = WalkerDelta(
        time=start_time,
        nsats=nsats,
        nplanes=8,
        semi_major_axis=7000,
        inclination=45,
        eccentricity=0.01,
        periapsis_argument=90,
    )

    scenario = Scenario(
        name="Constellation",
        start_time=start_time,
        end_time=start_time + TimeDelta.from_hours(duration_hours),
        constellations=[Constellation(model=wd)],
    )

    assert len(scenario.assets) == 0
    assert len(scenario.all_assets) == nsats


def test_1_16_3():
    """The simulator shall be able to create Flower constellations."""
    start_time = Time.from_iso("TDB", "2016-05-30T12:00:00")
    duration_hours = 2.0

    nsats = 49

    flower = Flower(
        time=start_time,
        inclination=0.0,
        periapsis_argument=0.0,
        perigee_altitude=19702.0,
        nsats=nsats,
        n_petals=15,
        n_days=7,
        phasing_n=23,
        phasing_d=49,
    )

    scenario = Scenario(
        name="Constellation",
        start_time=start_time,
        end_time=start_time + TimeDelta.from_hours(duration_hours),
        constellations=[Constellation(model=flower)],
    )

    assert len(scenario.assets) == 0
    assert len(scenario.all_assets) == nsats


def test_1_16_4():
    """The simulator shall be able to create Street of Coverage constellations."""
    start_time = Time.from_iso("TDB", "2016-05-30T12:00:00")
    duration_hours = 2.0

    nsats = 66

    soc = StreetOfCoverage(
        time=start_time,
        nsats=nsats,
        nplanes=6,
        semi_major_axis=7158,
        inclination=86.4,
        eccentricity=0.00001,
        periapsis_argument=90,
        coverage_fold=1,
    )

    scenario = Scenario(
        name="Constellation",
        start_time=start_time,
        end_time=start_time + TimeDelta.from_hours(duration_hours),
        constellations=[Constellation(model=soc)],
    )

    assert len(scenario.assets) == 0
    assert len(scenario.all_assets) == nsats


def test_1_17_1(lunar_scenario, lunar_visibility):
    """The simulator shall be able to compute visiblity windows (accesses) for all asset pairings."""
    sc = lunar_scenario["Lunar Transfer"]
    assert len(lunar_visibility.passes[sc.asset_id]) + 1 == len(lunar_scenario.assets)


@pytest.mark.skip()
def test_1_17_2(lunar_scenario, lunar_visibility):
    """Visibility results shall include observer and target, start and stop epochs and duration of individual windows
    as well as the total duration of all windows."""
    sc = lunar_scenario["Lunar Transfer"]
    gs = lunar_scenario["CEBR"]
    # assert lunar_visibility.total_duration(gs, sc) == pytest.approx(1171408.1592220461)
    first_pass = lunar_visibility[gs, sc][0]
    start = Time.from_utc("2022-02-01T00:00:00.000")
    stop = Time.from_utc("2022-02-01T09:53:13.472")
    assert first_pass.window.start.isclose(start)
    assert first_pass.window.stop.isclose(stop)


def test_1_17_3(lunar_scenario, lunar_visibility):
    """Visibility results shall include azimuth, elevation, and range for all windows."""
    sc = lunar_scenario["Lunar Transfer"]
    gs = lunar_scenario["CEBR"]
    first_pass = lunar_visibility[gs, sc][0]
    assert hasattr(first_pass, "observables")


def coverage_analysis(
    sc: Spacecraft, start_time: Time, duration_hours: float, areas_of_interest: list[Feature[Polygon, dict]]
) -> CoverageResults:
    scenario = Scenario(
        assets=[sc],
        name="Coverage analysis",
        start_time=start_time,
        end_time=start_time + TimeDelta.from_hours(duration_hours),
        areas_of_interest=areas_of_interest,
        auto_discretize=False,  # Areas are already discretized by the test
    )
    cov = Coverage(scenario=scenario)
    return cov.analyze()


def test_1_18_1_polygons(resources, phasma_sc):
    """The simulator shall be able to compute the coverage of a target area on a celestial body which shall be defined
    by polygons or a grid for a given time window."""
    feature_list = load_geojson_multipolygon(resources / "coverage" / "simple_polygons.geojson")
    results = coverage_analysis(
        sc=phasma_sc, start_time=phasma_sc.model.propagator.time, duration_hours=1.0, areas_of_interest=feature_list
    )
    assert len(results.to_geodataframe()) == len(feature_list)


def test_1_18_1_hexagonal_grid(phasma_sc, aoi_geom_dict):
    """The simulator shall be able to compute the coverage of a target area on a celestial body which shall be defined
    by polygons or a grid for a given time window."""
    feature_list = polygonize_aoi(aoi_geom_dict=aoi_geom_dict, res=1)
    results = coverage_analysis(
        sc=phasma_sc, start_time=phasma_sc.model.propagator.time, duration_hours=1.0, areas_of_interest=feature_list
    )
    assert len(results.to_geodataframe()) == len(feature_list)


def test_1_18_1_rectangular_grid(phasma_sc, aoi_geom_dict):
    """The simulator shall be able to compute the coverage of a target area on a celestial body which shall be defined
    by polygons or a grid for a given time window."""
    feature_list = polygonize_aoi_rectangles(aoi_geom_dict=aoi_geom_dict, vertex_degrees=1)
    results = coverage_analysis(
        sc=phasma_sc, start_time=phasma_sc.model.propagator.time, duration_hours=1.0, areas_of_interest=feature_list
    )
    assert len(results.to_geodataframe()) == len(feature_list)


def test_1_18_2(phasma_sc, aoi_geom_dict):
    """Coverage results shall include the percentage of time that the target area is covered for the given
    time window."""
    feature_list = polygonize_aoi(aoi_geom_dict=aoi_geom_dict, res=1)
    results = coverage_analysis(
        sc=phasma_sc, start_time=phasma_sc.model.propagator.time, duration_hours=1.0, areas_of_interest=feature_list
    )
    gdf = results.to_geodataframe()
    assert "coverage_percent" in gdf
    assert gdf["coverage_percent"].min() == 0.0
    assert gdf["coverage_percent"].max() <= 1.0


def test_1_18_3(phasma_sc, aoi_geom_dict):
    """The simulator shall support plotting the coverage results with customisable colours and contours."""
    feature_list = polygonize_aoi(aoi_geom_dict=aoi_geom_dict, res=1)
    results = coverage_analysis(
        sc=phasma_sc, start_time=phasma_sc.model.propagator.time, duration_hours=1.0, areas_of_interest=feature_list
    )

    # Matplotlib backend
    ax = results.plot_mpl(legend=True, cmap="viridis")  # All keyword arguments are passed to matplotlib
    assert isinstance(ax, Axes)

    # Plotly backend
    fig = results.plot_plotly(
        map_style="open-street-map", zoom=0, opacity=0.6, color_continuous_scale="Viridis"
    )  # All keyword arguments are passed to plotly
    assert isinstance(fig, Figure)


def test_1_19_1(phasma_link_budget):
    """The simulator shall be able to compute link budgets for all visibility windows (accesses) between all assets in
    a given time window."""
    assert isinstance(phasma_link_budget, LinkBudgetResults)


def test_1_19_2(phasma_scenario, phasma_link_budget):
    """Link budget results shall include free space path losses, effective isotropic radiated power (EIRP), G/T, figure
    of merit (Eb/N0 or C/N0), data rates, channel bandwidth, margins, and additional losses."""
    sc = phasma_scenario["PHASMA"]
    gs = phasma_scenario["Station 1"]
    link = phasma_link_budget[gs, sc][0]
    assert isinstance(link, Link)
    stats = link.stats[0]
    assert hasattr(stats, "fspl")
    assert hasattr(stats, "eirp")
    assert hasattr(stats, "gt")
    assert hasattr(stats, "c_n0")
    assert hasattr(stats, "eb_n0")
    assert hasattr(stats, "margin")
    assert hasattr(stats, "losses")
    assert hasattr(stats, "data_rate")
    assert hasattr(stats, "bandwidth")


def test_1_19_3(sc_transmitter, phasma_scenario, phasma_link_budget):
    """Link budget results should include additional losses broken down into output back off (power amplifier), antenna
    pointing loss, depolarization loss, demodulator loss, Solar scintillation effect, implementation losses, ionospheric
    loss, atmospheric loss."""

    assert hasattr(sc_transmitter, "output_back_off")

    rx = ComplexReceiver(
        frequency=Frequency.gigahertz(20), lna_gain=20, lna_noise_figure=4, noise_figure=5, loss=3, demodulator_loss=1.0
    )
    assert hasattr(rx, "demodulator_loss")
    assert hasattr(rx, "implementation_loss")

    sc = phasma_scenario["PHASMA"]
    gs = phasma_scenario["Station 1"]
    link = phasma_link_budget[gs, sc][0]
    stats = link.stats[0]

    assert hasattr(stats, "losses")
    assert isinstance(stats.losses, EnvironmentalLosses)
    assert hasattr(stats.losses, "rain_attenuation")
    assert hasattr(stats.losses, "gaseous_attenuation")
    assert hasattr(stats.losses, "scintillation_attenuation")
    assert hasattr(stats.losses, "atmospheric_attenuation")
    assert hasattr(stats.losses, "cloud_attenuation")
    assert hasattr(stats.losses, "depolarization_loss")


def test_1_19_4(phasma_scenario, phasma_link_budget):
    """Link budget results shall be plottable."""
    sc = phasma_scenario["PHASMA"]
    gs = phasma_scenario["Station 1"]
    link = phasma_link_budget[gs, sc][0]
    assert hasattr(link, "plot")


def test_1_20_1(phasma_sc, aoi_geom_dict):
    """The simulator shall be able to compute time gap analysis and revisit times."""
    feature_list = polygonize_aoi(aoi_geom_dict=aoi_geom_dict, res=1)
    results = coverage_analysis(
        sc=phasma_sc, start_time=phasma_sc.model.propagator.time, duration_hours=1.0, areas_of_interest=feature_list
    )

    results_df = results.to_geodataframe()
    assert "max_time_gaps" in results_df
    assert "revisit_count" in results_df
    assert "total_revisit_duration_hours" in results_df

    fig = results.plot_plotly(data_to_plot="max_time_gaps")
    assert isinstance(fig, Figure)


def test_1_21_1():
    """All inputs and outputs of the simulator shall be provided in machine-readable and serialisable formats to allow
    integration with external optimisation tools."""
    assert issubclass(Scenario, BaseModel)
    assert issubclass(Visibility, BaseModel)
    assert issubclass(VisibilityResults, BaseModel)
    assert issubclass(LinkBudget, BaseModel)
    assert issubclass(LinkBudgetResults, BaseModel)


def test_1_22_1(phasma_scenario):
    """The simulator shall be able to perform a preliminary assessment of interference analysis for uplink
    and downlink."""
    """
    Based on the PHASMA scenario, and additional clones the spacecraft to generate downlink interference.
    Uplink interference is also expected, as the PHASMA scenario contains several ground stations closely located
    """
    phasma_sc_cloned = phasma_scenario["PHASMA"].model.model_copy()
    # Generate a unique UUID5 for the clone using the asset namespace
    clone_uuid = uuid.uuid5(ASSET_NAMESPACE, "PHASMA_clone")
    phasma_sc_cloned_asset = Asset(
        asset_id=clone_uuid,
        model=phasma_sc_cloned,
        name="PHASMA_clone",
        comms=phasma_scenario["PHASMA"].comms,
    )

    # Create a new scenario with the cloned asset included
    phasma_scenario = phasma_scenario.model_copy(update={"assets": [*phasma_scenario.assets, phasma_sc_cloned_asset]})

    # Clear the cached all_assets property to ensure it includes the new asset
    # The cached_property stores its value with the attribute name, not with underscore
    if "all_assets" in phasma_scenario.__dict__:
        del phasma_scenario.__dict__["all_assets"]

    lb_with_interf = LinkBudget(scenario=phasma_scenario, with_interference=True).analyze()
    valid_uplink_with_interf_df = None
    valid_downlink_with_interf_df = None
    for _target_id, target_passes in lb_with_interf.links.items():
        for _observer_id, links in target_passes.items():
            for link in links:
                for link_stat in link.stats:
                    if (
                        link_stat.interference_stats
                        and link_stat.interference_stats.interference_power_w > 0
                        and link.link_type == "uplink"
                    ):
                        valid_uplink_with_interf_df = link.to_dataframe()
                        break

                    if (
                        link_stat.interference_stats
                        and link_stat.interference_stats.interference_power_w > 0
                        and link.link_type == "downlink"
                    ):
                        valid_downlink_with_interf_df = link.to_dataframe()
                        break

    assert valid_uplink_with_interf_df is not None
    assert valid_uplink_with_interf_df["interference_power_w"].max() > 0
    assert (
        valid_uplink_with_interf_df["c_n0i0"] - valid_uplink_with_interf_df["c_n0"]
    ).min() < 0  # Interference degrades the C/N0
    assert (
        valid_uplink_with_interf_df["eb_n0i0"] - valid_uplink_with_interf_df["eb_n0"]
    ).min() < 0  # Interference degrades the Eb/N0
    assert (
        valid_uplink_with_interf_df["margin_with_interference"] - valid_uplink_with_interf_df["margin"]
    ).min() < 0  # Interference degrades the link margin

    assert valid_downlink_with_interf_df is not None
    assert valid_downlink_with_interf_df["interference_power_w"].max() > 0
    assert (
        valid_downlink_with_interf_df["c_n0i0"] - valid_downlink_with_interf_df["c_n0"]
    ).min() < 0  # Interference degrades the C/N0
    assert (
        valid_downlink_with_interf_df["eb_n0i0"] - valid_downlink_with_interf_df["eb_n0"]
    ).min() < 0  # Interference degrades the Eb/N0
    assert (
        valid_downlink_with_interf_df["margin_with_interference"] - valid_downlink_with_interf_df["margin"]
    ).min() < 0  # Interference degrades the link margin


def test_1_23_1(nav_scenario):
    """The simulator shall be able to compute for a given satellite network as seen by one or multiple ground assets,
    the following Navigation Performance Figures of Merit:
    - Dilution of Precision (e.g. GDOP, HDOP, etc.)
    - Navigation Accuracy (e.g. HACC, PACC, etc.) (optional)
    - Number of visible satellites.
    - Availability of position fix. (optional)
    - Availability of position accuracy. (optional)
    - Availability of N satellites.
    - Depth of coverage."""

    observer = nav_scenario["ESOC"]
    nav = Navigation(scenario=nav_scenario).analyze()
    assert observer.asset_id in nav.dop
