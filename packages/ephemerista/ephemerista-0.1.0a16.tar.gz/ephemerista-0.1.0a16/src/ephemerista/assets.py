"""The assets.py module.

This module provides models for space and ground assets.
"""

import uuid
from typing import Literal, Self, overload

import lox_space as lox
import numpy as np
from pydantic import UUID5, Field, PrivateAttr

from ephemerista import BaseModel, eop_provider
from ephemerista.angles import Angle, Latitude, Longitude
from ephemerista.bodies import Origin
from ephemerista.comms.systems import CommunicationSystem
from ephemerista.coords.trajectories import Trajectory
from ephemerista.coords.twobody import Cartesian
from ephemerista.propagators.oem import OEMPropagator
from ephemerista.propagators.orekit.numerical import NumericalPropagator
from ephemerista.propagators.orekit.semianalytical import SemiAnalyticalPropagator
from ephemerista.propagators.sgp4 import SGP4
from ephemerista.time import Time
from ephemerista.uuid_utils import generate_asset_uuid

type Propagator = OEMPropagator | SGP4 | NumericalPropagator | SemiAnalyticalPropagator


class Spacecraft(BaseModel):
    """The ``Spacecraft`` model."""

    asset_type: Literal["spacecraft"] = Field(
        default="spacecraft", alias="type", repr=False, frozen=True, description="Spacecraft asset type"
    )
    propagator: Propagator = Field(discriminator="propagator_type", description="The orbit propagator")

    @overload
    def propagate(self, time: Time) -> Cartesian: ...

    @overload
    def propagate(self, time: list[Time]) -> Trajectory: ...

    def propagate(self, time: Time | list[Time]) -> Cartesian | Trajectory:
        """
        Propagate the spacecraft state.

        Parameters
        ----------
        time : Time or list of Time
            Either a single Time or a list of Times.

        Returns
        -------
        Cartesian or Trajectory
            Either a single Cartesian state for a discrete input or a Trajectory for a list.
        """
        return self.propagator.propagate(time)


class Observables(BaseModel):
    """The ``Observables`` model.

    This class models a single observation of a spacecraft from a ground station.
    """

    azimuth: Angle = Field(description="Azimuth angle in degrees")
    elevation: Angle = Field(description="Elevation angle in degrees")
    rng: float = Field(description="Range in km")
    rng_rate: float = Field(description="Range rate in km/s")

    @classmethod
    def _from_lox(cls, obs: lox.Observables) -> Self:
        return cls(
            azimuth=Angle.from_radians(obs.azimuth()),
            elevation=Angle.from_radians(obs.elevation()),
            rng=obs.range(),
            rng_rate=obs.range_rate(),
        )


class GroundLocation(BaseModel):
    """The ``GroundLocation`` model."""

    body: Origin = Field(default=Origin(name="Earth"), description="Central body of the ground station")
    longitude: Longitude = Field(description="Longitude")
    latitude: Latitude = Field(description="Latitude")
    altitude: float = Field(default=0, description="Altitude in meters")
    minimum_elevation: Angle | tuple[list[Angle], list[Angle]] = Field(
        default=Angle.from_degrees(0),
        description="Minimum elevation in radians or an elevation mask in SEZ frame with azimuth in the range [-pi,pi]",
    )
    polygon_ids: list[int] = Field(
        default=[], description="IDs of the polygon this point belongs to. Can be multiple in case of a grid"
    )
    _location: lox.GroundLocation = PrivateAttr()
    _mask: lox.ElevationMask = PrivateAttr()

    def __init__(self, location: lox.GroundLocation | None = None, mask: lox.ElevationMask | None = None, **data):
        super().__init__(**data)

        if not location:
            self._location = lox.GroundLocation(
                self.body._origin,
                self.longitude.radians,
                self.latitude.radians,
                self.altitude,
            )
        else:
            self._location = location

        if not mask:
            if isinstance(self.minimum_elevation, Angle):
                self._mask = lox.ElevationMask.fixed(self.minimum_elevation.radians)
            else:
                azimuth = np.array([az.radians for az in self.minimum_elevation[0]])
                elevation = np.array([el.radians for el in self.minimum_elevation[1]])
                self._mask = lox.ElevationMask.variable(azimuth, elevation)
        else:
            self._mask = mask

    @classmethod
    def from_lla(cls, longitude: float, latitude: float, **data) -> Self:
        """Construct a `GroundLocation` from geodetic coordinates."""
        return cls(
            longitude=Longitude.from_degrees(longitude),
            latitude=Latitude.from_degrees(latitude),
            **data,
        )

    def get_minimum_elevation(self, azimuth: float) -> float:
        """Return the minimum elevation for a given azimuth."""
        return self._mask.min_elevation(azimuth)

    def observables(self, target: Cartesian) -> Observables:
        """Return the modelled observables for a given spacecraft state."""
        obs = self._location.observables(target._cartesian)
        return Observables._from_lox(obs)

    def observables_batch(self, targets: list[Cartesian]) -> list[Observables]:
        """Return the modelled observables for multiple spacecraft states.

        Parameters
        ----------
        targets : list[Cartesian]
            List of spacecraft states

        Returns
        -------
        list[Observables]
            List of observables for each target state
        """
        return [self.observables(target) for target in targets]

    @overload
    def propagate(self, time: Time) -> Cartesian: ...

    @overload
    def propagate(self, time: list[Time]) -> Trajectory: ...

    def propagate(self, time: Time | list[Time]) -> Cartesian | Trajectory:
        """
        Propagate the ground station state.

        Parameters
        ----------
        time : Time or list of Time
            Either a single Time or a list of Times.

        Returns
        -------
        Cartesian or Trajectory
            Either a single Cartesian state for a discrete input or a Trajectory for a list.
        """
        propagator = lox.GroundPropagator(self._location, eop_provider())
        if isinstance(time, Time):
            return Cartesian._from_lox(propagator.propagate(time._time))
        else:
            return Trajectory._from_lox(propagator.propagate([time._time for time in time]), "groundstation")

    def rotation_to_topocentric(self) -> np.ndarray:
        """Return the rotation matrix to the SEZ frame."""
        return self._location.rotation_to_topocentric()


class GroundStation(GroundLocation):
    """The ``GroundStation`` model."""

    asset_type: Literal["groundstation"] = Field(
        default="groundstation", alias="type", repr=False, frozen=True, description="Ground station asset type"
    )


class Asset(BaseModel):
    """The ``Asset`` model.

    This class is composed of a `Spacecraft` or `GroundStation` model and adds additional
    metadata and subsystem models.
    """

    asset_id: UUID5 = Field(alias="id", default_factory=generate_asset_uuid, description="Asset UUID")
    name: str = Field(description="The name of the asset", default="Asset")
    model: Spacecraft | GroundStation = Field(discriminator="asset_type", description="Underlying model of the asset")
    comms: list[CommunicationSystem] = Field(default=[], description="List of communication systems")
    tracked_object_ids: list[UUID5] = Field(
        default=[], description="List of asset IDs that this asset's antennas shall track"
    )
    tracked_constellation_ids: list[UUID5] = Field(
        default=[], description="List of constellation IDs that this asset shall track"
    )
    constellation_id: UUID5 | None = Field(
        default=None, description="ID of the constellation this asset belongs to (if any)"
    )
    pointing_error: float = Field(default=0.1, ge=0.0, description="Pointing error in degrees when tracking")

    def comms_by_channel_id(self, channel_id: UUID5) -> CommunicationSystem | None:
        """Return the comms system associated to a given channel."""
        return next((c for c in self.comms if channel_id in c.channels), None)

    def track(
        self,
        asset_ids: UUID5 | list[UUID5] | None = None,
        constellation_ids: UUID5 | list[UUID5] | None = None,
    ):
        """Track one or more assets and/or constellations.

        Parameters
        ----------
        asset_ids : UUID or list of UUID, optional
            Asset IDs to track
        constellation_ids : UUID or list of UUID, optional
            Constellation IDs to track
        """
        if asset_ids is not None:
            if isinstance(asset_ids, uuid.UUID | str):
                asset_ids = [asset_ids]
            self.tracked_object_ids = asset_ids
        else:
            self.tracked_object_ids = []

        if constellation_ids is not None:
            if isinstance(constellation_ids, uuid.UUID | str):
                constellation_ids = [constellation_ids]
            self.tracked_constellation_ids = constellation_ids
        else:
            self.tracked_constellation_ids = []

    def is_tracking(self, asset_id: UUID5) -> bool:
        """Check if this asset is tracking the given asset ID directly."""
        return asset_id in self.tracked_object_ids


type AssetKey = UUID5 | Asset


def _asset_id(asset: AssetKey) -> UUID5:
    if isinstance(asset, Asset):
        return asset.asset_id
    elif isinstance(asset, uuid.UUID | str):
        return asset
