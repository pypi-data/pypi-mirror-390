"""The transmitter.py module.

This module provides the `Transmitter` class which models a radio transmitter.
"""

from pydantic import Field

from ephemerista import BaseModel
from ephemerista.comms.antennas import Antenna
from ephemerista.comms.frequencies import Frequency
from ephemerista.comms.utils import to_db


class Transmitter(BaseModel):
    """The `Transmitter` class."""

    frequency: Frequency = Field(description="Operating frequency")
    power: float = Field(gt=0.0, description="Transmit power in W")
    line_loss: float = Field(ge=0.0, description="Line loss in dB")
    output_back_off: float = Field(ge=0.0, default=0.0, description="Power amplifier output back off in dB (optional)")

    def equivalent_isotropic_radiated_power(self, antenna: Antenna, angle: float) -> float:
        """Calculate the Equivalent Isotropic Radiated Power (EIRP) in dB."""
        return antenna.gain(self.frequency, angle) + to_db(self.power) - self.line_loss - self.output_back_off
