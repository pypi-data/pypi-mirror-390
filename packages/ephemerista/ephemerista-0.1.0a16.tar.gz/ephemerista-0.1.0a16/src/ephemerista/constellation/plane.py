"""The plane.py module.

This module provides the `Plane` class.
"""

from pydantic import Field

from ephemerista import BaseModel
from ephemerista.bodies import Origin
from ephemerista.coords.twobody import DEFAULT_ORIGIN


class Plane(BaseModel):
    """The `Plane` class.

    This class models an orbital plane of a satellite constellation.
    """

    plane_id: int = Field(description="Plane ID")
    semi_major_axis: float = Field(gt=0, description="Semi major axis, in km")
    eccentricity: float = Field(ge=0, description="Eccentricity")
    inclination: float = Field(ge=0, lt=180.0, description="Inclination, in degrees")
    ascending_node: float = Field(ge=-360.0, lt=360.0, description="Right Ascension of the Ascending Node, in degrees")
    periapsis_argument: float = Field(ge=0, lt=360.0, description="Argument of Perigee, in degrees")
    number_of_satellites: int = Field(gt=0, description="Number of satellites in the plane")
    primary_body: Origin = Field(
        default=DEFAULT_ORIGIN,
        description="Origin of the coordinate system",
    )

    @property
    def elements(self) -> dict:
        """Returns a dictionary of the Plane's Keplerian elements.

        Returns
        -------
            Dict: Keplerian elements
        """
        return self.model_dump(
            include={
                "plane_id",
                "semi_major_axis",
                "eccentricity",
                "inclination",
                "ascending_node",
                "periapsis_argument",
            }
        )
