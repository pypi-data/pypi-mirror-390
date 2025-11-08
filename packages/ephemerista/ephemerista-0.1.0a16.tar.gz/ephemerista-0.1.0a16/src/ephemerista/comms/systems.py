"""The systems.py module.

This module provides the `CommunicationSystem` class.
"""

from typing import Self

from pydantic import UUID5, Field

from ephemerista import BaseModel
from ephemerista.comms.antennas import ANTENNA_DISCRIMINATOR, AntennaType
from ephemerista.comms.receiver import ReceiverType
from ephemerista.comms.transmitter import Transmitter
from ephemerista.comms.utils import BOLTZMANN_CONSTANT, free_space_path_loss, from_db, to_db
from ephemerista.uuid_utils import generate_comms_uuid


class CommunicationSystem(BaseModel):
    """The `CommunicationSystem` class.

    This class composes the `Antenna`, `Receiver`, and `Transmitter` classes to form a model of full communication
    system. To instances of compatible communication systems are required to compute the properties of a link between
    the two systems.
    """

    system_id: UUID5 = Field(alias="id", default_factory=generate_comms_uuid)
    channels: list[UUID5]
    antenna: AntennaType = Field(discriminator=ANTENNA_DISCRIMINATOR)
    receiver: ReceiverType | None = Field(default=None, discriminator="receiver_type")
    transmitter: Transmitter | None = Field(default=None)

    def carrier_to_noise_density(self, rx: Self, losses: float, rng: float, tx_angle: float, rx_angle: float) -> float:
        """
        Calculate the carrier-to-noise density C/N0.

        Parameters
        ----------
        rx : CommunicationSystem
            The RX communication system.
        losses: float
            The sum of the environmental losses
        rng: float
            The slant range in meters.
        tx_angle: float
            The angle between the transmitter antenna's boresight vector and the transmitter-receiver vector in radians.
        rx_angle: float
            The angle between the receiver antenna's boresight vector and the receiver-transmitter vector in radians.

        Returns
        -------
        float
            The carrier-to-noise density C/N0 in dB.Hz.
        """
        if not self.transmitter:
            msg = "Transmitter must be defined"
            raise ValueError(msg)
        if not rx.receiver:
            msg = "Receiver must be defined"
            raise ValueError(msg)
        if self.transmitter.frequency != rx.receiver.frequency:
            msg = "Carrier frequencies must match"
            raise ValueError(msg)
        fspl = free_space_path_loss(rng, self.transmitter.frequency)
        eirp = self.transmitter.equivalent_isotropic_radiated_power(self.antenna, tx_angle)
        gt = rx.receiver.gain_to_noise_temperature(rx.antenna, rx_angle)
        return eirp + gt - fspl - losses - to_db(BOLTZMANN_CONSTANT)

    def noise_power(self, rx: Self, bandwidth: float) -> float:
        """
        Calculate the noise power in dBW.

        Parameters
        ----------
        rx : CommunicationSystem
            The RX communication system.
        bandwidth : float
            The channel's bandwidth in Hz.

        Returns
        -------
        float
            The noise power in dBW.
        """
        if not self.transmitter:
            msg = "Transmitter must be defined"
            raise ValueError(msg)
        if not rx.receiver:
            msg = "Receiver must be defined"
            raise ValueError(msg)
        if self.transmitter.frequency != rx.receiver.frequency:
            msg = "Carrier frequencies must match"
            raise ValueError(msg)

        return to_db(rx.receiver.system_noise_temperature * BOLTZMANN_CONSTANT * bandwidth)

    def carrier_power(self, rx: Self, losses: float, rng: float, tx_angle: float, rx_angle: float) -> float:
        """
        Calculate the carrier power at receiver input in dBW.

        Parameters
        ----------
        rx : CommunicationSystem
            The RX communication system.
        losses: float
            The sum of the environmental losses
        rng: float
            The slant range in meters.
        tx_angle: float
            The angle between the transmitter antenna's boresight vector and the transmitter-receiver vector in radians.
        rx_angle: float
            The angle between the receiver antenna's boresight vector and the receiver-transmitter vector in radians.

        Returns
        -------
        float
            The carrier power at receiver input in dBW.
        """
        if not self.transmitter:
            msg = "Transmitter must be defined"
            raise ValueError(msg)
        if not rx.receiver:
            msg = "Receiver must be defined"
            raise ValueError(msg)
        if self.transmitter.frequency != rx.receiver.frequency:
            msg = "Carrier frequencies must match"
            raise ValueError(msg)
        fspl = free_space_path_loss(rng, self.transmitter.frequency)
        eirp = self.transmitter.equivalent_isotropic_radiated_power(self.antenna, tx_angle)
        rx_gains = rx.receiver.total_gain(rx.antenna, rx_angle)
        return eirp - fspl - losses + rx_gains

    def carrier_to_noise_interference_density(
        self,
        rx: Self,
        losses: float,
        rng: float,
        tx_angle: float,
        rx_angle: float,
        bandwidth: float,
        interference_power_w: float,
    ) -> float:
        """
        Calculate the carrier-to-noise interference density C/(I0+N0) in dBHz.

        Parameters
        ----------
        rx : CommunicationSystem
            The RX communication system.
        losses: float
            The sum of the environmental losses
        rng: float
            The slant range in meters.
        tx_angle: float
            The angle between the transmitter antenna's boresight vector and the transmitter-receiver vector in radians.
        rx_angle: float
            The angle between the receiver antenna's boresight vector and the receiver-transmitter vector in radians.
        interference_power_w: float
            The interference power in W

        Returns
        -------
        float
            The carrier-to-noise interference density C/(I0+N0) in dBHz.
        """
        return self._recompute_c_n0i0(
            carrier_power=self.carrier_power(rx, losses, rng, tx_angle, rx_angle),
            noise_power=self.noise_power(rx, bandwidth),
            bandwidth=bandwidth,
            interference_power_w=interference_power_w,
        )

    @staticmethod
    def _recompute_c_n0i0(
        carrier_power: float, noise_power: float, bandwidth: float, interference_power_w: float
    ) -> float:
        """
        Calculate the carrier-to-noise interference density C/(I0+N0) in dBHz.

        Calculated using C/(N0+I0) = PRxInput - (N+I) + 10*log10(bandwidth)
        Reference: https://uk.mathworks.com/help/satcom/ug/interference-from-satellite-constellation-on-comms-link.html

        Parameters
        ----------
        carrier_power: float
            The carrier power at receiver input in W.
        noise_power: float
            The noise power in W.
        bandwidth: float
            The channel's bandwidth in Hz.
        interference_power_w: float
            The interference power in W.

        Returns
        -------
        float
            The carrier-to-noise interference density C/(I0+N0) in dBHz.
        """
        noise_and_interf_power_w = from_db(noise_power) + interference_power_w
        return carrier_power - to_db(noise_and_interf_power_w) + to_db(bandwidth)
