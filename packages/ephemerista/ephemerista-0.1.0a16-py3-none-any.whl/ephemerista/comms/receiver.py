"""The receiver.py module.

This module provides the `SimpleReceiver` and `ComplexReceiver`.
"""

import abc
from typing import Literal

from pydantic import Field

from ephemerista import BaseModel
from ephemerista.comms.antennas import Antenna
from ephemerista.comms.frequencies import Frequency
from ephemerista.comms.utils import ROOM_TEMPERATURE, from_db, to_db

DISCRIMINATOR = "receiver_type"


class Receiver(BaseModel, abc.ABC):
    """Abstract base class for receiver models."""

    frequency: Frequency = Field(description="Operating frequency")

    @abc.abstractmethod
    def total_gain(self, antenna: Antenna, angle: float) -> float:
        """Calculate the total gain of receiver and antenna."""
        raise NotImplementedError()

    @abc.abstractmethod
    def gain_to_noise_temperature(self, antenna: Antenna, angle: float) -> float:
        """Calculate the gain-to-noise temperature in dB/K."""
        raise NotImplementedError()


class SimpleReceiver(Receiver):
    """The `SimpleReceiver` class.

    This class models a receiver that is fully characterised by its system noise temperature.
    """

    receiver_type: Literal["simple"] = Field(
        default="simple", alias="type", repr=False, frozen=True, description="Simple receiver type"
    )
    system_noise_temperature: float = Field(gt=0.0, description="System noise temperature in K")

    def total_gain(self, antenna: Antenna, angle: float) -> float:
        """Calculate the total gain of receiver and antenna."""
        return antenna.gain(self.frequency, angle)

    def gain_to_noise_temperature(self, antenna: Antenna, angle: float) -> float:
        """Calculate the gain-to-noise temperature in dB/K."""
        return self.total_gain(antenna, angle) - to_db(self.system_noise_temperature)


class ComplexReceiver(Receiver):
    """The `ComplexReceiver` class.

    This class models a complex receiver with additional parameters for the receiving antenna and
    the low-noise amplifier.
    """

    receiver_type: Literal["complex"] = Field(
        default="complex", alias="type", repr=False, frozen=True, description="Complex receiver type"
    )
    antenna_noise_temperature: float = Field(gt=0.0, default=265, description="Antenna noise temperature in K")
    lna_gain: float = Field(gt=0.0, description="LNA gain in dB")
    lna_noise_figure: float = Field(ge=0.0, description="LNA noise figure in dB")
    noise_figure: float = Field(ge=0.0, description="Noise figure in dB")
    loss: float = Field(ge=0.0, description="Additional losses in dB")
    demodulator_loss: float = Field(
        ge=0.0, default=0.0, description="Demodulator loss in dB"
    )  # Only plays a role in the gain but not the noise because inside the receiver
    implementation_loss: float = Field(
        ge=0.0, default=0.0, description="Implementation loss in dB"
    )  # Only plays a role in the gain but not the noise because inside the receiver

    @property
    def noise_temperature(self) -> float:
        """float: receiver noise temperature."""
        return ROOM_TEMPERATURE * (10 ** (self.noise_figure / 10) - 1)

    @property
    def system_noise_temperature(self) -> float:
        """float: system noise temperature."""
        loss = from_db(-self.loss)
        return self.antenna_noise_temperature * loss + ROOM_TEMPERATURE * (1 - loss) + self.noise_temperature

    def total_gain(self, antenna: Antenna, angle: float) -> float:
        """Calculate the total gain of receiver and antenna."""
        return (
            antenna.gain(self.frequency, angle)
            + self.lna_gain
            - self.loss
            - self.demodulator_loss
            - self.implementation_loss
        )

    def gain_to_noise_temperature(self, antenna: Antenna, angle: float) -> float:
        """Calculate the gain-to-noise temperature in dB/K."""
        t_sys = self.system_noise_temperature
        return self.total_gain(antenna, angle) - to_db(t_sys) - self.lna_noise_figure


type ReceiverType = SimpleReceiver | ComplexReceiver
