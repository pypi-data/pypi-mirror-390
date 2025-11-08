import os

import numpy as np
import pytest
from pytest import approx

from ephemerista.coords.twobody import Cartesian
from ephemerista.propagators.orekit.ccsds import (
    CcsdsFileFormat,
    parse_oem,
    parse_omm,
    parse_opm,
    write_oem,
    write_omm,
    write_opm,
)
from ephemerista.time import Time


def check_cart_equal(c_exp: Cartesian, c_act: Cartesian):
    assert c_exp.time.isclose(c_act.time)
    assert c_exp.isclose(c_act)


def test_oem_read(resources):
    oem_ex = resources / "ccsds" / "odm" / "oem" / "OEMExample5.txt"
    dt = 1800.0
    trajectory = parse_oem(oem_ex, dt)
    cart_states = trajectory.cartesian_states
    check_cart_equal(
        Cartesian.from_rv(
            Time.from_utc("2017-04-11T22:31:43.121856"),
            np.array([2906.2752178573, 4076.3580691129, 4561.3636609099]),
            np.array([-6.8794973158, 1.4495313106, 3.0813176196]),
        ),
        cart_states[0],
    )

    check_cart_equal(
        Cartesian.from_rv(
            Time.from_utc("2017-04-12T22:31:43.121856"),
            np.array([-1212.0312303805, -4196.2446023828, -5200.9281612207]),
            np.array([7.5222575948, -0.5747199952, -1.2870157271]),
        ),
        cart_states[-1],
    )


@pytest.mark.parametrize("file_format", [CcsdsFileFormat.KVN, CcsdsFileFormat.XML])
def test_oem_read_write_read(resources, file_format):
    oem_ex = resources / "ccsds" / "odm" / "oem" / "OEMExample5.txt"
    if file_format == CcsdsFileFormat.KVN:
        oem_file_out = "oem_tmp.txt"
    else:
        oem_file_out = "oem_tmp.xml"

    dt = 300.0
    traj_0 = parse_oem(oem_ex, dt)
    write_oem(traj_0, oem_file_out, dt, file_format)
    traj_1 = parse_oem(oem_file_out, dt)

    for cart0, cart1 in zip(traj_0.cartesian_states, traj_1.cartesian_states, strict=False):
        check_cart_equal(cart0, cart1)

    if os.path.isfile(oem_file_out):
        os.remove(oem_file_out)


def test_omm_read(resources):
    omm_ex = resources / "ccsds" / "odm" / "omm" / "OMMExample1.txt"
    cart_act = parse_omm(omm_ex)
    kepl_act = cart_act.to_keplerian()

    assert kepl_act.time.isclose(Time.from_utc("2007-03-05T10:34:41.4264"))

    # The following thresholds are low because the OMM is in TEME frame, and we convert internally to ICRF
    mean_motion_act = 86400.0 / kepl_act.orbital_period.to_decimal_seconds()
    assert mean_motion_act == approx(1.00273272, rel=1e-3)
    assert kepl_act.eccentricity == approx(0.0005013, rel=1e-2)
    assert np.rad2deg(kepl_act.inclination) == approx(3.0539, rel=2.5e-2)
    assert np.rad2deg(kepl_act.ascending_node) == approx(81.7939, rel=1e-3)
    assert np.rad2deg(kepl_act.periapsis_argument) == approx(249.2363, rel=1e-3)
    assert np.rad2deg(kepl_act.mean_anomaly) == approx(150.1602, rel=1e-3)


@pytest.mark.parametrize("file_format", [CcsdsFileFormat.KVN, CcsdsFileFormat.XML])
def test_omm_read_write_read(resources, file_format):
    omm_ex = resources / "ccsds" / "odm" / "omm" / "OMMExample1.txt"

    if file_format == CcsdsFileFormat.KVN:
        omm_file_out = "omm_tmp.txt"
    else:
        omm_file_out = "omm_tmp.xml"

    cart_0 = parse_omm(omm_ex)
    write_omm(cart_0, omm_file_out, file_format)
    cart_1 = parse_omm(omm_file_out)

    assert cart_0.time.isclose(cart_1.time)
    assert cart_0.isclose(cart_1, atol_p=1e-6, atol_v=1e-6)

    if os.path.isfile(omm_file_out):
        os.remove(omm_file_out)


def test_opm_read(resources):
    opm_ex = resources / "ccsds" / "odm" / "opm" / "OPMExample5.txt"
    cart_act = parse_opm(opm_ex)

    check_cart_equal(
        Cartesian.from_rv(
            Time.from_utc("2006-06-03T00:00:00.000"),
            np.array([6655.9942, -40218.5751, -82.9177]),
            np.array([3.11548208, 0.47042605, -0.00101495]),
        ),
        cart_act,
    )


@pytest.mark.parametrize("file_format", [CcsdsFileFormat.KVN, CcsdsFileFormat.XML])
def test_opm_read_write_read(resources, file_format):
    opm_ex = resources / "ccsds" / "odm" / "opm" / "OPMExample5.txt"

    if file_format == CcsdsFileFormat.KVN:
        opm_file_out = "opm_tmp.txt"
    else:
        opm_file_out = "opm_tmp.xml"

    cart_0 = parse_opm(opm_ex)
    write_opm(cart_0, opm_file_out, file_format)
    cart_1 = parse_opm(opm_file_out)

    check_cart_equal(cart_0, cart_1)

    if os.path.isfile(opm_file_out):
        os.remove(opm_file_out)
