import numpy as np
import pytest

from ephemerista.angles import Angle
from ephemerista.bodies import Origin
from ephemerista.coords.anomalies import TrueAnomaly
from ephemerista.coords.shapes import RadiiShape
from ephemerista.coords.trajectories import Trajectory
from ephemerista.coords.twobody import Inclination, Keplerian
from ephemerista.propagators.orekit import OrekitPropagator
from ephemerista.propagators.orekit.conversions import cartesian_to_tpv, time_to_abs_date, time_to_j2000_tai
from ephemerista.propagators.orekit.numerical import NumericalPropagator
from ephemerista.propagators.orekit.semianalytical import SemiAnalyticalPropagator
from ephemerista.time import Time


def clone_propagator_java(prop: OrekitPropagator, java_prop_class):
    third_bodies_names = [body.name for body in prop.params.third_bodies]
    tpv_icrf_init = cartesian_to_tpv(prop.state_init.to_cartesian())
    return java_prop_class(
        tpv_icrf_init,
        prop.params.prop_min_step,
        prop.params.prop_max_step,
        prop.params.prop_init_step,
        prop.params.prop_position_error,
        prop.params.mass,
        prop.params.cross_section,
        list(prop.params.grav_degree_order) if prop.params.grav_degree_order else [],
        third_bodies_names,
        prop.params.c_r,
        prop.params.enable_srp,
        prop.params.c_d,
        prop.params.enable_drag,
    )


@pytest.mark.parametrize("py_prop_class", [NumericalPropagator, SemiAnalyticalPropagator])
@pytest.mark.parametrize("grav_degree_order", [None, (16, 16)])
@pytest.mark.parametrize("enable_srp", [False, True])
@pytest.mark.parametrize("enable_drag", [False, True])
@pytest.mark.parametrize("third_bodies", [[], [Origin(name="Sun"), Origin(name="luna"), Origin(name="jupiter")]])
def test_comparison_java(py_prop_class, enable_srp, enable_drag, grav_degree_order, third_bodies):
    apoapsis_radius = 7000.0  # km
    periapsis_radius = 6900.0  # km

    time_start = Time.from_iso("TDB", "2016-05-30T12:00:00")
    time_end = Time.from_iso("TDB", "2016-05-30T14:00:00")
    t_step = 300.0  # s
    time_list = time_start.trange(time_end, t_step)
    time_j2000_list = [time_to_j2000_tai(t) for t in time_list]

    state_init = Keplerian(
        time=time_start,
        shape=RadiiShape(ra=apoapsis_radius, rp=periapsis_radius),  # type: ignore
        inc=Inclination(degrees=98.0),
        node=Angle(degrees=0.0),
        arg=Angle(degrees=0.0),
        anomaly=TrueAnomaly(degrees=90.0),  # starting somewhere in between apoapsis and periapsis
    )

    py_prop = py_prop_class(
        state_init=state_init,
        enable_srp=enable_srp,
        enable_drag=enable_drag,
        grav_degree_order=grav_degree_order,
        third_bodies=third_bodies,
    )

    from org.lsf import NumericalPropagatorRef, SemiAnalyticalPropagatorRef  # type: ignore  # noqa: PLC0415

    # The lines below could be parametrized by pytest, but that would require starting the JVM and importing the Java
    # classes at the very beginning of the pytest run...
    if isinstance(py_prop, NumericalPropagator):
        # Matching the Python Propagator classes with their Java counterparts
        java_prop = clone_propagator_java(py_prop, NumericalPropagatorRef)
    elif isinstance(py_prop, SemiAnalyticalPropagator):
        java_prop = clone_propagator_java(py_prop, SemiAnalyticalPropagatorRef)

    traj_python = py_prop.propagate(time=time_list)
    cart_list_python = traj_python.cartesian_states

    stop_conds = []
    time_end_abs = time_to_abs_date(time_end)
    tpv_list = java_prop.propagate(time_j2000_list, time_end_abs, stop_conds)
    states_array = np.asarray(memoryview(tpv_list))
    traj_java = Trajectory(start_time=time_start, states=states_array)
    cart_list_java = traj_java.cartesian_states

    assert len(cart_list_python) == len(cart_list_java)

    for i in range(0, len(cart_list_python)):
        assert cart_list_python[i].isclose(cart_list_java[i], atol_p=1e-6, atol_v=1e-9)
