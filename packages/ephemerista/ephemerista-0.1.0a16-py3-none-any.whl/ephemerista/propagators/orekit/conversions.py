"""The conversions.py module.

This module contains utility functions for converting between Ephemerista and Orekit types.
"""

from math import floor

import numpy as np

from ephemerista.coords.anomalies import MeanAnomaly
from ephemerista.coords.trajectories import Trajectory
from ephemerista.coords.twobody import Cartesian, Keplerian
from ephemerista.frames import ReferenceFrame
from ephemerista.time import SecondsTimestamp, Time


def time_to_j2000_tai(time: Time) -> float:
    """Convert `Time` to Julian Day number in the TAI scale and J2000 epoch."""
    time_tai = time.to_scale("TAI")
    return time_tai._time.seconds() + time_tai._time.subsecond()


def time_to_abs_date(time: Time):
    """Convert `Time` to an ``AbsoluteDate``, after having converted the Time object to TAI scale."""
    from org.orekit.time import AbsoluteDate, TimeScalesFactory  # type: ignore  # noqa: PLC0415

    j2000_epoch_tai = AbsoluteDate(2000, 1, 1, 12, 0, 0.0, TimeScalesFactory.getTAI())
    return AbsoluteDate(j2000_epoch_tai, time_to_j2000_tai(time), TimeScalesFactory.getTAI())


def abs_date_to_time(abs_date) -> Time:
    """Return the Time representation of the given AbsoluteDate, in TAI scale."""
    from org.orekit.time import AbsoluteDate, TimeScalesFactory  # type: ignore  # noqa: PLC0415

    j2000_epoch_tai = AbsoluteDate(2000, 1, 1, 12, 0, 0.0, TimeScalesFactory.getTAI())
    j2000_float = abs_date.durationFrom(j2000_epoch_tai)
    j2000_seconds = floor(j2000_float)
    j2000_subsecond = j2000_float - j2000_seconds
    return Time(scale="TAI", timestamp=SecondsTimestamp(seconds=j2000_seconds, subsecond=j2000_subsecond))


def cartesian_to_tpv(cart: Cartesian):
    """Convert `Cartesian` to ``TimeStampedPVCoordinates``."""
    from org.hipparchus.geometry.euclidean.threed import Vector3D  # type: ignore  # noqa: PLC0415

    pos_icrf = Vector3D(cart.x * 1e3, cart.y * 1e3, cart.z * 1e3)
    vel_icrf = Vector3D(cart.vx * 1e3, cart.vy * 1e3, cart.vz * 1e3)
    from org.orekit.utils import TimeStampedPVCoordinates  # type: ignore  # noqa: PLC0415

    return TimeStampedPVCoordinates(time_to_abs_date(cart.time), pos_icrf, vel_icrf)


def cartesian_to_orbit(cart: Cartesian):
    """Convert `Cartesian` to ``CartesianOrbit``."""
    from org.orekit.frames import FramesFactory  # type: ignore  # noqa: PLC0415
    from org.orekit.orbits import CartesianOrbit  # type: ignore  # noqa: PLC0415

    if not cart.frame == ReferenceFrame():
        msg = "only ICRF is supported"
        raise ValueError(msg)
    tpv = cartesian_to_tpv(cart)
    frame = FramesFactory.getGCRF()  # Earth-centered ICRF
    mu = cart.origin.gravitational_parameter
    return CartesianOrbit(tpv, frame, mu)


def tpv_to_cartesian(tpv) -> Cartesian:
    """Convert ``TimeStampedPVCoordinates`` to `Cartesian`."""
    return Cartesian.from_rv(
        time=abs_date_to_time(tpv.getDate()),
        r=1e-3 * np.array(tpv.getPosition().toArray()),
        v=1e-3 * np.array(tpv.getVelocity().toArray()),
    )


def orekit_to_keplerian(kepl_orekit) -> Keplerian:
    """Convert ``KeplerianOrbit`` to `Keplerian`."""
    return Keplerian.from_elements(
        time=abs_date_to_time(kepl_orekit.getDate()),
        semi_major_axis=kepl_orekit.getA() * 1e-3,
        eccentricity=kepl_orekit.getE(),
        inclination=np.rad2deg(kepl_orekit.getI()),
        ascending_node=np.rad2deg(kepl_orekit.getRightAscensionOfAscendingNode()),
        periapsis_argument=np.rad2deg(kepl_orekit.getPerigeeArgument()),
        anomaly=np.rad2deg(kepl_orekit.getMeanAnomaly()),
        anomaly_type=MeanAnomaly,  # type: ignore
    )


def trajectory_to_ephemeris(t: Trajectory):
    """Convert `Trajectory` to ``Ephemeris``."""
    from java.util import ArrayList  # type: ignore  # noqa: PLC0415
    from org.orekit.propagation import (  # type: ignore  # noqa: PLC0415
        SpacecraftState,
        SpacecraftStateInterpolator,
    )
    from org.orekit.propagation.analytical import Ephemeris  # type: ignore  # noqa: PLC0415

    states = ArrayList([SpacecraftState(cartesian_to_orbit(s)) for s in t.cartesian_states])
    return Ephemeris(states, SpacecraftStateInterpolator(states[0].getFrame()))
