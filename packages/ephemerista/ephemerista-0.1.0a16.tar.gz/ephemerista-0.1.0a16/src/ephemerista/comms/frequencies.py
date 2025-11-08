"""Radio frequency modeling for communication systems.

This module provides the Frequency class for representing and working with radio frequencies
in telecommunications link budget calculations and interference analysis.
"""

import typing
from typing import Literal

import numpy as np
from pydantic import Field

from ephemerista import BaseModel

type Unit = Literal["Hz", "KHz", "MHz", "GHz", "THz"]

factors: dict[Unit, float] = {
    "Hz": 1,
    "KHz": 1e3,
    "MHz": 1e6,
    "GHz": 1e9,
    "THz": 1e12,
}

Band = Literal["HF", "VHF", "UHF", "L", "S", "C", "X", "Ku", "K", "Ka", "V", "W"]

BAND_NAMES = typing.get_args(Band)

BAND_FREQS = np.array([3e6, 30e6, 300e6, 1e9, 2e9, 4e9, 8e9, 12e9, 18e9, 27e9, 40e9, 75e9, 110e9])


class Frequency(BaseModel):
    """Represents a radio frequency with unit conversion and band identification.

    The Frequency class provides a convenient way to work with radio frequencies
    across different units (Hz, KHz, MHz, GHz, THz) and automatically identifies the
    corresponding frequency band (HF, VHF, UHF, L, S, C, X, Ku, K, Ka, V, W).

    Attributes
    ----------
    unit : {"KHz", "MHz", "GHz", "THz"}, default: "GHz"
        The unit of the radio frequency.
    value : float, default: 20.0
        The numerical value of the radio frequency in the specified unit.

    Examples
    --------
    Create a frequency using the constructor:

    >>> freq = Frequency(value=2.4, unit="GHz")
    >>> freq.hertz
    2400000000.0

    Create a frequency with the default unit (Hz):

    >>> freq = Frequency(5000)
    >>> freq.value
    5000.0
    >>> freq.unit
    'Hz'

    Create frequencies using class methods:

    >>> freq = Frequency.megahertz(2308.0)
    >>> freq.value
    2308.0
    >>> freq.unit
    'MHz'

    Identify frequency bands:

    >>> x_band = Frequency.gigahertz(10.0)
    >>> x_band.band
    'X'
    >>> ka_band = Frequency.gigahertz(30.0)
    >>> ka_band.band
    'Ka'
    """

    unit: Unit = Field(default="Hz", description="The unit of the radio frequency")
    value: float = Field(description="The numerical value of the radio frequency")

    def __init__(self, value: float | None = None, **kwargs):
        super().__init__(**dict(value=value, **kwargs))

    def __hash__(self) -> int:
        """Return a hash value for the frequency.

        Returns
        -------
        int
            The hash value of the frequency.
        """
        return hash(self.hertz)

    def __eq__(self, other: object) -> bool:
        """Check if two frequencies are equal.

        Parameters
        ----------
        other : object
            The other frequency to compare.

        Returns
        -------
        bool
            True if the frequencies are equal, False otherwise.
        """
        if not isinstance(other, Frequency):
            return NotImplemented
        return self.hertz == other.hertz

    @property
    def hertz(self) -> float:
        """Convert the frequency to Hertz.

        Returns
        -------
        float
            The frequency value in Hertz.
        """
        return self.value * factors[self.unit]

    @classmethod
    def kilohertz(cls, value: float) -> "Frequency":
        """Create a Frequency instance with value in kilohertz.

        Parameters
        ----------
        value : float
            The frequency value in kilohertz.

        Returns
        -------
        Frequency
            A Frequency instance with the specified value in KHz.
        """
        return cls(value=value, unit="KHz")

    @classmethod
    def megahertz(cls, value: float) -> "Frequency":
        """Create a Frequency instance with value in megahertz.

        Parameters
        ----------
        value : float
            The frequency value in megahertz.

        Returns
        -------
        Frequency
            A Frequency instance with the specified value in MHz.
        """
        return cls(value=value, unit="MHz")

    @classmethod
    def gigahertz(cls, value: float) -> "Frequency":
        """Create a Frequency instance with value in gigahertz.

        Parameters
        ----------
        value : float
            The frequency value in gigahertz.

        Returns
        -------
        Frequency
            A Frequency instance with the specified value in GHz.
        """
        return cls(value=value, unit="GHz")

    @classmethod
    def terahertz(cls, value: float) -> "Frequency":
        """Create a Frequency instance with value in terahertz.

        Parameters
        ----------
        value : float
            The frequency value in terahertz.

        Returns
        -------
        Frequency
            A Frequency instance with the specified value in THz.
        """
        return cls(value=value, unit="THz")

    @property
    def band(self) -> Band | None:
        """Identify the frequency band for this frequency.

        Returns the standard frequency band designation based on the frequency value.

        The bands are defined as:

        * HF: 3-30 MHz (High Frequency)
        * VHF: 30-300 MHz (Very High Frequency)
        * UHF: 300 MHz - 1 GHz (Ultra High Frequency)
        * L: 1-2 GHz
        * S: 2-4 GHz
        * C: 4-8 GHz
        * X: 8-12 GHz
        * Ku: 12-18 GHz
        * K: 18-27 GHz
        * Ka: 27-40 GHz
        * V: 40-75 GHz
        * W: 75-110 GHz

        Returns
        -------
        {"HF", "VHF", "UHF", "L", "S", "C", "X", "Ku", "K", "Ka", "V", "W"} or None
            The band designation as a string, or None if the frequency
            is below 3 MHz or above 110 GHz.

        Examples
        --------
        >>> Frequency.megahertz(100).band
        'VHF'
        >>> Frequency.gigahertz(2.4).band
        'S'
        >>> Frequency.gigahertz(30).band
        'Ka'
        """
        freq_hz = self.hertz
        if freq_hz < BAND_FREQS[0] or freq_hz > BAND_FREQS[-1]:
            return None
        return BAND_NAMES[np.flatnonzero(BAND_FREQS <= freq_hz)[-1]]
