"""The utils.py module.

This module provides various utilities and physical constants for link budget calculations.
"""

import math
from typing import overload

import numpy as np
from numpy.typing import ArrayLike

from ephemerista.comms.frequencies import Frequency

"""The Boltzmann constant"""
BOLTZMANN_CONSTANT: float = 1.38064852e-23  # J/K

"""Average room temperature in K"""
ROOM_TEMPERATURE = 290  # K

"""The speed of light in vacuum in m/s"""
SPEED_OF_LIGHT_VACUUM: float = 2.99792458e8  # m/s


def wavelength(frequency: float | Frequency) -> float:
    """Return the wavelength of electromagnetic radiation of a given frequency."""
    freq_hz = frequency.hertz if isinstance(frequency, Frequency) else frequency
    return SPEED_OF_LIGHT_VACUUM / freq_hz


@overload
def to_db(val: float) -> float: ...


@overload
def to_db(val: ArrayLike) -> ArrayLike: ...


def to_db(val: ArrayLike | float) -> ArrayLike | float:
    """Convert a given value to decibel."""
    return 10 * np.log10(val)


@overload
def from_db(val: float) -> float: ...


@overload
def from_db(val: np.ndarray) -> np.ndarray: ...


def from_db(val: np.ndarray | float) -> np.ndarray | float:
    """Convert from decibel."""
    return 10 ** (val / 10)


def free_space_path_loss(distance: float, frequency: float | Frequency) -> float:
    """Calculate the free-space path loss for a given frequency and distance.

    Parameters
    ----------
    distance : float
        Distance in km
    frequency : Union[float, Frequency]
        Frequency in Hz or Frequency object


    Returns
    -------
    float
        Free-space path loss in dB
    """
    return to_db((4 * math.pi * distance * 1e3 / wavelength(frequency)) ** 2)
