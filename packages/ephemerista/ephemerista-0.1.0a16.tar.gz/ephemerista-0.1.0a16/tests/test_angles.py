import math

from pytest import approx

from ephemerista.angles import Angle


def test_angle():
    angle = Angle(degrees=90)
    assert angle.radians == approx(math.pi / 2)
