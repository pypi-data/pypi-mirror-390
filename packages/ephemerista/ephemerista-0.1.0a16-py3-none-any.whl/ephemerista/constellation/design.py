"""The design.py module.

This module provides several classes for modelling various types of satellite constellations.
"""

import abc
import uuid
from functools import cached_property
from typing import Literal, Self

import numpy as np
import pandas as pd
import scipy
import scipy.optimize
from pydantic import UUID5, Field, PrivateAttr, computed_field

from ephemerista import BaseModel
from ephemerista.assets import Asset, Spacecraft
from ephemerista.bodies import Origin
from ephemerista.comms.systems import CommunicationSystem
from ephemerista.constellation.plane import Plane
from ephemerista.coords.twobody import DEFAULT_ORIGIN, Keplerian
from ephemerista.math import normalize_two_pi
from ephemerista.propagators.orekit import OrekitPropagatorParams
from ephemerista.propagators.orekit.numerical import NumericalPropagator
from ephemerista.propagators.orekit.semianalytical import SemiAnalyticalPropagator
from ephemerista.time import Time
from ephemerista.uuid_utils import generate_constellation_uuid

DEFAULT_PLANET: Literal["earth"] = "earth"


class AbstractConstellation(BaseModel, abc.ABC):  # noqa: PLW1641
    """Abstract base class for all constellation types."""

    inclination: float = Field(ge=0, description="Inclination, in degrees")
    periapsis_argument: float = Field(ge=0, description="Argument of Perigee, in degrees")
    name: str = Field(default="My Constellation", description="Name of the Constellation")
    origin: Origin = Field(
        default=DEFAULT_ORIGIN,
        description="Origin of the coordinate system",
    )
    time: Time = Field(description="Epoch of the constellation")

    #  Define private attributes for future gets
    _satellites: dict[str, Keplerian] = PrivateAttr()

    def model_post_init(self, __context):  # noqa: D102
        # Initialise private attributes for future gets
        self._satellites = {}

    def __eq__(self, other: Self) -> bool:
        """Compare the constellation to another for equality."""
        rules = [
            self.time == other.time,
            len(self.satellites) == len(other.satellites),
        ]
        rules += [self.satellites[i] == other.satellites[i] for i in range(0, len(self.satellites))]
        return all(rules)

    @computed_field(description="Inclination in radians")
    @property
    def inclination_radians(self) -> float:
        return np.radians(self.inclination)

    @computed_field(description="List of Keplerian elements of the satellites")
    @cached_property
    def satellites(self) -> dict[str, Keplerian]:
        """Method to return the satellites to the user, with results cached for future gets."""
        return self.define_satellites()

    @abc.abstractmethod
    def define_satellites(self) -> dict[str, Keplerian]:
        """Return a list of Keplerian objects that define the constellation's satellites."""
        pass

    def to_dataframe(self, data: str = "satellites") -> pd.DataFrame:
        """Return a dataframe of the Keplerian elements of each satellite.

        Parameters
        ----------
        data : str, optional
            Flag to return plane or satellite data. Defaults to "satellites"

        Returns
        -------
        pd.DataFrame
            Dataframe of Keplerian elements of each satellite
        """
        if data.lower() == "satellites":
            # Flatten values into a single list
            return pd.concat([sc.to_dataframe(name) for name, sc in self.satellites.items()])
        else:
            msg = "Data requested should be 'satellites'"
            raise ValueError(msg)


class AbstractWalkerOrSocConstellation(AbstractConstellation, abc.ABC):
    """Abstract base class for Walker or streets-of-coverage constellations."""

    nsats: int = Field(gt=0, description="Number of satellites in the constellation")
    nplanes: int = Field(gt=0, description="Number of orbital planes in the constellation")
    semi_major_axis: float = Field(gt=0, description="Semi major axis, in km")
    eccentricity: float = Field(ge=0, description="Eccentricity")

    # Define private attributes for easier computation
    _planes: dict[int, Plane] = PrivateAttr()
    _sats_per_plane: int = PrivateAttr()

    def model_post_init(self, __context):  # noqa: D102
        if self.nsats % self.nplanes != 0:
            msg = "The number of satellites per plane must be a multiple of the number of planes for a constellation."
            raise ValueError(msg)
        self._planes = {}
        self._sats_per_plane = self.nsats // self.nplanes

        valid, reason = Keplerian.is_physical(
            semi_major_axis=self.semi_major_axis,
            eccentricity=self.eccentricity,
            inclination=self.inclination,
            periapsis_argument=self.periapsis_argument,
            origin=self.origin,
        )
        if not valid:
            error_message = f"The constellation is not physical: {reason}"
            raise ValueError(error_message)

    @computed_field(description="Orbit elements of the orbit planes")
    @property
    def planes(self) -> dict[int, Plane]:
        """Method to return the planes to the user, with results cached for future gets."""
        if not hasattr(self, "_planes"):
            self._planes = self.define_planes()
        return self._planes

    @abc.abstractmethod
    def define_planes(self) -> dict[int, Plane]:
        """Return a list of Plane objects that define the constellation."""
        pass

    def to_dataframe(self, data: str = "planes") -> pd.DataFrame:
        """Return a data frame of the constellation parameters.

        This will either be the Keplerian elements of each plane in the constellation, or the satellites in each plane,
        depending on the input.

        Parameters
        ----------
        data : str, optional
            Flag to return plane or satellite data. Defaults to "planes"

        Returns
        -------
        pd.DataFrame
            Dataframe of Keplerian elements of each constellation,
            or the satellites in each plane, depending on the input
        """
        if data.lower() == "planes":
            return pd.concat([pd.DataFrame.from_records([p.elements]) for p in self.planes.values()], ignore_index=True)
        if data.lower() == "satellites":
            return super().to_dataframe("satellites")
        else:
            msg = "Data requested should be 'planes' or 'satellites'"
            raise ValueError(msg)


class AbstractWalker(AbstractWalkerOrSocConstellation, abc.ABC):
    """Abstract base class for Walker Star or Delta constellations."""

    phasing: int = Field(default=0, ge=0, description="Phasing between satellites in adjacent planes")
    _raan_spacing: float = PrivateAttr()
    _anomaly_spacing: float = PrivateAttr()
    _anomaly_phasing: float = PrivateAttr()  # Additional anomaly offset between adjacent planes

    def model_post_init(self, __context):  # noqa: D102
        super().model_post_init(__context)

        if self.phasing >= self.nplanes:
            msg = "Phasing must be lower than the number of planes"
            raise ValueError(msg)

        self._anomaly_spacing = 360 / self._sats_per_plane
        self._planes = self.define_planes()
        self._satellites = self.define_satellites()

    def define_planes(self) -> dict[int, Plane]:
        """Generate constellation planes based on the user-provided parameters."""
        planes = {}

        for p in range(self.nplanes):
            ascending_node = p * self._raan_spacing

            # Initialise planes equally spaced in raan
            planes.update(
                {
                    p + 1: Plane(
                        plane_id=p + 1,
                        inclination=self.inclination,
                        ascending_node=ascending_node,
                        semi_major_axis=self.semi_major_axis,
                        eccentricity=self.eccentricity,
                        periapsis_argument=self.periapsis_argument,
                        number_of_satellites=self._sats_per_plane,
                        primary_body=self.origin,
                    )
                }
            )
        return planes

    def define_satellites(self) -> dict[str, Keplerian]:
        """Generate constellation satellites based on the user-provided parameters."""
        satellites = {}

        for p in range(self.nplanes):
            ascending_node = p * self._raan_spacing

            for j in range(self._sats_per_plane):
                arg_latitude = j * self._anomaly_spacing + 2 * p * self._anomaly_phasing
                while arg_latitude > 180.0:  # noqa: PLR2004
                    arg_latitude -= 360.0

                # This is satellite number (j), divided by the total satellites per plane, multiplied by 2pi
                satellites[f"Plane {p + 1} Sat {j + 1}"] = Keplerian.from_elements(
                    time=self.time,
                    semi_major_axis=self.semi_major_axis,
                    eccentricity=self.eccentricity,
                    inclination=self.inclination,
                    periapsis_argument=self.periapsis_argument,
                    ascending_node=ascending_node,
                    anomaly=arg_latitude,  # Spread satellites evenly in argument of latitude, starting at 0 deg.
                    origin=self.origin,
                )

        return satellites


class WalkerStar(AbstractWalker):
    """The `WalkerStar` class.

    This class models a Walker Star constellation.
    """

    constellation_type: Literal["walker_star"] = Field(
        default="walker_star", frozen=True, repr=False, alias="type", description="The type of constellation"
    )

    def model_post_init(self, __context):  # noqa: D102
        self._raan_spacing = (360 / 2) / self.nplanes
        self._anomaly_phasing = (
            self.phasing * 180 / self.nsats
        )  # https://uk.mathworks.com/help/aerotbx/ug/satellitescenario.walkerstar.html#mw_fb3f83e6-67c5-4ff5-b6f8-c4a4e65f6a78

        # Here the super is called at the end because AbstractWalker's constructor needs to know the _raan_spacing value
        super().model_post_init(__context)


class WalkerDelta(AbstractWalker):
    """The `WalkerDelta` class.

    This class models a Walker Delta constellation.
    """

    constellation_type: Literal["walker_delta"] = Field(
        default="walker_delta", frozen=True, alias="type", description="The type of constellation"
    )

    def model_post_init(self, __context):  # noqa: D102
        self._raan_spacing = 360 / self.nplanes
        self._anomaly_phasing = (
            self.phasing * 180 / self.nsats
        )  # https://de.mathworks.com/help/aerotbx/ug/satellitescenario.walkerdelta.html#mw_badf1acd-4f40-4ad6-987e-c7d35ae2368c

        # Here the super is called at the end because AbstractWalker's constructor needs to know the _raan_spacing value
        super().model_post_init(__context)


def c_j(nu: float, s: float, j: int) -> float:
    """
    Compute the minimum half-width of Street-of-Coverage required for j-fold continuous global coverage.

    :param nu: Central angle of coverage in radians, variable that will be optimized
    :param s: number of satellites per plane
    :param j: coverage fold

    Ref: Equation 3 of [1]
    """
    return np.arccos(np.cos(nu) / np.cos(j * np.pi / s))


class StreetOfCoverage(AbstractWalkerOrSocConstellation):
    """
    The `StreetOfCoverage` class.

    This class models a streets-of-coverage constellation.

    References
    ----------
    [1] S. Huang, C. Colombo, and F. Bernelli-Zazzera,
      “Multi-criteria design of continuous global coverage Walker and Street-of-Coverage constellations through property assessment”
      Acta Astronautica, vol. 188, pp. 151-170, Nov. 2021,
      doi: 10.1016/j.actaastro.2021.07.002.
    """  # noqa: E501

    constellation_type: Literal["street_of_coverage"] = Field(
        default="street_of_coverage", frozen=True, repr=False, alias="type", description="The type of constellation"
    )

    j: int = Field(
        default=1,
        ge=1,
        le=4,
        alias="coverage_fold",
        description="Number of satellites that must provide simultaneous coverage of a ground location",
    )
    _nu_optimal_rad: float | None = PrivateAttr(default=None)  # Optimal central angle of coverage in radians

    def model_post_init(self, __context):  # noqa: D102
        super().model_post_init(__context)

        if self.j * self.nplanes * (self.nplanes - 1) > self.nsats:
            # Ref: Equation 11 of [1]
            msg = f"This Street-of-Coverage constellation has too little satellites to provide {self.j}-fold coverage"
            raise ValueError(msg)
        elif np.sin(self.inclination_radians) < 1e-9:  # noqa: PLR2004
            msg = "A Street-of-Coverage constellation cannot be used for equatorial orbits"
            raise ValueError(msg)

        self._nu_optimal_rad = self._optimize_nu()
        self._planes = self.define_planes()
        self._satellites = self.define_satellites()

    def get_nu_bounds(self) -> tuple[float, float]:
        """Compute initial bounds of the central angle of coverage in radians."""
        nu_min = self.j * np.pi / self._sats_per_plane  # Ref: Eq (7) of [1]
        nu_max = np.pi / 2
        return (nu_min, nu_max)

    @staticmethod
    def _nu_to_minimize(nu: float, p: float, s: float, j: int, i: float) -> float:
        """
        Return current nu value.

        Function to be used in a minimizer to compute the optimal nu value for optimal coverage.

        :param nu: Central angle of coverage in radians, variable that will be optimized
        :param p: number of planes
        :param s: number of satellites per plane
        :param j: coverage fold
        :param i: inclination in radians

        Ref: Equation 37 of [1]
        """
        c_j_theta = c_j(nu, s, j)
        c_1_theta = c_j(nu, s, 1)
        sin_i = np.sin(i)
        return np.fabs(
            (p - 1) * np.arcsin(np.sin((nu + c_j_theta) / 2) / sin_i)
            - np.arcsin(np.sin((np.pi - c_1_theta - c_j_theta) / 2) / sin_i)
        )

    def _optimize_nu(self) -> float:
        """Compute the optimal nu (Central angle of coverage) value for optimal coverage."""
        res = scipy.optimize.minimize_scalar(
            self._nu_to_minimize,
            bounds=self.get_nu_bounds(),
            args=(self.nplanes, self._sats_per_plane, self.j, self.inclination_radians),
            options={"maxiter": 100, "xatol": 1e-6},
        )
        if not res.success:
            msg = "Not able to compute the central angle of coverage"
            raise ValueError(msg)
        return res.x

    def _raan_spacing_co_rotating(self) -> float:
        """Ref: Equation 2 of [1]."""
        nu = self._nu_optimal_rad
        s = self._sats_per_plane
        i = self.inclination_radians
        return 2 * np.arcsin(np.sin((nu + c_j(nu, s, self.j)) / 2) / np.sin(i))

    def _raan_spacing_counter_rotating(self) -> float:
        """Ref: Equation 2 of [1]."""
        nu = self._nu_optimal_rad
        s = self._sats_per_plane
        i = self.inclination_radians
        return 2 * np.arcsin(np.sin((np.pi - c_j(nu, s, 1) - c_j(nu, s, self.j)) / 2) / np.sin(i))

    def _anom_spacing_intra_plane(self) -> float:
        """Ref: Equation 5 of [1]."""
        return 2 * np.pi / self._sats_per_plane

    def _anom_spacing_inter_plane(self) -> float:
        """Ref: Equation 6 of [1]."""
        nu = self._nu_optimal_rad
        s = self._sats_per_plane
        return self.j * np.pi / s - 2 * np.arccos(
            np.cos(self._raan_spacing_co_rotating() / 2) / np.cos((nu + c_j(nu, s, self.j)) / 2)
        )

    def _raan_array_deg(self) -> list[float]:
        delta_raan_co = np.rad2deg(self._raan_spacing_co_rotating())
        return [i * delta_raan_co for i in range(self.nplanes)]

    def define_planes(self) -> dict[int, Plane]:
        """Return a list of Plane objects that define the constellation."""
        """Using the user defined constellation inputs (number of satellites, number of planes, keplerian elements etc.)
        generates Plane objects to fully define the constellation.
        """
        planes = {}

        raan_array = self._raan_array_deg()
        for p in range(self.nplanes):
            planes.update(
                {
                    p + 1: Plane(
                        plane_id=p + 1,
                        inclination=self.inclination,
                        ascending_node=raan_array[p],
                        semi_major_axis=self.semi_major_axis,
                        eccentricity=self.eccentricity,
                        periapsis_argument=self.periapsis_argument,
                        number_of_satellites=self._sats_per_plane,
                        primary_body=self.origin,
                    )
                }
            )
        return planes

    def define_satellites(self) -> dict[str, Keplerian]:
        """Return a list of Keplerian objects that define the constellation's satellites."""
        satellites = {}

        raan_array = self._raan_array_deg()
        for p in range(self.nplanes):
            for k in range(self._sats_per_plane):
                arg_latitude = np.rad2deg(k * self._anom_spacing_intra_plane() + p * self._anom_spacing_inter_plane())
                while arg_latitude > 180.0:  # noqa: PLR2004
                    arg_latitude -= 360.0

                satellites[f"Plane {p + 1} Sat {k + 1}"] = Keplerian.from_elements(
                    time=self.time,
                    semi_major_axis=self.semi_major_axis,
                    eccentricity=self.eccentricity,
                    inclination=self.inclination,
                    periapsis_argument=self.periapsis_argument,
                    ascending_node=raan_array[p],
                    anomaly=arg_latitude,
                    origin=self.origin,
                )

        return satellites


class Flower(AbstractConstellation):
    """
    The `Flower` class.

    This class models a Flower constellation.

    References
    ----------
    [1] M. P. Wilkins, The Flower Constellations: Theory, design process, and applications.
    Texas A&M University, 2004.
    https://search.proquest.com/openview/d2a1245a4defb3f086c797b56e1a5b22/1?pq-origsite=gscholar&cbl=18750&diss=y

    [2] https://gitlab.com/open-galactic/satellite-constellation
    """

    constellation_type: Literal["flower"] = Field(
        default="flower", frozen=True, repr=False, alias="type", description="The type of constellation"
    )

    perigee_altitude: float = Field(gt=0, description="Perigee altitude, in km")
    n_petals: int = Field(gt=0, description="Number of petals")
    n_days: int = Field(gt=0, description="Number of sidereal days for the constellation to repeat its ground track")
    nsats: int = Field(gt=0, description="Desired number of satellites in the constellation")
    phasing_n: int = Field(gt=0, description="n phasing parameter")
    phasing_d: int = Field(gt=0, description="d phasing parameter")

    _nsats_max: int = PrivateAttr()
    _raan_spacing: float = PrivateAttr()
    _anomaly_spacing: float = PrivateAttr()
    _semi_major_axis: float = PrivateAttr()  # [km]
    _eccentricity: float = PrivateAttr()

    _earth_ang_vel: float = PrivateAttr(7.2921159e-5)  # Earth angular velocity in rad/s

    def model_post_init(self, __context):  # noqa: D102
        super().model_post_init(__context)

        self._nsats_max = self.phasing_d * self.n_days
        self._define_spacing()
        self._define_orbit_params()

    def _define_spacing(self):
        self._raan_spacing = -360.0 * self.phasing_n / self.phasing_d
        self._anomaly_spacing = -self._raan_spacing * self.n_petals / self.n_days

        if abs(self._raan_spacing) > 360.0:  # noqa: PLR2004
            self._raan_spacing = self._raan_spacing % 360

        if abs(self._anomaly_spacing) > 360.0:  # noqa: PLR2004
            self._anomaly_spacing = self._anomaly_spacing % 360

    def _define_orbit_params(self):
        # First, compute orbit period
        T = (2 * np.pi / self._earth_ang_vel) * self.n_days / self.n_petals  # noqa: N806

        self._semi_major_axis = np.power(self.origin.gravitational_parameter * np.square(T / (2 * np.pi)), 1 / 3)

        self._eccentricity = 1.0 - (self.origin.mean_radius + self.perigee_altitude) / self._semi_major_axis

    def define_satellites(self) -> dict[str, Keplerian]:
        """Return a list of Keplerian objects that define the constellation's satellites."""
        satellites = {}

        for i_sat in range(self.nsats):
            ascending_node = normalize_two_pi(i_sat * self._raan_spacing, center=np.pi)
            mean_anomaly = normalize_two_pi(i_sat * self._anomaly_spacing)

            satellites[f"Sat {i_sat + 1}"] = Keplerian.from_elements(
                time=self.time,
                semi_major_axis=self._semi_major_axis,
                eccentricity=self._eccentricity,
                inclination=self.inclination,
                periapsis_argument=self.periapsis_argument,
                ascending_node=ascending_node,
                anomaly=mean_anomaly,
                anomaly_type="mean",
                origin=self.origin,
            )

        return satellites


type ConstellationType = WalkerStar | WalkerDelta | StreetOfCoverage | Flower


class Constellation(BaseModel):
    """The main class for modelling constellations."""

    constellation_id: UUID5 = Field(
        alias="id", default_factory=generate_constellation_uuid, description="Constellation UUID"
    )
    model: ConstellationType = Field(discriminator="constellation_type")
    name: str = Field(default="Default Constellation")
    propagator: Literal["semi-analytical", "numerical"] = Field(default="semi-analytical")
    params: OrekitPropagatorParams = Field(default=OrekitPropagatorParams())
    comms: list[CommunicationSystem] = Field(default=[])

    @property
    def assets(self) -> list[Asset]:
        """list[Asset]: list of spacecraft of the constellation."""
        propagator = NumericalPropagator if self.propagator == "numerical" else SemiAnalyticalPropagator
        assets = []
        for sat_name, k in self.model.satellites.items():
            # Generate deterministic UUID based on constellation ID and satellite name
            # This ensures the same satellite always gets the same UUID
            asset_id = uuid.uuid5(self.constellation_id, sat_name)
            # Include constellation name in the asset name
            full_name = f"{self.name} - {sat_name}"
            assets.append(
                Asset(
                    asset_id=asset_id,
                    model=Spacecraft(propagator=propagator(params=self.params, state_init=k)),
                    name=full_name,
                    comms=self.comms,
                    constellation_id=self.constellation_id,
                )
            )
        return assets
