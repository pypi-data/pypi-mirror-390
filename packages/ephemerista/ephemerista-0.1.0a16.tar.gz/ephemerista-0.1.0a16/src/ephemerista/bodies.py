"""The origin.py module.

This module provides the `Origin` class.
"""

from typing import Self

import lox_space as lox
import numpy as np
import plotly.graph_objects as go
from pydantic import Field, PrivateAttr

from ephemerista import BaseModel


class Origin(BaseModel):
    """The ``Origin`` model.

    This class models coordinate origins which are typically celestial bodies or a barycenters.

    Notes
    -----
    Not all properties are defined for all available origins. Ephemerista will raise an exception
    if the user tries to access an undefined property.
    """

    name: str = Field(description="The name of the origin")
    _origin: lox.Origin = PrivateAttr()

    def __init__(self, origin: lox.Origin | None = None, **data):
        super().__init__(**data)
        if not origin:
            self._origin = lox.Origin(self.name)
            self.name = self._origin.name()
        else:
            self._origin = origin

    @classmethod
    def _from_lox(cls, origin: lox.Origin) -> Self:
        return cls(origin=origin, name=origin.name())

    @property
    def naif_id(self) -> int:
        """int: NAID ID of the origin."""
        return self._origin.id()

    @property
    def gravitational_parameter(self) -> float:
        """float: Gravitational parameter of the origin."""
        return self._origin.gravitational_parameter()

    @property
    def mean_radius(self) -> float:
        """float: Mean radius of the origin in km."""
        return self._origin.mean_radius()

    @property
    def polar_radius(self) -> float:
        """float: Polar radius of the origin in km."""
        return self._origin.polar_radius()

    @property
    def flattening(self) -> float:
        """float: Flattening factor of the origin."""
        return (self.equatorial_radius - self.polar_radius) / self.polar_radius

    @property
    def equatorial_radius(self) -> float:
        """float: The equatorial radius of the celestial body in km."""
        return self._origin.equatorial_radius()

    @property
    def radii(self) -> tuple[float, float, float]:
        """tuple[float, float, float]: Tri-axial ellipsoid of the origin."""
        return self._origin.radii()

    def plot_3d_surface(self) -> go.Mesh3d:
        """Plot the origin as a 3D surface in a ``plotly`` plot."""
        phi = np.linspace(0, 2 * np.pi)
        theta = np.linspace(-np.pi / 2, np.pi / 2)
        phi, theta = np.meshgrid(phi, theta)
        x = np.cos(theta) * np.sin(phi) * self.mean_radius
        y = np.cos(theta) * np.cos(phi) * self.mean_radius
        z = np.sin(theta) * self.mean_radius
        x, y, z = np.vstack([x.ravel(), y.ravel(), z.ravel()])
        return go.Mesh3d(x=x, y=y, z=z, alphahull=0, name=self._origin.name())
