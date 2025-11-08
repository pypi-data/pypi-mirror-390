"""The `propagators` package provides several different semi-analytical and numerical orbit propagators."""

import abc
from typing import overload

from ephemerista import BaseModel
from ephemerista.coords.trajectories import Trajectory
from ephemerista.coords.twobody import Cartesian
from ephemerista.propagators.events import StoppingEvent
from ephemerista.time import Time


class Propagator(BaseModel, abc.ABC):
    """Abstract base class for propagators."""

    @overload
    @abc.abstractmethod
    def propagate(self, time: Time) -> Cartesian: ...

    @overload
    @abc.abstractmethod
    def propagate(self, time: list[Time]) -> Trajectory: ...

    @overload
    @abc.abstractmethod
    def propagate(self, time: Time, stop_conds: list[StoppingEvent] | None = None) -> Cartesian: ...

    @overload
    @abc.abstractmethod
    def propagate(self, time: list[Time], stop_conds: list[StoppingEvent] | None = None) -> Trajectory: ...

    @abc.abstractmethod
    def propagate(
        self,
        time: Time | list[Time],
        stop_conds: list[StoppingEvent] | None = None,
    ) -> Cartesian | Trajectory:
        """
        Propagate the state.

        Parameters
        ----------
        time: Time | list[Time]
            Either a single `Time` or a list of `Time`s.

        Returns
        -------
        Cartesian | Trajectory
            Either a single `Cartesian` state for a discrete input or a `Trajectory` for a list.
        """
        pass
