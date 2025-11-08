"""The angles.py module.

This module contains the ``Angle`` class which provides a generic angle model for other Ephemerista data structures.
"""

import math
from typing import Self

from pydantic import Field, PrivateAttr

from ephemerista import BaseModel


class Angle(BaseModel):
    """
    Generic angle model.

    Notes
    -----
    Subclasses of ``Angle`` may override the ``degrees`` field to customise constraints.

    Examples
    --------
    >>> class Inclination(Angle):
    ...     degrees: float = Field(ge=0, le=180)
    >>> inc = Inclination.from_radians(1.5707963267948966)
    >>> inc.degrees
    90.0
    """

    degrees: float = Field(description="Value of the angle in degrees")
    _radians: float = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._radians = math.radians(self.degrees)

    @classmethod
    def from_radians(cls, radians: float) -> Self:
        """
        Construct an ``Angle`` object from a value in radians.

        Parameters
        ----------
        radians : float
            The value of the angle in radians
        """
        return cls(degrees=math.degrees(radians))

    @classmethod
    def from_degrees(cls, degrees: float) -> Self:
        """
        Construct an ``Angle`` object from a value in degrees.

        Parameters
        ----------
        degrees : float
            The value of the angle in degrees
        """
        return cls(degrees=degrees)

    @property
    def radians(self):
        """float: Value of the angle in radians."""
        return self._radians


class Longitude(Angle):
    """Longitude."""

    degrees: float = Field(ge=-180, le=180, description="Longitude in degrees")


class Latitude(Angle):
    """Latitude."""

    degrees: float = Field(ge=-90, le=90, description="Latitude in degrees")
