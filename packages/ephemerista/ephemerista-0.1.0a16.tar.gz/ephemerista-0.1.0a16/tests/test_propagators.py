import numpy as np
import numpy.testing as npt
import pytest

from ephemerista.assets import GroundStation
from ephemerista.time import Time


@pytest.mark.parametrize(
    "time,expected",
    [
        (
            Time.from_utc("2022-01-31T23:00:00"),
            np.array([-1771.962631551279, 4522.356363399281, 4120.057120495107]),
        ),
        # (
        #     Time.from_utc("2022-03-22T06:22:48.027"),
        #     np.array([75.85079609053327, -4859.680827946813, 4116.330675316688]),
        # ),
    ],
)
def test_groundstation(time, expected):
    gs = GroundStation.from_lla(latitude=40.4527, longitude=-4.3676, altitude=0.0)

    actual = gs.propagate(time)._cartesian.position()
    npt.assert_allclose(actual, expected, rtol=1e-2)
