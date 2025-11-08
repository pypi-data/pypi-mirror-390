"""The link_budget.py module.

This module provides the `LinkBudget` class and the associated `LinkBudgetResults` class.
"""

from functools import partial
from typing import Literal, Self

import itur
import lox_space as lox
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from itur.models import itu618, itu836
from lox_space import TimeDelta
from pydantic import UUID5, Field, computed_field

from ephemerista import BaseModel
from ephemerista.analysis import Analysis
from ephemerista.analysis.visibility import Pass, Visibility, VisibilityResults, Window
from ephemerista.angles import Angle
from ephemerista.assets import Asset, AssetKey, GroundStation, Spacecraft, _asset_id
from ephemerista.comms.antennas import ParabolicPattern
from ephemerista.comms.channels import Channel
from ephemerista.comms.frequencies import Frequency
from ephemerista.comms.systems import CommunicationSystem
from ephemerista.comms.utils import free_space_path_loss, from_db, to_db
from ephemerista.coords.twobody import Cartesian
from ephemerista.frames import ReferenceFrame
from ephemerista.math import angle_between
from ephemerista.scenarios import Ensemble, Scenario
from ephemerista.time import Time

# Constant representing zero power in dBW for JSON serialization compatibility
ZERO_POWER_DBW = -999.0


class InterferenceStats(BaseModel):
    """The `InterferenceStats` class.

    This class models the influence of interfering radio transmissions on the link.
    """

    interference_power_w: float = Field(ge=0.0, description="Total received interference power from all sources, in W")
    c_n0i0: float = Field(description="Carrier to noise plus interference density, in dB")
    eb_n0i0: float = Field(description="Bit energy to noise plus interference density, in dB")
    margin_with_interference: float = Field(description="Link margin considering interference, in dB")

    @computed_field(description="Total received interference power in dBW")
    @property
    def interference_power(self) -> float:
        return to_db(self.interference_power_w) if self.interference_power_w > 0 else ZERO_POWER_DBW


def _off_boresight_angle(
    time: Time, ensemble: Ensemble, self: Asset, other: Asset, comms: CommunicationSystem
) -> float:
    self_state = ensemble[self].interpolate(time)
    other_state = ensemble[other].interpolate(time)

    # Check if tracking the other asset directly or via constellation
    is_tracking_directly = other.asset_id in self.tracked_object_ids
    is_tracking_via_constellation = (
        other.constellation_id is not None and other.constellation_id in self.tracked_constellation_ids
    )

    if is_tracking_directly or is_tracking_via_constellation:
        # This asset is tracking the other asset (directly or via constellation), return pointing error
        angle = np.radians(self.pointing_error)
    elif self.tracked_object_ids:
        # This asset tracks other assets, compute angle between communication vector and closest tracked object
        min_angle = float("inf")
        for tracked_id in self.tracked_object_ids:
            if tracked_id in ensemble:
                tracked_state = ensemble[tracked_id].interpolate(time)
                # Compute angle in the appropriate local frame
                angle = _compute_angle_between_targets(self, self_state, other_state, tracked_state)
                min_angle = min(min_angle, angle)

        if min_angle != float("inf"):
            angle = min_angle
        else:
            # No tracked objects found in ensemble, compute angle using antenna's boresight vector
            angle = _compute_boresight_angle(self, self_state, other_state, comms)
    else:
        # This asset does not track any object, using its antenna's boresight vector
        angle = _compute_boresight_angle(self, self_state, other_state, comms)

    return max(0, angle)


def _compute_angle_between_targets(
    asset: Asset, self_state: Cartesian, other_state: Cartesian, tracked_state: Cartesian
) -> float:
    """Compute angle between two target directions in the appropriate local frame."""
    if isinstance(asset.model, Spacecraft):
        # For spacecraft: work in LVLH frame
        rot_lvlh_from_eci = self_state.rotation_lvlh().T
        # Transform both communication vectors to LVLH
        this_to_other_eci = other_state.position - self_state.position
        this_to_tracked_eci = tracked_state.position - self_state.position
        this_to_other_lvlh = rot_lvlh_from_eci @ this_to_other_eci
        this_to_tracked_lvlh = rot_lvlh_from_eci @ this_to_tracked_eci
        # Compute angle in LVLH frame
        return angle_between(this_to_other_lvlh, this_to_tracked_lvlh)

    elif isinstance(asset.model, GroundStation):
        # For ground station: work in SEZ frame
        # Get rotation matrix from ECEF to SEZ
        rot_sez_from_ecef = asset.model.rotation_to_topocentric()

        # Convert ECI states to ECEF
        iau_earth_frame = ReferenceFrame(abbreviation="IAU_EARTH")
        other_ecef = other_state.to_frame(iau_earth_frame).position
        tracked_ecef = tracked_state.to_frame(iau_earth_frame).position
        self_ecef = self_state.to_frame(iau_earth_frame).position

        # Transform communication vectors to SEZ
        this_to_other_ecef = other_ecef - self_ecef
        this_to_tracked_ecef = tracked_ecef - self_ecef
        this_to_other_sez = rot_sez_from_ecef @ this_to_other_ecef
        this_to_tracked_sez = rot_sez_from_ecef @ this_to_tracked_ecef

        # Compute angle in SEZ frame
        return angle_between(this_to_other_sez, this_to_tracked_sez)

    else:
        # Fallback: use ECI frame
        this_to_other = other_state.position - self_state.position
        this_to_tracked = tracked_state.position - self_state.position
        return angle_between(this_to_other, this_to_tracked)


def _compute_boresight_angle(
    asset: Asset, self_state: Cartesian, other_state: Cartesian, comms: CommunicationSystem
) -> float:
    """Compute the off-boresight angle in the appropriate local frame."""
    if isinstance(asset.model, Spacecraft):
        # For spacecraft: work in LVLH frame
        rot_lvlh_from_eci = self_state.rotation_lvlh().T
        # Transform communication vector to LVLH
        comm_vector_eci = other_state.position - self_state.position
        comm_vector_lvlh = rot_lvlh_from_eci @ comm_vector_eci
        comm_unit_lvlh = comm_vector_lvlh / np.linalg.norm(comm_vector_lvlh)

        # Antenna boresight is already in LVLH frame for spacecraft
        boresight_lvlh = comms.antenna.boresight_array

        # Compute angle in LVLH frame
        angle = angle_between(comm_unit_lvlh, boresight_lvlh)

    elif isinstance(asset.model, GroundStation):
        # For ground station: work in SEZ frame
        # Get rotation matrix from ECEF to SEZ
        rot_sez_from_ecef = asset.model.rotation_to_topocentric()

        # Convert ECI states to ECEF
        iau_earth_frame = ReferenceFrame(abbreviation="IAU_EARTH")
        other_ecef = other_state.to_frame(iau_earth_frame).position
        self_ecef = self_state.to_frame(iau_earth_frame).position

        # Transform communication vector to SEZ
        comm_vector_ecef = other_ecef - self_ecef
        comm_vector_sez = rot_sez_from_ecef @ comm_vector_ecef
        comm_unit_sez = comm_vector_sez / np.linalg.norm(comm_vector_sez)

        # Antenna boresight is already in SEZ frame for ground stations
        boresight_sez = comms.antenna.boresight_array

        # Compute angle in SEZ frame
        angle = angle_between(comm_unit_sez, boresight_sez)

    else:
        # Fallback: compute in ECI frame (should not happen with current asset types)
        r = other_state.position - self_state.position
        ru = r / np.linalg.norm(r)
        # Assume boresight is in ECI frame as fallback
        angle = angle_between(ru, comms.antenna.boresight_array)

    return angle


class EnvironmentalLosses(BaseModel):
    """The `EnvironmentalLosses` class.

    This class models all environmental losses supported by Ephemerista.
    """

    rain_attenuation: float = Field(ge=0.0, description="Rain attenuation, in dB)")
    gaseous_attenuation: float = Field(ge=0.0, description="Gaseous attenuation, in dB")
    scintillation_attenuation: float = Field(ge=0.0, description="Solar scintillation attenuation, in dB")
    atmospheric_attenuation: float = Field(ge=0.0, description="Attenuation of atmospheric gases, in dB")
    cloud_attenuation: float = Field(ge=0.0, description="Attenuation due to clouds, in dB")
    depolarization_loss: float = Field(ge=0.0, description="Depolarization losses, in dB")

    def sum(self) -> float:
        """Sum all environmental losses.

        Returns
        -------
        float
            Total environmental losses in dB.
        """
        return (
            self.rain_attenuation
            + self.gaseous_attenuation
            + self.scintillation_attenuation
            + self.atmospheric_attenuation
            + self.cloud_attenuation
            + self.depolarization_loss
        )

    @classmethod
    def no_losses(cls) -> Self:
        """Initialize all environmental losses to zero.

        Returns
        -------
        EnvironmentalLosses
            Instance with all loss components set to zero.
        """
        return cls(
            rain_attenuation=0,
            gaseous_attenuation=0,
            scintillation_attenuation=0,
            atmospheric_attenuation=0,
            cloud_attenuation=0,
            depolarization_loss=0,
        )

    @classmethod
    def calculate(
        cls,
        percentage_exceed: float,
        time: Time,
        observer: Asset,
        target_comms: CommunicationSystem,
        observer_comms: CommunicationSystem,
        gs_pass: Pass,
        min_elevation_deg: float = 5.0,
    ) -> Self:
        """Calculate environmental losses for a given link.

        The losses are computed based on ITU-R recommendations using the `ìtur` library.

        Parameters
        ----------
        percentage_exceed : float
            Percentage of time losses are exceeded
        time : Time
            Time at which to calculate losses
        observer : Asset
            Observer asset (typically ground station)
        target_comms : CommunicationSystem
            Target communication system
        observer_comms : CommunicationSystem
            Observer communication system
        gs_pass : Pass
            Pass object for elevation data
        min_elevation_deg : float, optional
            Minimum elevation (degrees) below which the threshold value is used.
            ITU-R models become numerically unstable below ~5 degrees.
            Default is 5.0.

        Returns
        -------
        EnvironmentalLosses
            Calculated environmental losses for the link
        """
        f = target_comms.transmitter.frequency
        f_ghz = f.hertz * 1e-9
        gs_lat_deg = observer.model.latitude.degrees
        gs_lon_deg = observer.model.longitude.degrees
        gs_alt_km = observer.model.altitude * 1e-3

        gs_ant_parabolic_equivalent = ParabolicPattern.from_beamwidth(observer_comms.antenna.beamwidth(f), f)
        gs_ant_dia = gs_ant_parabolic_equivalent.diameter
        gs_ant_eff = gs_ant_parabolic_equivalent.efficiency

        pass_observables = gs_pass.interpolate(time)
        el_deg = pass_observables.elevation.degrees

        # For elevations below threshold, use the threshold value to avoid numerical instability
        # ITU-R models become numerically unstable at very low elevations
        el_deg = max(el_deg, min_elevation_deg)

        # Computing rain attenuation
        rain_attenuation = itur.rain_attenuation(
            gs_lat_deg, gs_lon_deg, f_ghz, el_deg, gs_alt_km, percentage_exceed
        ).value

        # Computing depolarization loss
        depolarization_loss = 0
        if f_ghz > 4 and f_ghz <= 55:  # noqa: PLR2004
            xpd = itu618.rain_cross_polarization_discrimination(
                rain_attenuation,
                f_ghz,
                el_deg if el_deg < 60 else 60,  # noqa: PLR2004
                percentage_exceed,
            ).value
            depolarization_loss = to_db(1 + 1 / xpd)

        # Computing scintillation
        scintillation_attenuation = itur.scintillation_attenuation(
            gs_lat_deg, gs_lon_deg, f_ghz, el_deg, percentage_exceed, gs_ant_dia, gs_ant_eff
        ).value

        # Computing gaseous attenuation
        T = itur.surface_mean_temperature(gs_lat_deg, gs_lon_deg).value  # noqa: N806
        P = itur.standard_pressure(gs_lat_deg, gs_alt_km).value  # noqa: N806
        rho = itu836.surface_water_vapour_density(gs_lat_deg, gs_lon_deg, percentage_exceed, gs_alt_km).value
        gaseous_attenuation = itur.gaseous_attenuation_slant_path(f_ghz, el_deg, rho, P, T, h=gs_alt_km).value

        # Computing atmospheric attenuation
        atmospheric_attenuation = itur.atmospheric_attenuation_slant_path(
            gs_lat_deg, gs_lon_deg, f_ghz, el_deg, percentage_exceed, gs_ant_dia
        ).value

        # Computing cloud attenuation
        cloud_attenuation = itur.cloud_attenuation(gs_lat_deg, gs_lon_deg, el_deg, f_ghz, percentage_exceed).value

        return cls(
            rain_attenuation=rain_attenuation,
            gaseous_attenuation=gaseous_attenuation,
            scintillation_attenuation=scintillation_attenuation,
            atmospheric_attenuation=atmospheric_attenuation,
            cloud_attenuation=cloud_attenuation,
            depolarization_loss=depolarization_loss,
        )


class LinkStats(BaseModel):
    """The `LinkStats` class.

    This class models all relevant properties of a radio link for link budget calculations at specific point in time.
    """

    slant_range: float = Field(description="Range between transmit and receive antennas, in km")
    fspl: float = Field(description="Free space path loss, in dB")
    tx_angle: Angle = Field(
        description="Angle between the TX antenna boresight vector and the transmitter to receiver vector, in degrees"
    )
    rx_angle: Angle = Field(
        description="Angle between the RX antenna boresight vector and the receiver to transmitter vector, in degrees"
    )
    eirp: float = Field(description="Effective isotropic radiated power, in dBW")
    gt: float = Field(description="Gain to noise temperature ratio, in dB/K")
    c_n0: float = Field(description="Carrier to noise density, in dB")
    eb_n0: float = Field(description="Bit energy to noise density, in dB")
    margin: float = Field(description="Link margin, in dB")
    losses: EnvironmentalLosses = Field(description="Environmental losses")
    carrier_rx_power: float = Field(description="Power level at receiver input, in dBW")
    data_rate: float = Field(description="Data rate, in bit/s")
    bandwidth: float = Field(description="Bandwidth, in Hz")
    frequency: Frequency = Field(description="Operating frequency")
    noise_power: float = Field(description="Noise power, in dBW")
    interference_stats: InterferenceStats | None = Field(
        default=None, description="Interference data (optional, only available after analyzing interference)"
    )

    @classmethod
    def calculate(
        cls,
        time: Time,
        channel: Channel,
        link_type: Literal["uplink", "downlink"],
        target: Asset,
        observer: Asset,
        target_comms: CommunicationSystem,
        observer_comms: CommunicationSystem,
        losses: EnvironmentalLosses,
        ensemble: Ensemble,
    ) -> Self:
        """Calculate link statistics for a given time and link configuration.

        Parameters
        ----------
        time : Time
            Time at which to calculate link statistics
        channel : Channel
            Communication channel configuration
        link_type : {"uplink", "downlink"}
            Type of link direction
        target : Asset
            Target asset (typically spacecraft)
        observer : Asset
            Observer asset (typically ground station)
        target_comms : CommunicationSystem
            Target communication system
        observer_comms : CommunicationSystem
            Observer communication system
        losses : EnvironmentalLosses
            Environmental losses to apply
        ensemble : Ensemble
            Ensemble containing propagated trajectories

        Returns
        -------
        LinkStats
            Calculated link statistics including EIRP, G/T, margins, etc.
        """
        sc_state = ensemble[target].interpolate(time)
        gs_state = ensemble[observer].interpolate(time)

        sc_angle = _off_boresight_angle(time, ensemble, target, observer, target_comms)
        gs_angle = _off_boresight_angle(time, ensemble, observer, target, observer_comms)

        slant_range = float(np.linalg.norm(sc_state.position - gs_state.position))
        if link_type == "uplink":
            rx_angle = sc_angle
            tx_angle = gs_angle
            rx = target_comms
            tx = observer_comms
        else:
            rx_angle = gs_angle
            tx_angle = sc_angle
            rx = observer_comms
            tx = target_comms
        if not tx.transmitter:
            msg = "Transmitter not found"
            raise ValueError(msg)
        if not rx.receiver:
            msg = "Receiver not found"
            raise ValueError(msg)
        frequency = tx.transmitter.frequency
        bandwidth = channel.bandwidth
        fspl = free_space_path_loss(slant_range, frequency)
        eirp = tx.transmitter.equivalent_isotropic_radiated_power(tx.antenna, tx_angle)
        gt = rx.receiver.gain_to_noise_temperature(rx.antenna, rx_angle)
        carrier_rx_power = tx.carrier_power(rx, losses.sum(), slant_range, tx_angle, rx_angle)
        noise_power = tx.noise_power(rx, bandwidth)
        c_n0 = tx.carrier_to_noise_density(rx, losses.sum(), slant_range, tx_angle, rx_angle)
        eb_n0 = channel.bit_energy_to_noise_density(tx, rx, losses.sum(), slant_range, tx_angle, rx_angle)
        margin = eb_n0 - channel.required_eb_n0 - channel.margin
        return cls(
            slant_range=slant_range,
            fspl=fspl,
            tx_angle=Angle.from_radians(tx_angle),
            rx_angle=Angle.from_radians(rx_angle),
            eirp=eirp,
            gt=gt,
            c_n0=c_n0,
            eb_n0=eb_n0,
            margin=margin,
            losses=losses,
            carrier_rx_power=carrier_rx_power,
            data_rate=channel.data_rate,
            bandwidth=bandwidth,
            frequency=frequency,
            noise_power=noise_power,
        )

    def add_interference(self, interference_power_w: float) -> Self:
        """Add interference to previously computed link statistics.

        Parameters
        ----------
        interference_power_w : float
            Total interference power in Watts

        Returns
        -------
        LinkStats
            Updated link statistics including interference effects
        """
        c_n0i0 = CommunicationSystem._recompute_c_n0i0(
            self.carrier_rx_power, self.noise_power, self.bandwidth, interference_power_w
        )
        eb_n0i0 = Channel._recompute_eb_n0i0(
            self.carrier_rx_power, self.noise_power, self.bandwidth, interference_power_w, self.data_rate
        )
        margin_with_interference = self.margin + eb_n0i0 - self.eb_n0

        return self.model_copy(
            update={
                "interference_stats": InterferenceStats(
                    interference_power_w=interference_power_w,
                    c_n0i0=c_n0i0,
                    eb_n0i0=eb_n0i0,
                    margin_with_interference=margin_with_interference,
                )
            }
        )

    def as_flatten_dict(self) -> dict[str, float]:
        """
        Convert the link stats to a flattened dictionary.

        The resultant dict is the same as if it were created by Pydantic's model_dump, but
        the parameters that have internal structure are flattened following these rules:
        - tx_angle and rx_angle just use their internal `degrees` parameter.
        - losses and interference_stats are flattened, with their parameters added to the top level.
        """
        link_dict = self.model_dump(
            exclude={"interference_stats", "losses", "tx_angle", "rx_angle"},
        )
        link_dict.update(
            self.losses.model_dump(),
            tx_angle=self.tx_angle.degrees,
            rx_angle=self.rx_angle.degrees,
            losses_sum=self.losses.sum(),
        )
        link_dict.update(
            self.interference_stats.model_dump()
            if self.interference_stats
            else InterferenceStats(
                interference_power_w=0.0, c_n0i0=self.c_n0, eb_n0i0=self.eb_n0, margin_with_interference=self.margin
            ).model_dump()
        )
        return link_dict


class Link(BaseModel):
    """The `Link` class.

    This class models a radio link between two communication systems covering a specific visbility window.
    """

    window: Window = Field(description="Time window of the visibility pass where the link budget is computed")
    link_type: Literal["uplink", "downlink"] = Field(description="Link type, uplink or downlink")
    times: list[Time] = Field(description="Time vector")
    stats: list[LinkStats] = Field(description="List of link metrics, one for each time step")

    @computed_field
    @property
    def mean_slant_range(self) -> float:
        return float(np.mean([s.slant_range for s in self.stats]))

    @computed_field
    @property
    def mean_tx_angle(self) -> float:
        return float(np.mean([s.tx_angle.degrees for s in self.stats]))

    @computed_field
    @property
    def mean_rx_angle(self) -> float:
        return float(np.mean([s.rx_angle.degrees for s in self.stats]))

    @computed_field
    @property
    def mean_fspl(self) -> float:
        return float(np.mean([s.fspl for s in self.stats]))

    @computed_field
    @property
    def mean_eirp(self) -> float:
        return float(np.mean([s.eirp for s in self.stats]))

    @computed_field
    @property
    def mean_gt(self) -> float:
        return float(np.mean([s.gt for s in self.stats]))

    @computed_field
    @property
    def mean_losses(self) -> float:
        return float(np.mean([s.losses.sum() for s in self.stats]))

    @computed_field
    @property
    def mean_c_n0(self) -> float:
        return float(np.mean([s.c_n0 for s in self.stats]))

    @computed_field
    @property
    def mean_eb_n0(self) -> float:
        return float(np.mean([s.eb_n0 for s in self.stats]))

    @computed_field
    @property
    def mean_margin(self) -> float:
        return float(np.mean([s.margin for s in self.stats]))

    def to_dataframe(self) -> pd.DataFrame:
        """Convert link statistics to a pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            DataFrame containing all link statistics indexed by time.
        """
        data = [s.as_flatten_dict() for s in self.stats]
        df = pd.DataFrame.from_records(data, index=[t.datetime for t in self.times])
        return df

    def plot(self, *, plot_interference: bool = False):
        """Plot all link properties.

        Parameters
        ----------
        plot_interference : bool, optional
            Whether to include interference statistics in the plots.
            Default is False.

        Returns
        -------
        matplotlib.figure.Figure
            Figure containing subplots of all link properties.
        """
        df = self.to_dataframe()

        fig, ax = plt.subplots(3, 3, figsize=(12, 8))
        plt.subplots_adjust(hspace=0.4, wspace=0.4)

        plot_title = f"{self.link_type.title()} from {self.window.start.to_utc()} to {self.window.stop.to_utc()}"
        if plot_interference:
            plot_title += ", with interference"
        fig.suptitle(plot_title)

        for a in ax.flat:
            a.xaxis.set_major_locator(mdates.HourLocator())
            a.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            a.xaxis.set_tick_params(rotation=45)
            a.grid()

        ax[0, 0].plot(df.index, df["slant_range"])
        ax[0, 0].set_title("Slant Range")
        ax[0, 0].set_ylabel("km")

        ax[0, 1].plot(df.index, df["tx_angle"], label="TX")
        ax[0, 1].plot(df.index, df["rx_angle"], label="RX")
        ax[0, 1].legend()
        ax[0, 1].set_title("Off Boresight Angles")
        ax[0, 1].set_ylabel("degrees")

        ax[0, 2].plot(df.index, df["fspl"])
        ax[0, 2].set_title("Free Space Path Loss")
        ax[0, 2].set_ylabel("dB")

        ax[1, 0].plot(df.index, df["eirp"])
        ax[1, 0].set_title("EIRP")
        ax[1, 0].set_ylabel("dBW")

        ax[1, 1].plot(df.index, df["gt"])
        ax[1, 1].set_title("G/T")
        ax[1, 1].set_ylabel("dB/K")

        ax[1, 2].plot(df.index, df["losses_sum"])
        ax[1, 2].set_title("Environment attenuations")
        ax[1, 2].set_ylabel("dB")

        ax[2, 0].plot(df.index, df["c_n0"], label="C/N0")
        if plot_interference:
            ax[2, 0].plot(df.index, df["c_n0i0"], label="C/(N0+I0)")
            ax[2, 0].legend()
        ax[2, 0].set_title("C/N0")
        ax[2, 0].set_ylabel("dB")

        ax[2, 1].plot(df.index, df["eb_n0"], label="Eb/N0")
        if plot_interference:
            ax[2, 1].plot(df.index, df["eb_n0i0"], label="Eb/(N0+I0)")
            ax[2, 1].legend()
        ax[2, 1].set_title("Eb/N0")
        ax[2, 1].set_ylabel("dB")

        ax[2, 2].plot(df.index, df["margin"], label="Margin")
        if plot_interference:
            ax[2, 2].plot(df.index, df["margin_with_interference"], label="Margin (with interference)")
            ax[2, 2].legend()
        ax[2, 2].set_title("Link Margin")
        ax[2, 2].set_ylabel("dB")

        return fig

    def plot_attenuations(self, percentage_exceed: float):
        """Plot all environmental attenuations.

        Parameters
        ----------
        percentage_exceed : float
            Percentage of time the attenuations are exceeded, used in plot title.

        Returns
        -------
        matplotlib.figure.Figure
            Figure containing subplots of all environmental attenuations.
        """
        df = self.to_dataframe()

        fig, ax = plt.subplots(2, 3, figsize=(10, 6))
        plt.subplots_adjust(hspace=0.4, wspace=0.4)

        plot_title = f"{self.window.start.to_utc()} to {self.window.stop.to_utc()}, attenuations exceeded {percentage_exceed}% of the time"  # noqa: E501
        fig.suptitle(plot_title)

        for a in ax.flat:
            a.xaxis.set_major_locator(mdates.HourLocator())
            a.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            a.xaxis.set_tick_params(rotation=45)
            a.grid()

        ax[0, 0].plot(df.index, df["rain_attenuation"])
        ax[0, 0].set_title("Rain attenuation")
        ax[0, 0].set_ylabel("dB")

        ax[0, 1].plot(df.index, df["gaseous_attenuation"])
        ax[0, 1].set_title("Gaseous attenuation")
        ax[0, 1].set_ylabel("dB")

        ax[0, 2].plot(df.index, df["scintillation_attenuation"])
        ax[0, 2].set_title("Scintillation attenuation")
        ax[0, 2].set_ylabel("dB")

        ax[1, 0].plot(df.index, df["atmospheric_attenuation"])
        ax[1, 0].set_title("Atmospheric attenuation")
        ax[1, 0].set_ylabel("dB")

        ax[1, 1].plot(df.index, df["cloud_attenuation"])
        ax[1, 1].set_title("Cloud attenuation")
        ax[1, 1].set_ylabel("dB")

        ax[1, 2].plot(df.index, df["depolarization_loss"])
        ax[1, 2].set_title("Depolarization loss")
        ax[1, 2].set_ylabel("dB")


class LinkBudgetResults(BaseModel):
    """The results of the `LinkBudget` analysis."""

    results_type: Literal["link_budget"] = Field(default="link_budget", frozen=True, repr=False, alias="type")
    links: dict[UUID5, dict[UUID5, list[Link]]] = Field(
        description="Dictionary of all links between all targets and all observers"
    )

    def get(self, observer: AssetKey, target: AssetKey) -> list[Link]:
        """Get all links for a given observer and target pairing."""
        target_passes = self.links.get(_asset_id(target), {})
        return target_passes.get(_asset_id(observer), [])

    def __getitem__(self, key: tuple[AssetKey, AssetKey]) -> list[Link]:
        """Get all links for a given observer and target pairing."""
        return self.get(*key)

    def to_dataframe(self, observer: AssetKey, target: AssetKey, *, with_interference: bool = False) -> pd.DataFrame:
        """Convert the analysis results to a Pandas data frame.

        Parameters
        ----------
        observer : AssetKey
            Observer asset identifier
        target : AssetKey
            Target asset identifier
        with_interference : bool, optional
            Whether to include interference statistics in the dataframe.
            Default is False.

        Returns
        -------
        pd.DataFrame
            Dataframe containing link statistics for all passes between
            the observer and target.
        """
        links = self.get(observer, target)
        data = []
        for link in links:
            row = {
                "start": link.window.start.datetime,
                "end": link.window.stop.datetime,
                "duration": link.window.duration,
                "type": link.link_type,
                "mean_slant_range": link.mean_slant_range,
                "mean_tx_angle": link.mean_tx_angle,
                "mean_rx_angle": link.mean_rx_angle,
                "mean_fspl": link.mean_fspl,
                "mean_eirp": link.mean_eirp,
                "mean_gt": link.mean_gt,
                "mean_losses": link.mean_losses,
                "mean_c_n0": link.mean_c_n0,
                "mean_eb_n0": link.mean_eb_n0,
                "mean_margin": link.mean_margin,
            }

            if with_interference:
                interference_power = []
                c_n0i0 = []
                eb_n0i0 = []
                margin_with_interference = []
                for s in link.stats:
                    s_interf = s.interference_stats
                    if s_interf:
                        interference_power.append(s_interf.interference_power)
                        c_n0i0.append(s_interf.c_n0i0)
                        eb_n0i0.append(s_interf.eb_n0i0)
                        margin_with_interference.append(s_interf.margin_with_interference)
                    else:
                        # No interference detected, so c_n0i0 = c_n0 and eb_n0i0 = eb_n0
                        interference_power.append(ZERO_POWER_DBW)
                        c_n0i0.append(s.c_n0)
                        eb_n0i0.append(s.eb_n0)
                        margin_with_interference.append(s.margin)

                row["mean_c_n0i0"] = np.mean(c_n0i0)
                row["mean_eb_n0i0"] = np.mean(eb_n0i0)
                row["mean_margin_interference"] = np.mean(margin_with_interference)

            data.append(row)
        return pd.DataFrame(data)


class LinkBudget(Analysis[LinkBudgetResults]):
    """The `LinkBudget` analysis."""

    scenario: Scenario = Field(description="The scenario used to analyze the link budget")
    start_time: Time | None = Field(
        default=None, description="Start time (optional, if None the scenario's start time is used)"
    )
    end_time: Time | None = Field(
        default=None, description="End time (optional, if None the scenario's end time is used)"
    )
    percentage_exceed: float = Field(
        gt=0.001,
        le=5.0,
        default=1.0,
        description="Percentage of the time the environmental attenuation values are exceeded, per ITU-R",
    )
    min_elevation_deg: float = Field(
        ge=0.0,
        le=90.0,
        default=5.0,
        description="Minimum elevation angle (degrees) below which the threshold value is used to avoid "
        "numerical instability",
    )
    with_environmental_losses: bool = Field(
        default=True,
        description="Whether to calculate environmental losses (rain, atmospheric, etc.) or use zero losses",
    )
    with_interference: bool = Field(
        default=False,
        description="Whether to calculate interference from other transmissions in the scenario",
    )

    def analyze(  # type: ignore
        self,
        ensemble: Ensemble | None = None,
        visibility: VisibilityResults | None = None,
    ) -> LinkBudgetResults:
        """Run the link budget analysis.

        Parameters
        ----------
        ensemble : Ensemble, optional
            Pre-computed ensemble with propagated trajectories. If None,
            the scenario will be propagated automatically.
        visibility : VisibilityResults, optional
            Pre-computed visibility results. If None, visibility analysis
            will be run automatically.

        Returns
        -------
        LinkBudgetResults
            Complete link budget analysis results including all links
            and their statistics over time.
        """
        if not ensemble:
            ensemble = self.scenario.propagate()

        start_time = self.start_time or self.scenario.start_time
        end_time = self.end_time or self.scenario.end_time

        if not visibility:
            visibility = Visibility(scenario=self.scenario, start_time=start_time, end_time=end_time).analyze(ensemble)

        links = {}

        for target_id, observers in visibility.passes.items():
            target = self.scenario[target_id]
            if not isinstance(target.model, Spacecraft):
                continue
            target_channels = set()
            for c in target.comms:
                target_channels.update(c.channels)

            if target_id not in links:
                links[target_id] = {}

            for observer_id, passes in observers.items():
                links[target_id][observer_id] = []

                observer = self.scenario[observer_id]
                if not isinstance(observer.model, GroundStation):
                    continue
                observer_channels = set()
                for c in observer.comms:
                    observer_channels.update(c.channels)

                channels = target_channels.intersection(observer_channels)
                if not channels:
                    continue

                for channel_id in channels:
                    channel = self.scenario.channel_by_id(channel_id)
                    link_type = channel.link_type
                    target_comms = target.comms_by_channel_id(channel_id)
                    observer_comms = observer.comms_by_channel_id(channel_id)

                    if link_type == "uplink":
                        rx = target_comms
                        tx = observer_comms
                    else:
                        rx = observer_comms
                        tx = target_comms

                    if not rx.receiver or not tx.transmitter:
                        continue

                    for gs_pass in passes:
                        t0 = gs_pass.window.start
                        t1 = gs_pass.window.stop
                        times = [float(t - t0) for t in gs_pass.times]
                        func = partial(
                            lambda t,
                            gs_pass,
                            channel,
                            link_type,
                            target,
                            observer,
                            target_comms,
                            observer_comms,
                            ensemble,
                            with_environmental_losses,
                            percentage_exceed,
                            min_elevation_deg: _viability(
                                t,
                                gs_pass=gs_pass,
                                channel=channel,
                                link_type=link_type,
                                target=target,
                                observer=observer,
                                target_comms=target_comms,
                                observer_comms=observer_comms,
                                with_environmental_losses=with_environmental_losses,
                                percentage_exceed=percentage_exceed,
                                min_elevation_deg=min_elevation_deg,
                                ensemble=ensemble,
                            ),
                            gs_pass=gs_pass,
                            channel=channel,
                            link_type=link_type,
                            target=target,
                            observer=observer,
                            target_comms=target_comms,
                            observer_comms=observer_comms,
                            ensemble=ensemble,
                            with_environmental_losses=self.with_environmental_losses,
                            percentage_exceed=self.percentage_exceed,
                            min_elevation_deg=self.min_elevation_deg,
                        )

                        windows = lox.find_windows(
                            func,
                            t0._time,
                            t1._time,
                            times,
                        )

                        for w in windows:
                            window = Window._from_lox(w)
                            times = window.start.trange(window.stop, self.scenario.time_step)
                            stats = [
                                LinkStats.calculate(
                                    t,
                                    channel,
                                    link_type,
                                    target,
                                    observer,
                                    target_comms,
                                    observer_comms,
                                    EnvironmentalLosses.calculate(
                                        self.percentage_exceed,
                                        t,
                                        observer,
                                        target_comms,
                                        observer_comms,
                                        gs_pass,
                                        self.min_elevation_deg,
                                    )
                                    if self.with_environmental_losses
                                    else EnvironmentalLosses.no_losses(),
                                    ensemble,
                                )
                                for i, t in enumerate(times)
                            ]
                            links[target_id][observer_id].append(
                                Link(window=window, link_type=link_type, stats=stats, times=times)
                            )

        results = LinkBudgetResults(links=links)

        # Apply interference analysis if enabled
        if self.with_interference:
            self._analyze_uplink_interference(results, ensemble, visibility)
            self._analyze_downlink_interference(results, ensemble, visibility)
            # Ensure all links have interference stats, even if zero interference
            self._ensure_all_links_have_interference_stats(results)

        return results

    def _analyze_uplink_interference(
        self, results: LinkBudgetResults, ensemble: Ensemble, visibility: VisibilityResults
    ) -> None:
        """Analyze uplink interference in the link budget results."""
        for target_id, target_passes in results.links.items():
            # Target=spacecraft
            target = self.scenario[target_id]
            if not isinstance(target.model, Spacecraft):
                continue

            for observer_id, links in target_passes.items():
                observer = self.scenario[observer_id]
                if not isinstance(observer.model, GroundStation):
                    continue

                for i_link, link in enumerate(links):
                    if link.link_type != "uplink":
                        continue

                    if not link.stats:
                        continue

                    # Calculate interference from ALL ground stations, not just those with viable links
                    interference_powers = self._calculate_uplink_interference_from_all_ground_stations(
                        link, target, observer, ensemble, visibility
                    )

                    # Adding interference metrics to link stats
                    link_stats_with_interf = []
                    for link_stat, interference_power_w in zip(link.stats, interference_powers, strict=False):
                        link_stats_with_interf.append(link_stat.add_interference(interference_power_w))

                    results.links[target_id][observer_id][i_link].stats = link_stats_with_interf

    def _calculate_uplink_interference_from_all_ground_stations(
        self, link: Link, target: Asset, observer: Asset, ensemble: Ensemble, visibility: VisibilityResults
    ) -> np.ndarray:
        """Calculate interference power from all ground stations visible during the link window."""
        # Initialize interference power array
        interference_powers_w = np.zeros(len(link.stats))

        # Get link parameters
        if not link.stats:
            return interference_powers_w

        link_channel = None
        for channel in self.scenario.channels:
            if channel.link_type == link.link_type:
                link_channel = channel
                break

        if not link_channel:
            return interference_powers_w

        # Get receiver system on spacecraft
        target_comms = target.comms_by_channel_id(link_channel.channel_id)
        if not target_comms or not target_comms.receiver:
            return interference_powers_w

        link_freq = link.stats[0].frequency.hertz
        link_bw = link.stats[0].bandwidth

        # Check all ground stations in the scenario
        for asset in self.scenario.all_assets:
            if asset.asset_id == observer.asset_id:
                continue  # Skip the main transmitter

            if not isinstance(asset.model, GroundStation):
                continue  # Only ground stations can interfere in uplink

            # Check if this ground station has a transmitter on a compatible channel
            for comms in asset.comms:
                if not comms.transmitter:
                    continue

                # Check frequency overlap
                tx_freq = comms.transmitter.frequency.hertz
                tx_bw = link_channel.bandwidth  # Use channel bandwidth
                overlap_factor = _get_overlap_factor(link_freq, link_bw, tx_freq, tx_bw)

                if overlap_factor <= 0.0:
                    continue  # No frequency overlap

                # Check if interfering ground station has visibility with the spacecraft
                interferer_passes = visibility.passes.get(target.asset_id, {}).get(asset.asset_id, [])
                if not interferer_passes:
                    continue  # No visibility between interferer and spacecraft

                # Calculate interference for each time in the link
                for i, (time, _link_stat) in enumerate(zip(link.times, link.stats, strict=False)):
                    # Check if time is within any visibility window
                    visible = False
                    for pass_ in interferer_passes:
                        if pass_.window.start._time <= time._time <= pass_.window.stop._time:
                            visible = True
                            break

                    if not visible:
                        continue  # Interferer not visible at this time

                    try:
                        sc_state = ensemble[target].interpolate(time)
                        obs = asset.model.observables(sc_state)

                        # Calculate received power from interferer
                        slant_range = obs.rng  # Already in km

                        # Calculate angles for link budget
                        tx_angle = _off_boresight_angle(time, ensemble, asset, target, comms)
                        rx_angle = _off_boresight_angle(time, ensemble, target, asset, target_comms)

                        # Calculate carrier power at receiver
                        carrier_rx_power_dbw = comms.carrier_power(
                            target_comms,
                            0.0,  # No environmental losses for interference
                            slant_range,
                            tx_angle,
                            rx_angle,
                        )

                        # Convert to watts and apply frequency overlap factor
                        carrier_rx_power_w = from_db(carrier_rx_power_dbw)
                        interference_powers_w[i] += overlap_factor * carrier_rx_power_w

                    except (KeyError, ValueError):
                        # Skip if we can't calculate interference from this source
                        continue

        return interference_powers_w

    def _analyze_downlink_interference(
        self, results: LinkBudgetResults, ensemble: Ensemble, visibility: VisibilityResults
    ) -> None:
        """Analyze downlink interference in the link budget results."""
        for target_id, target_passes in results.links.items():
            # Target=spacecraft
            target = self.scenario[target_id]
            if not isinstance(target.model, Spacecraft):
                continue

            for observer_id, links in target_passes.items():
                observer = self.scenario[observer_id]
                if not isinstance(observer.model, GroundStation):
                    continue

                for i_link, link in enumerate(links):
                    if link.link_type != "downlink":
                        continue

                    if not link.stats:
                        continue

                    # Calculate interference from ALL satellites, not just those with viable links
                    interference_powers = self._calculate_downlink_interference_from_all_satellites(
                        link, target, observer, ensemble, visibility
                    )

                    # Adding interference metrics to link stats
                    link_stats_with_interf = []
                    for link_stat, interference_power_w in zip(link.stats, interference_powers, strict=False):
                        link_stats_with_interf.append(link_stat.add_interference(interference_power_w))

                    results.links[target_id][observer_id][i_link].stats = link_stats_with_interf

    def _calculate_downlink_interference_from_all_satellites(
        self, link: Link, target: Asset, observer: Asset, ensemble: Ensemble, visibility: VisibilityResults
    ) -> np.ndarray:
        """Calculate interference power from all satellites visible during the link window."""
        # Initialize interference power array
        interference_powers_w = np.zeros(len(link.stats))

        # Get link parameters
        if not link.stats:
            return interference_powers_w

        link_channel = None
        for channel in self.scenario.channels:
            if channel.link_type == link.link_type:
                link_channel = channel
                break

        if not link_channel:
            return interference_powers_w

        # Get receiver system
        observer_comms = observer.comms_by_channel_id(link_channel.channel_id)
        if not observer_comms or not observer_comms.receiver:
            return interference_powers_w

        link_freq = link.stats[0].frequency.hertz
        link_bw = link.stats[0].bandwidth

        # Check all spacecraft in the scenario
        for asset in self.scenario.all_assets:
            if asset.asset_id == target.asset_id:
                continue  # Skip the main transmitter

            if not isinstance(asset.model, Spacecraft):
                continue  # Only spacecraft can interfere in downlink

            # Check if this spacecraft has a transmitter on a compatible channel
            for comms in asset.comms:
                if not comms.transmitter:
                    continue

                # Check frequency overlap
                tx_freq = comms.transmitter.frequency.hertz
                tx_bw = link_channel.bandwidth  # Use channel bandwidth
                overlap_factor = _get_overlap_factor(link_freq, link_bw, tx_freq, tx_bw)

                if overlap_factor <= 0.0:
                    continue  # No frequency overlap

                # Check if interferer has visibility with the ground station
                interferer_passes = visibility.passes.get(asset.asset_id, {}).get(observer.asset_id, [])
                if not interferer_passes:
                    continue  # No visibility between interferer and ground station

                # Calculate interference for each time in the link
                for i, (time, _link_stat) in enumerate(zip(link.times, link.stats, strict=False)):
                    # Check if time is within any visibility window
                    visible = False
                    for pass_ in interferer_passes:
                        if pass_.window.start._time <= time._time <= pass_.window.stop._time:
                            visible = True
                            break

                    if not visible:
                        continue  # Interferer not visible at this time

                    try:
                        interferer_state = ensemble[asset].interpolate(time)
                        obs = observer.model.observables(interferer_state)

                        # Calculate received power from interferer
                        slant_range = obs.rng  # Already in km

                        # Calculate angles for link budget
                        tx_angle = _off_boresight_angle(time, ensemble, asset, observer, comms)
                        rx_angle = _off_boresight_angle(time, ensemble, observer, asset, observer_comms)

                        # Calculate carrier power at receiver
                        carrier_rx_power_dbw = comms.carrier_power(
                            observer_comms,
                            0.0,  # No environmental losses for interference
                            slant_range,
                            tx_angle,
                            rx_angle,
                        )

                        # Convert to watts and apply frequency overlap factor
                        carrier_rx_power_w = from_db(carrier_rx_power_dbw)
                        interference_powers_w[i] += overlap_factor * carrier_rx_power_w

                    except (KeyError, ValueError):
                        # Skip if we can't calculate interference from this source
                        continue

        return interference_powers_w

    def _ensure_all_links_have_interference_stats(self, results: LinkBudgetResults) -> None:
        """Ensure all links have interference stats, adding zero interference if not present."""
        for target_id, target_passes in results.links.items():
            for observer_id, links in target_passes.items():
                for i_link, link in enumerate(links):
                    # Check if any link stats are missing interference data
                    stats_with_interference = []
                    for link_stat in link.stats:
                        if link_stat.interference_stats is None:
                            # Add zero interference stats
                            stats_with_interference.append(link_stat.add_interference(0.0))
                        else:
                            stats_with_interference.append(link_stat)
                    results.links[target_id][observer_id][i_link].stats = stats_with_interference


def _viability(
    t: float,
    *,
    gs_pass: Pass,
    channel: Channel,
    link_type: Literal["uplink", "downlink"],
    target: Asset,
    observer: Asset,
    target_comms: CommunicationSystem,
    observer_comms: CommunicationSystem,
    with_environmental_losses: bool,
    percentage_exceed: float,
    min_elevation_deg: float,
    ensemble: Ensemble,
) -> float:
    time = gs_pass.window.start + TimeDelta(t)

    # Calculate environmental losses dynamically for this specific time
    losses = (
        EnvironmentalLosses.calculate(
            percentage_exceed,
            time,
            observer,
            target_comms,
            observer_comms,
            gs_pass,
            min_elevation_deg,
        )
        if with_environmental_losses
        else EnvironmentalLosses.no_losses()
    )

    # Reuse LinkStats.calculate to avoid code duplication
    link_stats = LinkStats.calculate(
        time, channel, link_type, target, observer, target_comms, observer_comms, losses, ensemble
    )

    return link_stats.margin


def _are_time_wins_overlapping(w1_start: Time, w1_end: Time, w2_start: Time, w2_end: Time) -> bool:
    """
    Check if two time windows are overlapping.

    Parameters
    ----------
    w1_start : Time
        Start time of the first time window
    w1_end : Time
        End time of the first time window
    w2_start : Time
        Start time of the second time window
    w2_end : Time
        End time of the second time window

    Returns
    -------
    bool
        True if the time windows overlap, otherwise False
    """
    return ((w2_start - w1_end).to_decimal_seconds() <= 0) and ((w1_start - w2_end).to_decimal_seconds() <= 0)


def _get_overlap_factor(center_freq_1: float, bw1: float, center_freq_2: float, bw2: float) -> float:
    """
    Return overlap factor between two frequency bands.

    The factor is between 0 and 1 and represents the fraction of the interference
    bandwidth that overlaps with the receiver bandwidth. This matches MATLAB's
    implementation where the overlap is normalized by the interference bandwidth.

    Parameters
    ----------
    center_freq_1 : float
        Center frequency of the receiver (Hz)
    bw1 : float
        Bandwidth of the receiver (Hz)
    center_freq_2 : float
        Center frequency of the interferer (Hz)
    bw2 : float
        Bandwidth of the interferer (Hz)

    Returns
    -------
    float
        Overlap factor (0 to 1) representing fraction of interference power
        that falls within the receiver bandwidth
    """
    # Calculate frequency limits
    fmax_1 = center_freq_1 + bw1 / 2
    fmin_1 = center_freq_1 - bw1 / 2
    fmax_2 = center_freq_2 + bw2 / 2
    fmin_2 = center_freq_2 - bw2 / 2

    # Check if there's no overlap
    if fmax_2 < fmin_1 or fmin_2 > fmax_1:
        return 0.0

    # Calculate the overlapping bandwidth
    overlap_start = max(fmin_1, fmin_2)
    overlap_end = min(fmax_1, fmax_2)
    overlapping_bw = overlap_end - overlap_start

    # Normalize by the interference bandwidth (bw2) to get the fraction
    # of interference power that falls within the receiver bandwidth
    return overlapping_bw / bw2


def _get_interfering_power_w(ref_link: Link, interfering_link: Link) -> None | np.ndarray:
    """
    Compute the interference power between the reference link and the interfering link source.

    Parameters
    ----------
    ref_link : Link
        The link under interference
    interference_link : Link
        The link that interferes ref_link

    Returns
    -------
    np.ndarray or None
        The interference power in watts, an array as a function of time.
        Or None if there is no time window or frequency overlap between the two links
    """
    if not ref_link.stats:
        return

    if not interfering_link.stats:
        return

    interfering_power_w = np.zeros(len(ref_link.stats))
    link_freq = ref_link.stats[0].frequency.hertz
    link_bw = ref_link.stats[0].bandwidth
    t0 = ref_link.times[0]
    # Converting time to relative (seconds) for interpolation
    times_rel = [(time - t0).to_decimal_seconds() for time in ref_link.times]

    # Find passes for this spacecraft and these two ground stations which overlap in time
    if not _are_time_wins_overlapping(
        ref_link.window.start, ref_link.window.stop, interfering_link.window.start, interfering_link.window.stop
    ):
        return

    # Compute frequency band overlap
    other_link_freq = interfering_link.stats[0].frequency.hertz
    other_link_bw = interfering_link.stats[0].bandwidth
    overlap_factor = _get_overlap_factor(link_freq, link_bw, other_link_freq, other_link_bw)
    if overlap_factor <= 0.0:
        return

    other_times_rel = [(time - t0).to_decimal_seconds() for time in interfering_link.times]
    # Add interfering contribution, weighted by frequency band overlap
    interfering_power_w = overlap_factor * np.interp(
        times_rel,
        other_times_rel,
        from_db(np.array([s.carrier_rx_power for s in interfering_link.stats])),
        left=0,
        right=0,
    )

    return interfering_power_w
