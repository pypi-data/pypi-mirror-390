"""The events.py module.

This module provides event detectors.
"""

from __future__ import annotations

import abc
from typing import Literal

from pydantic import Field

from ephemerista import BaseModel
from ephemerista.assets import GroundStation
from ephemerista.coords.trajectories import Event, Trajectory
from ephemerista.coords.twobody import Cartesian


class EventDetector(abc.ABC):
    """Abstract base class for event detectors."""

    @abc.abstractmethod
    def callback(self, s: Cartesian) -> float:
        """Return zero at the event."""
        raise NotImplementedError()

    def filtr(self, events: list[Event]) -> list[Event]:
        """Override this method to filter events after detection."""
        return events

    def detect(self, trajectory: Trajectory) -> list[Event]:
        """Detect all events on the provided trajectory."""
        return self.filtr(trajectory.find_events(lambda s: self.callback(s)))


class ApsisDetector(BaseModel, EventDetector):
    """The ApsisDetector class.

    This event detector finds apsis passes.
    """

    apsis: Literal["periapsis", "apoapsis"] | None = Field(default=None)

    def callback(self, s: Cartesian) -> float:
        """Return zero when passing apoapsis or periapsis."""
        return s.position @ s.velocity  # type: ignore

    def filtr(self, events: list[Event]) -> list[Event]:
        """Filter events based on the provided apsis type."""
        if self.apsis == "periapsis":
            return [e for e in events if e.crossing == "up"]
        elif self.apsis == "apoapsis":
            return [e for e in events if e.crossing == "down"]
        return events


class ElevationDetector(BaseModel, EventDetector):
    """The ElevationDetector class.

    This event detector finds when the elevation at a certain ground location rises above a threshold.
    """

    ground_station: GroundStation

    def callback(self, s: Cartesian) -> float:
        """Return zero when elevation rises above minimum elevation."""
        return self.ground_station.observables(s).elevation.radians - self.ground_station.minimum_elevation.radians
