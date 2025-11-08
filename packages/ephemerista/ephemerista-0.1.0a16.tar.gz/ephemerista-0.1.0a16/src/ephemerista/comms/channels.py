"""The channels.py module.

This module provides the `Channel` class which models a radio communications channel.
"""

from typing import Literal

from pydantic import UUID5, Field

from ephemerista import BaseModel
from ephemerista.comms.systems import CommunicationSystem
from ephemerista.comms.utils import to_db
from ephemerista.uuid_utils import generate_channel_uuid


class Channel(BaseModel):
    """The `Channel` class."""

    channel_id: UUID5 = Field(alias="id", default_factory=generate_channel_uuid)
    link_type: Literal["uplink", "downlink"]
    name: str = Field(description="The name of the channel", default="Default Channel")
    data_rate: float
    required_eb_n0: float = Field(json_schema_extra={"title": "Required Eb/N0"})
    margin: float
    modulation: Literal["BPSK", "QPSK", "8PSK", "16QAM", "32QAM", "64QAM", "128QAM", "256QAM"]
    roll_off: float = Field(default=1.5)
    forward_error_correction: float = Field(default=0.5)

    def bits_per_symbol(self) -> int:
        """
        Return the required bits per symbol for the channel's modulation scheme.

        Returns
        -------
        int
            The number of bits per symbol corresponding to the channels' modulation scheme.
        """
        return {
            "BPSK": 1,
            "QPSK": 2,
            "8PSK": 3,
            "16QAM": 4,
            "32QAM": 5,
            "64QAM": 6,
            "128QAM": 7,
            "256QAM": 8,
        }[self.modulation]

    @property
    def bandwidth(self) -> float:
        """float: bandwidth of the channel in Hz."""
        return self.data_rate * (1 + self.roll_off) / self.bits_per_symbol() / self.forward_error_correction

    def bit_energy_to_noise_density(
        self,
        tx: CommunicationSystem,
        rx: CommunicationSystem,
        losses: float,
        rng: float,
        tx_angle: float,
        rx_angle: float,
    ) -> float:
        """
        Calculate Eb/N0.

        This method calculates the energy per bit to noise power spectral density ratio for a link between a
        transmitting `CommunicationSystem` and a receiving `CommunicationSystem` on this channel.

        Parameters
        ----------
        tx : CommunicationSystem
            The TX communication system.
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
            The energy per bit to noise power spectral density ratio Eb/N0 in dB.
        """
        if self.channel_id not in tx.channels:
            msg = "Channel not supported by transmitter"
            raise ValueError(msg)
        if self.channel_id not in rx.channels:
            msg = "Channel not supported by receiver"
            raise ValueError(msg)

        c_n0 = tx.carrier_to_noise_density(rx, losses, rng, tx_angle, rx_angle)
        return c_n0 - to_db(self.data_rate)

    def bit_energy_to_noise_interference_density(
        self,
        tx: CommunicationSystem,
        rx: CommunicationSystem,
        losses: float,
        rng: float,
        tx_angle: float,
        rx_angle: float,
        bandwidth: float,
        interference_power_w: float,
    ) -> float:
        """
        Calculate the energy per bit to noise and interference power spectral density Eb/(N0+I0).

        Parameters
        ----------
        tx : CommunicationSystem
            The TX communication system.
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
        bandwidth: float
            The channel's bandwidth in Hz.
        interference_power_w: float
            The interference power in W.

        Returns
        -------
        float
            The energy per bit to noise and interference power spectral density Eb/(N0+I0) in dB.
        """
        if self.channel_id not in tx.channels:
            msg = "Channel not supported by transmitter"
            raise ValueError(msg)
        if self.channel_id not in rx.channels:
            msg = "Channel not supported by receiver"
            raise ValueError(msg)

        c_n0i0 = tx.carrier_to_noise_interference_density(
            rx, losses, rng, tx_angle, rx_angle, bandwidth, interference_power_w
        )
        return c_n0i0 - to_db(self.data_rate)

    @staticmethod
    def _recompute_eb_n0i0(
        carrier_power: float, noise_power: float, bandwidth: float, interference_power_w: float, data_rate: float
    ) -> float:
        """
        Calculate Eb/(N0+I0) from previously computed carrier power and noise power.

        Calculated using Eb/(N0+I0) = C/(N0+I0) - 10*log10(BITRATE)
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
            The energy per bit to noise and interference power spectral density Eb/(N0+I0) in dB.
        """
        return CommunicationSystem._recompute_c_n0i0(
            carrier_power, noise_power, bandwidth, interference_power_w
        ) - to_db(data_rate)
