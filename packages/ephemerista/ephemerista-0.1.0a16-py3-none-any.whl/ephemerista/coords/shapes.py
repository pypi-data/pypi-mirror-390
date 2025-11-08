"""The shapes.py module.

This module provides several classes which provide different ways to define the shape of an orbit.

- Semi-major axis and eccentricity: :py:class:`SemiMajorAxisShape`
- Radius pairs: :py:class:`RadiiShape`
- Altitude pairs: :py:class:`AltitudesShape`

Notes
-----
The classes in this module are part of the :py:class:`ephemerista.coords.twobody.Keplerian` data model
for Keplerian orbits and should not be used directly.
"""

import abc
from typing import Literal

from pydantic import Field

from ephemerista import BaseModel

DISCRIMINATOR: Literal["shape_type"] = "shape_type"


class OrbitShape(BaseModel, abc.ABC):
    """Abstract base class for orbital shapes."""

    @abc.abstractmethod
    def semi_major_axis(self, mean_radius: float) -> float:
        """
        Return the semi-major axis of the orbit in kilometers.

        Parameters
        ----------
        mean_radius: float
            Mean radius of the central body [km]

        Notes
        -----
        The ``mean_radius`` parameter is not being used by the ``SemiMajorAxisShape`` and ``RadiiShape`` subclasses and
        can be set to zero.
        """
        pass

    @abc.abstractmethod
    def eccentricity(self, mean_radius: float) -> float:
        """
        Return the eccentricity of the orbit.

        Parameters
        ----------
        mean_radius: float
            Mean radius of the central body [km]

        Notes
        -----
        The ``mean_radius`` parameter is not being used by the ``SemiMajorAxisShape`` and ``RadiiShape`` subclasses.
        """
        pass

    @abc.abstractmethod
    def apoapsis_radius(self, mean_radius: float) -> float:
        """
        Return the apoapsis radius of the orbit in kilometers.

        Parameters
        ----------
        mean_radius: float
            Mean radius of the central body [km]

        Notes
        -----
        The ``mean_radius`` parameter is not being used by the ``SemiMajorAxisShape`` and ``RadiiShape`` subclasses.
        """
        pass

    @abc.abstractmethod
    def periapsis_radius(self, mean_radius: float) -> float:
        """
        Return the periapsis radius of the orbit in kilometers.

        Parameters
        ----------
        mean_radius: float
            Mean radius of the central body [km]

        Notes
        -----
        The ``mean_radius`` parameter is not being used by the ``SemiMajorAxisShape`` and ``RadiiShape`` subclasses.
        """
        pass


class SemiMajorAxisShape(OrbitShape):
    """Orbit shape based on semi-major axis and eccentricity."""

    shape_type: Literal["semi_major"] = Field(
        default="semi_major",
        frozen=True,
        repr=False,
        alias="type",
        description="The type of the orbit shape",
    )
    sma: float = Field(
        alias="semiMajorAxis",
        description="Semi-major axis of the orbit [km]",
    )
    ecc: float = Field(
        alias="eccentricity",
        description="Eccentricity of the orbit",
    )

    def semi_major_axis(self, mean_radius: float) -> float:  # noqa: ARG002
        """Return the semi-major axis of the orbit in kilometers."""
        return self.sma

    def eccentricity(self, mean_radius: float) -> float:  # noqa: ARG002
        """Return the eccentricity of the orbit."""
        return self.ecc

    def apoapsis_radius(self, mean_radius: float) -> float:  # noqa: ARG002
        """Return the apoapsis radius of the orbit in kilometers."""
        return self.sma * (1 + self.ecc)

    def periapsis_radius(self, mean_radius: float) -> float:  # noqa: ARG002
        """Return the periapsis radius of the orbit in kilometers."""
        return self.sma * (1 - self.ecc)


class RadiiShape(OrbitShape):
    """Orbit shape based on apoapsis and periapsis radius."""

    shape_type: Literal["radii"] = Field(
        default="radii",
        frozen=True,
        repr=False,
        alias="type",
        description="The type of the orbit shape",
    )
    ra: float = Field(
        gt=0,
        alias="apoapsisRadius",
        description="The apoapsis radius of the orbit [km]",
    )
    rp: float = Field(
        gt=0,
        alias="periapsisRadius",
        description="The periapsis radius of the orbit [km]",
    )

    def semi_major_axis(self, mean_radius: float) -> float:  # noqa: ARG002
        """Return the semi-major axis of the orbit in kilometers."""
        return (self.ra + self.rp) / 2

    def eccentricity(self, mean_radius: float) -> float:  # noqa: ARG002
        """Return the eccentricity of the orbit."""
        return (self.ra - self.rp) / (self.ra + self.rp)

    def apoapsis_radius(self, mean_radius: float) -> float:  # noqa: ARG002
        """Return the apoapsis radius of the orbit in kilometers."""
        return self.ra

    def periapsis_radius(self, mean_radius: float) -> float:  # noqa: ARG002
        """Return the periapsis radius of the orbit in kilometers."""
        return self.rp


class AltitudesShape(OrbitShape):
    """Orbit shape based on apoapsis and periapsis altitude."""

    shape_type: Literal["altitudes"] = Field(
        default="altitudes",
        frozen=True,
        repr=False,
        alias="type",
        description="The type of the orbit shape",
    )
    apoapsis_altitude: float = Field(
        gt=0,
        alias="apoapsisAltitude",
        description="The apoapsis altitude of the orbit [km]",
    )
    periapsis_altitude: float = Field(
        gt=0,
        alias="periapsisAltitude",
        description="The periapsis altitude of the orbit [km]",
    )

    def semi_major_axis(self, mean_radius: float) -> float:
        """Return the semi-major axis of the orbit in kilometers."""
        apoapsis_radius = self.apoapsis_radius(mean_radius)
        periapsis_radius = self.periapsis_radius(mean_radius)
        return (periapsis_radius + apoapsis_radius) / 2

    def eccentricity(self, mean_radius: float) -> float:
        """Return the eccentricity of the orbit."""
        apoapsis_radius = self.apoapsis_radius(mean_radius)
        periapsis_radius = self.periapsis_radius(mean_radius)
        return (apoapsis_radius - periapsis_radius) / (apoapsis_radius + periapsis_radius)

    def apoapsis_radius(self, mean_radius: float) -> float:
        """Return the apoapsis radius of the orbit in kilometers."""
        return self.apoapsis_altitude + mean_radius

    def periapsis_radius(self, mean_radius: float) -> float:
        """Return the periapsis radius of the orbit in kilometers."""
        return self.periapsis_altitude + mean_radius


type Shape = SemiMajorAxisShape | RadiiShape | AltitudesShape
