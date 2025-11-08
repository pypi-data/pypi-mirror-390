"""The time.py module.

This module contains the :py:class:`Time` class which is Ephemerista's representation for points in time (epochs).
"""

from datetime import datetime
from typing import Literal, Self, cast, overload

import lox_space as lox
import numpy as np
from pydantic import ConfigDict, Field, PrivateAttr, model_serializer

from ephemerista import BaseModel, get_eop_provider

JD_J2000: float = 2451545.0

type Scale = Literal["TT", "TAI", "TDB", "TCG", "TCB", "UT1"]

TimeDelta = lox.TimeDelta


class SecondsTimestamp(BaseModel):
    """A timestamp modelled as seconds and subsecond from the J2000 epoch."""

    time_type: Literal["seconds"] = Field(
        default="seconds",
        alias="type",
        frozen=True,
        repr=False,
        description="The type of the timestamp",
    )
    seconds: int
    subsecond: float


class UTCTimestamp(BaseModel):
    """A timestamp modelled as an ISO8601 string in UTC."""

    time_type: Literal["utc"] = Field(
        default="utc",
        alias="type",
        frozen=True,
        repr=False,
        description="The type of the timestamp",
    )
    value: str


class ISOTimestamp(BaseModel):
    """A timestamp modelled as an ISO8601 string in a continuous time scale."""

    time_type: Literal["iso"] = Field(
        default="iso",
        alias="type",
        frozen=True,
        repr=False,
        description="The type of the timestamp",
    )
    value: str


class JulianDateTimestamp(BaseModel):
    """A timestamp modelled as a Julian Day Number."""

    time_type: Literal["jd"] = Field(
        default="jd",
        alias="type",
        frozen=True,
        repr=False,
        description="The type of the timestamp",
    )
    value: float


class Time(BaseModel):  # noqa: PLW1641
    """The ``Time`` model.

    This class models an instant in a continuous time scale based on different timestamp formats.
    """

    model_config = ConfigDict(frozen=True)
    scale: Scale = Field(default="TAI")
    timestamp: SecondsTimestamp | UTCTimestamp | ISOTimestamp | JulianDateTimestamp = Field(discriminator="time_type")
    _time: lox.Time = PrivateAttr()

    def __init__(self, time: lox.Time | None = None, **data):
        super().__init__(**data)
        if not time:
            if isinstance(self.timestamp, ISOTimestamp):
                self._time = lox.Time.from_iso(self.timestamp.value, self.scale)
            elif isinstance(self.timestamp, JulianDateTimestamp):
                self._time = lox.Time.from_julian_date(self.scale, self.timestamp.value)
            elif isinstance(self.timestamp, UTCTimestamp):
                self._time = lox.UTC.from_iso(self.timestamp.value).to_scale("TAI")
            else:
                self._time = lox.Time.from_seconds(self.scale, self.timestamp.seconds, self.timestamp.subsecond)
        else:
            self._time = time

    @classmethod
    def _from_lox(cls, time: lox.Time) -> Self:
        scale = str(time.scale())
        timestamp = SecondsTimestamp(seconds=time.seconds(), subsecond=time.subsecond())
        return cls(scale=scale, timestamp=timestamp, time=time)

    @classmethod
    def from_components(
        cls,
        scale: Scale,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        seconds: float = 0.0,
    ) -> Self:
        """
        Instantiate a Time object from its components in the given time scale.

        Parameters
        ----------
        year : int
            The year of the timestamp
        month : int
            The month of the timestamp
        day : int
            The day of the timestamp
        hour : int
            The hour of the timestamp (default 0)
        minute : int
            The minute of the timestamp (default 0)
        seconds : float
            The seconds of the timestamp (default 0.0)
        scale : Scale
            The time scale of the timestamp
        """
        time = lox.Time(scale, year, month, day, hour, minute, seconds)
        timestamp = SecondsTimestamp(seconds=time.seconds(), subsecond=time.subsecond())
        return cls(scale=scale, timestamp=timestamp, time=time)

    @classmethod
    def from_day_of_year(
        cls,
        scale: Scale,
        year: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        seconds: float = 0.0,
    ) -> Self:
        """
        Instantiate a Time object from its components in the given time scale.

        Parameters
        ----------
        year : int
            The year of the timestamp
        month : int
            The month of the timestamp
        day : int
            The day of the timestamp
        hour : int
            The hour of the timestamp (default 0)
        minute : int
            The minute of the timestamp (default 0)
        seconds : float
            The seconds of the timestamp (default 0.0)
        scale : Scale
            The time scale of the timestamp
        """
        time = lox.Time.from_day_of_year(scale, year, day, hour, minute, seconds)
        timestamp = SecondsTimestamp(seconds=time.seconds(), subsecond=time.subsecond())
        return cls(scale=scale, timestamp=timestamp, time=time)

    @classmethod
    def from_iso(cls, scale: Scale, iso: str) -> Self:
        """
        Instantiate a Time object from an ISO8601-formatted string in the given time scale.

        Parameters
        ----------
        scale : Scale
            The time scale of the timestamp
        iso : str
            An ISO8601-formatted timestamp
        """
        return cls(scale=scale, timestamp=ISOTimestamp(value=iso))

    @classmethod
    def from_utc(cls, utc: str) -> Self:
        """
        Instantiate a Time object from an ISO8601-formatted string in the UTC scale.

        The returned Time object will be in the TAI scale.

        Parameters
        ----------
        scale : Scale
            The time scale of the timestamp
        iso : str
            An ISO8601-formatted timestamp
        """
        return cls(scale="TAI", timestamp=UTCTimestamp(value=utc))

    @classmethod
    def from_julian_date(cls, scale: Scale, jd: float) -> Self:
        """
        Instantiate a Time object from a Julian Date in the given time scale.

        Parameters
        ----------
        scale : Scale
            The time scale of the timestamp
        jd : float
            The Julian Date of the timestamp
        """
        return cls(scale=scale, timestamp=JulianDateTimestamp(value=jd))

    @classmethod
    def from_j2000(cls, scale: Scale, j2000: float) -> Self:
        """
        Instantiate a Time object from a Julian Date based on the J2000 epoch in the given time scale.

        Parameters
        ----------
        scale : Scale
            The time scale of the timestamp
        jd : float
            The Julian Date of the timestamp
        """
        return cls.from_julian_date(scale, j2000 + JD_J2000)

    @classmethod
    def from_two_part_julian_date(cls, scale: Scale, jd1: float, jd2: float) -> Self:
        """
        Instantiate a Time object from a two-part Julian Date in the given time scale.

        Parameters
        ----------
        scale : Scale
            The time scale of the timestamp
        jd1 : float
            The first part of the Julian Date
        jd2 : float
            The second part of the Julian Date
        """
        time = lox.Time.from_two_part_julian_date(scale, jd1, jd2)
        timestamp = SecondsTimestamp(seconds=time.seconds(), subsecond=time.subsecond())
        return cls(scale=scale, timestamp=timestamp, time=time)

    @property
    def year(self) -> int:
        """int: The year."""
        return self._time.year()

    @property
    def month(self) -> int:
        """int: The month."""
        return self._time.month()

    @property
    def day(self) -> int:
        """int: The day."""
        return self._time.day()

    @property
    def day_of_year(self) -> int:
        """int: The day of the year (1-366)."""
        return self._time.day_of_year()

    @property
    def hour(self) -> int:
        """int: The hour."""
        return self._time.hour()

    @property
    def minute(self) -> int:
        """int: The minute."""
        return self._time.minute()

    @property
    def second(self) -> int:
        """int: The second."""
        return self._time.second()

    @property
    def seconds(self) -> float:
        """float: Second and subsecond as a decimal number."""
        return self._time.decimal_seconds()

    @property
    def julian_date(self) -> float:
        """float: The Julian Day number."""
        return self._time.julian_date()

    @property
    def j2000(self) -> float:
        """float: The Julian Day number with epoch J2000."""
        return self._time.julian_date("j2000")

    @property
    def two_part_julian_date(self) -> tuple[float, float]:
        """tuple[float, float]: The Julian Day number split into two parts."""
        return self._time.two_part_julian_date()

    def __eq__(self, rhs: object) -> bool:
        """Check two `Time` objects for equality."""
        return self._time == cast(Time, rhs)._time

    def to_scale(self, scale: Scale) -> "Time":
        """
        Convert the Time object to a different time scale.

        Parameters
        ----------
        scale : Scale
            The time scale to convert the Time object to
        """
        return Time._from_lox(self._time.to_scale(scale, get_eop_provider()))

    def to_utc(self) -> str:
        """Convert the Time object to a UTC-formatted string."""
        return str(self._time.to_utc())

    @property
    def datetime(self) -> datetime:
        """Convert to a `datetime.datetime` object."""
        return datetime.fromisoformat(self.to_utc().split()[0])

    def __add__(self, other: TimeDelta) -> "Time":
        """Add `TimeDelta` to `Time`."""
        return Time._from_lox(self._time + other)

    @overload
    def __sub__(self, other: TimeDelta) -> Self: ...

    @overload
    def __sub__(self, other: Self) -> TimeDelta: ...

    def __sub__(self, other: TimeDelta | Self) -> "Time | TimeDelta":
        """Substract two `Time` objects or subtract a `TimeDelta` from a single `Time`.

        Returns
        -------
        Time | TimeDelta
            A `TimeDelta` when subtracting two `Time`s or the adjusted `Time` when subtracting
            a `TimeDelta` from a single `Time`.
        """
        if isinstance(other, Time):
            return self._time - other._time
        else:
            return Time._from_lox(self._time - other)

    def isclose(self, other: Self, atol: float = 1e-9, rtol: float = 1e-8) -> bool:
        """Check if two `Time` objects are equal within a given tolerance."""
        return self._time.isclose(other._time, rtol, atol)

    def trange(self, end: Self, step: float = 1) -> list["Time"]:
        """
        Generate a range of Time objects between the current Time object and the end Time object.

        Parameters
        ----------
        end : Time
            The end of the range
        step : float
            The step size in seconds
        """
        interval = float(end - self)
        rng = np.arange(0, interval, step)
        if not np.isclose(rng[-1], interval):
            rng = np.append(rng, interval)
        times = [self + TimeDelta(t) for t in rng]
        return times

    def trange_fast(self, end: Self, step: float = 1) -> list["Time"]:
        """
        Generate a range of Time objects between the current Time object and the end Time object.

        Optimized version that creates Time objects more efficiently.

        Parameters
        ----------
        end : Time
            The end of the range
        step : float
            The step size in seconds
        """
        interval = float(end - self)
        rng = np.arange(0, interval, step)
        if not np.isclose(rng[-1], interval):
            rng = np.append(rng, interval)

        # Create Time objects more efficiently
        times = []
        for t in rng:
            # Use the same mechanism as trange but pre-create TimeDelta
            delta = TimeDelta(t)
            times.append(self + delta)
        return times

    @model_serializer(when_used="json")
    def _serialize_to_utc(self):
        utc = str(self._time.to_utc()).replace(" UTC", "Z")
        model = {"scale": self.scale, "timestamp": {"type": "utc", "value": utc}}
        return model
