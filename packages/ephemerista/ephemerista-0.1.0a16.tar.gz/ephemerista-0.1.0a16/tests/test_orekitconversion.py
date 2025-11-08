import numpy as np
from pytest import approx

from ephemerista.coords.twobody import Cartesian
from ephemerista.propagators.orekit.conversions import (
    abs_date_to_time,
    cartesian_to_tpv,
    time_to_abs_date,
    tpv_to_cartesian,
)
from ephemerista.time import Time


def compare_time_vs_abs_date(time: Time, abs_date, orekit_scale):
    abs_date_components = abs_date.getComponents(orekit_scale)
    orekit_date = abs_date_components.getDate()
    orekit_time = abs_date_components.getTime()

    assert orekit_date.getYear() == time.year
    assert orekit_date.getMonth() == time.month
    assert orekit_date.getDay() == time.day
    assert orekit_time.getHour() == time.hour
    assert orekit_time.getMinute() == time.minute
    assert abs(orekit_time.getSecond() - time.seconds) == approx(0.0, abs=1e-6)


def test_time_to_abs_date_tai():
    time_tai_str = "2016-05-30T12:30:17.123456"
    time_tai = Time.from_iso("TAI", time_tai_str)
    abs_date = time_to_abs_date(time_tai)
    from org.orekit.time import TimeScalesFactory  # type: ignore  # noqa: PLC0415

    compare_time_vs_abs_date(time_tai, abs_date, TimeScalesFactory.getTAI())


def test_time_to_abs_date_utc():
    time_utc_str = "2016-05-30T12:30:17.123456"
    time_utc = Time.from_utc(time_utc_str)
    abs_date = time_to_abs_date(time_utc)
    from org.orekit.time import TimeScalesFactory  # type: ignore  # noqa: PLC0415

    compare_time_vs_abs_date(time_utc, abs_date, TimeScalesFactory.getTAI())


def test_abs_date_to_time_tai():
    time_tai_str = "2016-05-30T12:30:17.123456"

    from org.orekit.time import AbsoluteDate, TimeScalesFactory  # type: ignore  # noqa: PLC0415

    abs_date = AbsoluteDate(time_tai_str, TimeScalesFactory.getTAI())
    time_tai = abs_date_to_time(abs_date)

    compare_time_vs_abs_date(time_tai, abs_date, TimeScalesFactory.getTAI())


def test_abs_date_to_time_tai_before_j2000():
    time_tai_str = "1998-05-30T12:30:17.123456"

    from org.orekit.time import AbsoluteDate, TimeScalesFactory  # type: ignore  # noqa: PLC0415

    abs_date = AbsoluteDate(time_tai_str, TimeScalesFactory.getTAI())
    time_tai = abs_date_to_time(abs_date)

    compare_time_vs_abs_date(time_tai, abs_date, TimeScalesFactory.getTAI())


def test_abs_date_to_time_utc():
    time_utc_str = "2016-05-30T12:30:17.123456"

    from org.orekit.time import AbsoluteDate, TimeScalesFactory  # type: ignore  # noqa: PLC0415

    abs_date = AbsoluteDate(time_utc_str, TimeScalesFactory.getUTC())
    time_tai = abs_date_to_time(abs_date)

    compare_time_vs_abs_date(time_tai, abs_date, TimeScalesFactory.getTAI())


def test_abs_date_to_time_to_abs_date_tai():
    time_tai_str = "2016-05-30T12:30:17.123456"

    from org.orekit.time import AbsoluteDate, TimeScalesFactory  # type: ignore  # noqa: PLC0415

    abs_date = AbsoluteDate(time_tai_str, TimeScalesFactory.getTAI())
    time_tai = abs_date_to_time(abs_date)
    abs_date_2 = time_to_abs_date(time_tai)
    assert abs(abs_date.durationFrom(abs_date_2)) == approx(0.0, abs=1e-6)  # second


def test_abs_date_to_time_to_abs_date_utc():
    time_utc_str = "2016-05-30T12:30:17.123456"

    from org.orekit.time import AbsoluteDate, TimeScalesFactory  # type: ignore  # noqa: PLC0415

    abs_date = AbsoluteDate(time_utc_str, TimeScalesFactory.getUTC())
    time_tai = abs_date_to_time(abs_date)

    abs_date_2 = time_to_abs_date(time_tai)
    assert abs(abs_date.durationFrom(abs_date_2)) == approx(0.0, abs=1e-6)  # second


def test_time_to_abs_date_to_time_tai():
    time_tai_str = "2016-05-30T12:30:17.123456"
    time_tai = Time.from_iso("TAI", time_tai_str)
    abs_date = time_to_abs_date(time_tai)

    time_tai_2 = abs_date_to_time(abs_date)

    assert time_tai.isclose(time_tai_2, atol=1e-9)


def test_time_to_abs_date_to_time_utc():
    time_utc_str = "2016-05-30T12:30:17.123456"
    time_utc = Time.from_utc(time_utc_str)
    abs_date = time_to_abs_date(time_utc)

    time_tai = abs_date_to_time(abs_date)
    time_tai_2 = time_utc.to_scale("TAI")
    assert time_tai.isclose(time_tai_2, atol=1e-9)


def test_cartesian_to_tpv_to_cartesian():
    time_tai_str = "2016-05-30T12:30:17.123456"
    time_tai = Time.from_iso("TAI", time_tai_str)
    r = 1e-3 * np.array([7e6, 1e6, 1e3])
    v = 1e-3 * np.array([1e2, 7e3, 1.0])
    cart = Cartesian.from_rv(time=time_tai, r=r, v=v)
    tpv = cartesian_to_tpv(cart)
    cart2 = tpv_to_cartesian(tpv)
    delta_pos = cart2.position - cart.position
    delta_vel = cart2.velocity - cart.velocity
    assert np.linalg.norm(delta_pos) == approx(0.0, abs=1e-6)
    assert np.linalg.norm(delta_vel) == approx(0.0, abs=1e-6)
