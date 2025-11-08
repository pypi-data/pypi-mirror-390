"""The events.py module.

This module provides the `StoppingEvent` class.
"""

from enum import Enum, auto


class StoppingEvent(Enum):
    """Enum for stopping Orekit-based propagators at apsis passed."""

    PERIAPSIS = auto()
    APOAPSIS = auto()
