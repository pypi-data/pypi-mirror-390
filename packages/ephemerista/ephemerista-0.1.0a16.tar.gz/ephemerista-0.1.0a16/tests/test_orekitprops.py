import numpy as np
import pytest
from pytest import approx

from ephemerista.angles import Angle
from ephemerista.bodies import Origin
from ephemerista.coords.anomalies import TrueAnomaly
from ephemerista.coords.shapes import RadiiShape
from ephemerista.coords.twobody import Inclination, Keplerian
from ephemerista.propagators.events import StoppingEvent
from ephemerista.propagators.orekit.numerical import NumericalPropagator
from ephemerista.propagators.orekit.semianalytical import SemiAnalyticalPropagator
from ephemerista.time import Time, TimeDelta

OREKIT_PROP_CLASSES = [NumericalPropagator, SemiAnalyticalPropagator]


def n_force_models_min(prop):
    if isinstance(prop, NumericalPropagator):
        # The NumericPropagator has always minimum 2 force models: newtonian attraction and spherical harmonics of the
        # main attractor
        return 2
    elif isinstance(prop, SemiAnalyticalPropagator):
        # The SemiAnalyticalPropagator has minimum 3 force models because the zonal and tesseral force terms are
        # separated
        return 3
    else:
        return None


@pytest.mark.parametrize("orekit_prop", OREKIT_PROP_CLASSES)
def test_propagate_same_time(orekit_prop, c0):
    prop = orekit_prop(state_init=c0)

    c1 = prop.propagate(time=c0.time)

    assert c1.x == approx(c0.x)
    assert c1.y == approx(c0.y)
    assert c1.z == approx(c0.z)
    assert c1.vx == approx(c0.vx)
    assert c1.vy == approx(c0.vy)
    assert c1.vz == approx(c0.vz)


@pytest.mark.parametrize("orekit_prop", OREKIT_PROP_CLASSES)
def test_propagate_single_time(orekit_prop, c0):
    time_end = Time.from_iso("TDB", "2016-05-30T12:00:01")

    v_norm = np.linalg.norm(c0.velocity)

    prop = orekit_prop(state_init=c0)

    c2 = prop.propagate(time=time_end)
    delta_pos = c2.position - c0.position

    delta_t: TimeDelta = time_end - c0.time
    assert np.linalg.norm(delta_pos) == approx(v_norm * delta_t.to_decimal_seconds(), abs=1e-2)  # 10 meters tolerance


@pytest.mark.parametrize("orekit_prop", OREKIT_PROP_CLASSES)
def test_propagate_single_time_and_back(orekit_prop, c0):
    time_end = Time.from_iso("TDB", "2016-05-30T12:00:01")

    prop = orekit_prop(state_init=c0)

    prop.propagate(time=time_end)
    c3 = prop.propagate(time=c0.time)
    delta_pos = c3.position - c0.position
    delta_vel = c3.velocity - c0.velocity

    assert np.linalg.norm(delta_pos) == approx(0.0, abs=1e-6)
    assert np.linalg.norm(delta_vel) == approx(0.0, abs=1e-6)


@pytest.mark.parametrize("orekit_prop", OREKIT_PROP_CLASSES)
def test_propagate_multiple_times(orekit_prop, c0):
    time_list = [
        c0.time,
        Time.from_iso("TDB", "2016-05-30T12:00:01"),
        Time.from_iso("TDB", "2016-05-30T12:00:02"),
        Time.from_iso("TDB", "2016-05-30T12:00:05"),
    ]

    v_norm = np.linalg.norm(c0.velocity)

    prop = orekit_prop(state_init=c0)
    traj = prop.propagate(time=time_list)

    assert len(traj.cartesian_states) == len(time_list)

    for i in range(0, len(time_list)):
        c2 = traj.cartesian_states[i]
        time_tai = time_list[i]
        assert c2.time.isclose(time_tai, atol=1e-9)

        delta_pos = c2.position - c0.position
        delta_t: TimeDelta = time_tai - c0.time
        assert np.linalg.norm(delta_pos) == approx(
            v_norm * delta_t.to_decimal_seconds(), abs=1e-2
        )  # 10 meters tolerance


@pytest.mark.parametrize("orekit_prop", OREKIT_PROP_CLASSES)
def test_no_degree_order(orekit_prop, c0):
    prop = orekit_prop(state_init=c0, grav_degree_order=None)

    force_model_list = prop._orekit_prop.getAllForceModels()
    # In this case, we disable the Earth gravity harmonics so we only have a newtonian attraction
    assert len(force_model_list) == 1


@pytest.mark.parametrize("orekit_prop", OREKIT_PROP_CLASSES)
def test_all_valid_third_bodies(orekit_prop, c0):
    time_end = Time.from_iso("TDB", "2016-05-30T12:00:01")

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
    prop = orekit_prop(state_init=c0, third_bodies=third_bodies)

    prop.propagate(time=time_end)

    force_model_list = prop._orekit_prop.getAllForceModels()
    assert len(force_model_list) == n_force_models_min(prop) + len(third_bodies)


@pytest.mark.parametrize("orekit_prop", OREKIT_PROP_CLASSES)
def test_invalid_third_bodies(orekit_prop, c0):
    # We try to define a third body attractor not supported by Orekit
    third_bodies = [Origin(name="ceres")]
    with pytest.raises(ValueError):
        _prop = orekit_prop(state_init=c0, third_bodies=third_bodies)


@pytest.mark.parametrize("orekit_prop", OREKIT_PROP_CLASSES)
def test_srp(orekit_prop, c0):
    prop = orekit_prop(state_init=c0, enable_srp=True)

    force_model_list = prop._orekit_prop.getAllForceModels()
    assert len(force_model_list) == n_force_models_min(prop) + 1


@pytest.mark.parametrize("orekit_prop", OREKIT_PROP_CLASSES)
def test_drag(orekit_prop, c0):
    prop = orekit_prop(state_init=c0, enable_drag=True)

    force_model_list = prop._orekit_prop.getAllForceModels()
    assert len(force_model_list) == n_force_models_min(prop) + 1


@pytest.mark.parametrize("orekit_prop", OREKIT_PROP_CLASSES)
@pytest.mark.parametrize("peri_or_apoapsis", [StoppingEvent.APOAPSIS, StoppingEvent.PERIAPSIS])
def test_apside_stop(orekit_prop, peri_or_apoapsis: StoppingEvent):
    apoapsis_radius = 7000.0  # km
    periapsis_radius = 6900.0  # km

    time_start = Time.from_iso("TDB", "2016-05-30T12:00:00")
    time_end = Time.from_iso("TDB", "2016-05-30T14:00:00")
    t_step = 1.0  # s
    time_list = time_start.trange(time_end, t_step)

    state_init = Keplerian(
        time=time_start,
        shape=RadiiShape(ra=apoapsis_radius, rp=periapsis_radius),
        inc=Inclination(degrees=98.0),
        node=Angle(degrees=0.0),
        arg=Angle(degrees=0.0),
        anomaly=TrueAnomaly(degrees=90.0),  # starting somewhere in between apoapsis and periapsis
    )

    # For this test, we want a Keplerian behaviour so we disable all perturbation forces
    prop = orekit_prop(state_init=state_init, grav_degree_order=None)

    assert (
        len(prop._orekit_prop.getEventDetectors()) == 0
    )  # The Orekit EventDetector is added upon calling the propagate method

    traj = prop.propagate(time=time_list, stop_conds=[peri_or_apoapsis])

    assert (
        len(prop._orekit_prop.getEventDetectors()) == 1
    )  # The Orekit EventDetector is added upon calling the propagate method
    assert len(traj.cartesian_states) < len(time_list)  # the propagation stops before time_end

    state_last = traj.cartesian_states[-1]
    assert (time_end - state_last.time).to_decimal_seconds() > 0  # the propagation stops before time_end

    if peri_or_apoapsis == StoppingEvent.PERIAPSIS:
        assert np.linalg.norm(state_last.position) == approx(periapsis_radius, abs=1e-3)
    elif peri_or_apoapsis == StoppingEvent.APOAPSIS:
        assert np.linalg.norm(state_last.position) == approx(apoapsis_radius, abs=1e-3)
