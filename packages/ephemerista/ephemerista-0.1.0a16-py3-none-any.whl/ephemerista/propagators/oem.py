"""The oem.py module.

This module provides the `OEMPropagator` class.
"""

import tempfile
from typing import Literal

import lox_space as lox
from pydantic import Field, PrivateAttr

from ephemerista.coords.trajectories import Trajectory
from ephemerista.coords.twobody import Cartesian
from ephemerista.propagators import Propagator
from ephemerista.propagators.orekit.ccsds import parse_oem
from ephemerista.time import Time


class OEMPropagator(Propagator):
    """The `OEMPropagator` interpolates a precomputed trajectory to return the requested state vectors."""

    propagator_type: Literal["oem"] = Field(
        default="oem", frozen=True, repr=False, alias="type", description="The type of the propagator"
    )
    filename: str = Field(description="Name of the OEM file.")
    content: str = Field(description="Content of the OEM file.")
    time_step: float = Field(default=60)
    _trajectory: Trajectory = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(self.content.encode())
            self._trajectory = parse_oem(tmp.name, self.time_step)

    def propagate(self, time: Time | list[Time]) -> Cartesian | Trajectory:  # type: ignore
        """
        Propagate the state.

        Parameters
        ----------
        time : Time or list of Time
            Either a single Time or a list of Times.

        Returns
        -------
        Cartesian or Trajectory
            Either a single Cartesian state for a discrete input or a Trajectory for a list.
        """
        if isinstance(time, Time):
            return self._trajectory.interpolate(time)
        else:
            states = [self._trajectory._trajectory.interpolate(t._time) for t in time]
            return Trajectory._from_lox(lox.Trajectory(states))
