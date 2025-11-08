import pytest

from ephemerista.propagators.orekit.numerical import NumericalPropagator
from ephemerista.propagators.orekit.semianalytical import SemiAnalyticalPropagator

OREKIT_PROP_CLASSES = [NumericalPropagator, SemiAnalyticalPropagator]


def check_coeffs_at_degree(deg_order):
    from org.orekit.forces.gravity.potential import GravityFieldFactory  # type: ignore  # noqa: PLC0415

    coeff_reader = GravityFieldFactory.readGravityField(deg_order, deg_order)
    assert coeff_reader.getMaxAvailableDegree() == deg_order
    assert coeff_reader.getMaxAvailableOrder() == deg_order


def check_coeffs_until_degree(max_deg_order):
    from org.orekit.errors import OrekitException  # type: ignore  # noqa: PLC0415

    check_coeffs_at_degree(max_deg_order)

    with pytest.raises(OrekitException):
        check_coeffs_at_degree(max_deg_order + 1)


@pytest.mark.parametrize("orekit_prop", OREKIT_PROP_CLASSES)
@pytest.mark.parametrize(
    "grav_file,max_deg_order",
    [
        (None, 240),  # Default file in Orekit (EIGEN-6S) has max degree and order 240
        ("ICGEM_GOCO06s.gfc", 300),
    ],
)
def test_load_gravity_file(resources, orekit_prop, grav_file, max_deg_order, c0):
    if grav_file is None:
        gravity_file = None
    else:
        gravity_file = resources / "potential" / grav_file
    _prop = orekit_prop(state_init=c0, gravity_file=gravity_file)

    check_coeffs_until_degree(max_deg_order)

    from org.orekit.forces.gravity.potential import GravityFieldFactory  # type: ignore  # noqa: PLC0415

    # Clear custom gravity file at the end
    GravityFieldFactory.clearPotentialCoefficientsReaders()
    GravityFieldFactory.addDefaultPotentialCoefficientsReaders()
