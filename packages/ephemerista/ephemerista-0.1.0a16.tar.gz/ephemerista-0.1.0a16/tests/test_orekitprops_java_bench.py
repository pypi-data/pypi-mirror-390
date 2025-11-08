import pytest

from ephemerista.angles import Angle
from ephemerista.bodies import Origin
from ephemerista.coords.anomalies import TrueAnomaly
from ephemerista.coords.shapes import RadiiShape
from ephemerista.coords.twobody import Inclination, Keplerian
from ephemerista.propagators.orekit.numerical import NumericalPropagator
from ephemerista.propagators.orekit.semianalytical import SemiAnalyticalPropagator
from ephemerista.time import Time


@pytest.mark.parametrize("py_prop_class", [NumericalPropagator, SemiAnalyticalPropagator])
@pytest.mark.parametrize("grav_degree_order", [(4, 4)])
@pytest.mark.parametrize("enable_srp", [False])
@pytest.mark.parametrize("enable_drag", [False])
@pytest.mark.parametrize("third_bodies", [[Origin(name="sun"), Origin(name="luna")]])
def test_orekitprop_bench(py_prop_class, enable_srp, enable_drag, grav_degree_order, third_bodies):
    apoapsis_radius = 7000.0  # km
    periapsis_radius = 6900.0  # km
    time_start = Time.from_iso("TDB", "2016-05-15T12:00:00")
    time_end = Time.from_iso("TDB", "2016-05-30T14:00:00")
    t_step = 60.0  # s
    time_list = time_start.trange(time_end, t_step)

    py_prop = py_prop_class(
        state_init=Keplerian(
            time=time_start,
            shape=RadiiShape(ra=apoapsis_radius, rp=periapsis_radius),
            inc=Inclination(degrees=98.0),
            node=Angle(degrees=0.0),
            arg=Angle(degrees=0.0),
            anomaly=TrueAnomaly(degrees=90.0),  # starting somewhere in between apoapsis and periapsis
        ),
        enable_srp=enable_srp,
        enable_drag=enable_drag,
        grav_degree_order=grav_degree_order,
        third_bodies=third_bodies,
    )

    _traj_python = py_prop.propagate(time=time_list)

    assert True
