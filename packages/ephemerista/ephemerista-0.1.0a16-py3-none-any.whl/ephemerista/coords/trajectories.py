"""The trajectories.py module.

This module provides the `Trajectory` class.
"""

from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Literal, Self

import lox_space as lox
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pydantic_numpy.typing as pnd
from pydantic import Field, PrivateAttr, computed_field

from ephemerista import BaseModel, bodies, ephemeris
from ephemerista.coords.twobody import DEFAULT_FRAME, DEFAULT_ORIGIN, Cartesian
from ephemerista.frames import ReferenceFrame
from ephemerista.time import Scale, Time


class Event(BaseModel):
    """The `Event` class."""

    time: Time
    crossing: Literal["up", "down"]

    @classmethod
    def _from_lox(cls, event: lox.Event) -> Self:
        return cls(time=Time._from_lox(event.time()), crossing=event.crossing().lower())


class Trajectory(BaseModel):
    """Generic trajectory model."""

    trajectory_type: Literal["spacecraft", "groundstation", "ephemeris"] = Field(alias="type", default="spacecraft")
    start_time: Time
    origin: bodies.Origin = Field(
        default=DEFAULT_ORIGIN,
        description="Origin of the coordinate system",
    )
    frame: ReferenceFrame = Field(default=DEFAULT_FRAME, description="Reference frame of the coordinate system")
    states: pnd.Np2DArrayFp64
    attitude: list[tuple[float, float, float, float]] | None = Field(default=None)
    name: str | None = Field(default=None, description="Name of the asset")
    _trajectory: lox.Trajectory = PrivateAttr()

    def __init__(self, trajectory: lox.Trajectory | None = None, **data):
        super().__init__(**data)

        if not trajectory:
            self._trajectory = lox.Trajectory.from_numpy(
                self.start_time._time, self.states, self.origin._origin, self.frame._frame
            )
        else:
            self._trajectory = trajectory

    @classmethod
    def _from_lox(
        cls,
        trajectory: lox.Trajectory,
        trajectory_type: Literal["spacecraft", "groundstation", "ephemeris"] = "spacecraft",
    ) -> Self:
        states = trajectory.to_numpy()
        origin = bodies.Origin._from_lox(trajectory.origin())
        frame = ReferenceFrame._from_lox(trajectory.reference_frame())
        start_time = Time._from_lox(trajectory.states()[0].time())
        return cls(
            trajectory=trajectory,
            states=states,
            origin=origin,
            frame=frame,
            start_time=start_time,
            trajectory_type=trajectory_type,
        )

    @classmethod
    def from_csv(
        cls,
        path: str | Path,
        scale: Scale | Literal["UTC"] = "TAI",
        frame: ReferenceFrame = DEFAULT_FRAME,
        origin: bodies.Origin = DEFAULT_ORIGIN,
        **kwargs,
    ) -> Self:
        """Read a trajectory from a CSV file."""
        df = pd.read_csv(path, delimiter=",", **kwargs)
        states = np.empty((len(df), 7), dtype=np.float64)
        if scale == "UTC":
            start_time = Time.from_utc(df.iloc[0, 0])
        else:
            start_time = Time.from_iso(scale, df.iloc[0, 0])
        for i, row in df.iterrows():
            iso, *data = row.array
            if scale == "UTC":
                time = Time.from_utc(iso)
            else:
                time = Time.from_iso(scale, iso)
            states[i, 0] = float(time - start_time)
            states[i, 1:] = data

        return cls(states=states, start_time=start_time, frame=frame, origin=origin)

    @property
    def cartesian_states(self) -> list[Cartesian]:
        """List of states in the trajectory."""
        return [Cartesian._from_lox(s) for s in self._trajectory.states()]

    @computed_field
    @property
    def simulation_time(self) -> list[float]:
        """Array of simulation time steps."""
        return list(self.states[:, 0])  # type: ignore

    @property
    def times(self) -> list[Time]:
        """List of times in the trajectory."""
        return [s.time for s in self.cartesian_states]

    @property
    def datetimes(self) -> list[datetime]:
        """Return the time steps of the trajectory as a list of `datetime.datetime` objects."""
        return [t.datetime for t in self.times]

    def to_csv(self, path: str, **kwargs):
        """Write the trajectory to a CSV file."""
        df = pd.DataFrame(
            (
                (state.time.to_utc(), state.x, state.y, state.z, state.vx, state.vy, state.vz)
                for state in self.cartesian_states
            ),
            columns=["utc", "x", "y", "z", "vx", "vy", "vz"],
        )
        df.to_csv(path, index=False, **kwargs)

    def interpolate(self, time: Time) -> Cartesian:
        """
        Interpolates the state of the trajectory at a given time.

        Parameters
        ----------
        time: Time
            Time at which to interpolate the state

        Returns
        -------
        Cartesian
            Interpolated state of the trajectory
        """
        return Cartesian._from_lox(self._trajectory.interpolate(time._time))

    def interpolate_batch(self, times: list[Time]) -> list[Cartesian]:
        """
        Interpolates the state of the trajectory at multiple times.

        Parameters
        ----------
        times: list[Time]
            Times at which to interpolate the state

        Returns
        -------
        list[Cartesian]
            List of interpolated states
        """
        return [Cartesian._from_lox(self._trajectory.interpolate(t._time)) for t in times]

    def plot_3d(self) -> go.Scatter3d:
        """Plot a 3D representation of the trajectory."""
        scatter = go.Scatter3d(
            x=self.states[:, 1],
            y=self.states[:, 2],
            z=self.states[:, 3],
            mode="lines",
            name="Trajectory",
            hovertext=[t.to_utc() for t in self.times],
        )
        return scatter

    def find_events(self, func: Callable[[Cartesian], float]) -> list[Event]:
        """Find events along the trajectory.

        This method will find all zero-crossings of the provided callback function.
        """
        events = self._trajectory.find_events(lambda s: func(Cartesian._from_lox(s)))
        return [Event._from_lox(e) for e in events]

    def to_frame(self, frame: ReferenceFrame) -> "Trajectory":
        """Rotate all states of the trajectory to a different reference frame."""
        cartesian = self._trajectory.to_frame(frame._frame)
        return Trajectory._from_lox(cartesian)

    def to_origin(self, origin: bodies.Origin) -> "Trajectory":
        """Translate all states of the trajectory to a different coordinate origin."""
        cartesian = self._trajectory.to_origin(origin._origin, ephemeris())
        return Trajectory._from_lox(cartesian)
