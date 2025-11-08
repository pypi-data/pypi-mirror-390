"""The navigation.py module.

This module provides the `Navigation` class.
"""

from typing import Literal

import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from pydantic import UUID5, Field, computed_field
from scipy.interpolate import interp1d

from ephemerista import BaseModel
from ephemerista.analysis import Analysis
from ephemerista.assets import GroundStation, Spacecraft
from ephemerista.propagators.orekit.conversions import time_to_abs_date, trajectory_to_ephemeris
from ephemerista.scenarios import Ensemble, Scenario
from ephemerista.time import Time


class DilutionOfPrecision(BaseModel):
    """The `DilutionOfPrecision` class.

    This class models the dilution of precision for GNSS satellite constellation at a specific time.
    """

    time: Time = Field(description="Time vector representing each data point.")
    n_sats: int = Field(description="Number of GNSS satellites taken into account for DOP computation.")
    gdop: float = Field(description="Geometric Dilution of Precision.")
    hdop: float = Field(description="Horizontal Dilution of Precision.")
    pdop: float = Field(description="Position Dilution of Precision.")
    tdop: float = Field(description="Time Dilution of Precision.")
    vdop: float = Field(description="Vertical Dilution of Precision.")

    @classmethod
    def from_orekit(cls, time: Time, dop):
        """Convert from Orekit."""
        n_sats = dop.getGnssNb()
        gdop = dop.getGdop()
        hdop = dop.getHdop()
        pdop = dop.getPdop()
        tdop = dop.getTdop()
        vdop = dop.getVdop()
        return cls(time=time, n_sats=n_sats, gdop=gdop, hdop=hdop, pdop=pdop, tdop=tdop, vdop=vdop)


class PositionAccuracy(BaseModel):
    """The `PositionAccuracy` class.

    This class models the position accuracy derived from a Dilution of Precision and User Equivalent Range Error (UERE).
    """

    time: Time = Field(description="Time vector representing each data point.")
    gacc: float = Field(description="Geometric accuracy in meters.")
    hacc: float = Field(description="Horizontal accuracy in meters.")
    pacc: float = Field(description="Position accuracy in meters.")
    tacc: float = Field(description="Time accuracy in meters.")
    vacc: float = Field(description="Vertical accuracy in meters.")

    @classmethod
    def from_dop(cls, dop: DilutionOfPrecision, uere: float):
        """Create a PositionAccuracy from a DilutionOfPrecision and UERE."""
        return cls(
            time=dop.time,
            gacc=dop.gdop * uere,
            hacc=dop.hdop * uere,
            pacc=dop.pdop * uere,
            tacc=dop.tdop * uere,
            vacc=dop.vdop * uere,
        )


class DepthOfCoverage(BaseModel):
    """The `DepthOfCoverage` class.

    This class models the depth of coverage for an observer in a specific time frame.
    """

    min_sats: int = Field(description="Minimum number of visible satellites.")
    max_sats: int = Field(description="Maximum number of visible satellites.")


class NavigationResults(BaseModel):
    """The results of the `Navigation` analysis."""

    results_type: Literal["navigation"] = Field(default="navigation", frozen=True, repr=False, alias="type")
    dop: dict[UUID5, list[DilutionOfPrecision]]
    acc: dict[UUID5, list[PositionAccuracy]]

    @computed_field
    @property
    def depth_of_coverage(self) -> dict[UUID5, DepthOfCoverage]:
        return {
            asset_id: DepthOfCoverage(min_sats=min(d.n_sats for d in dop), max_sats=max(d.n_sats for d in dop))
            for asset_id, dop in self.dop.items()
        }

    def to_dataframe(self, observer: GroundStation) -> "pd.DataFrame":
        """Convert navigation results to a Pandas DataFrame for a specific observer.

        Parameters
        ----------
        observer : GroundStation
            The observer ground station.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns for time, n_sats, DOP values (gdop, hdop, pdop, tdop, vdop),
            and accuracy values (gacc, hacc, pacc, tacc, vacc).
        """
        dop_data = self.dop[observer.asset_id]
        acc_data = self.acc[observer.asset_id]

        data = []
        for dop, acc in zip(dop_data, acc_data, strict=True):
            data.append(
                {
                    "time": dop.time.datetime,
                    "n_sats": dop.n_sats,
                    "gdop": dop.gdop,
                    "hdop": dop.hdop,
                    "pdop": dop.pdop,
                    "tdop": dop.tdop,
                    "vdop": dop.vdop,
                    "gacc": acc.gacc,
                    "hacc": acc.hacc,
                    "pacc": acc.pacc,
                    "tacc": acc.tacc,
                    "vacc": acc.vacc,
                }
            )

        return pd.DataFrame(data)

    def plot(self, observer: UUID5):
        """Plot the dilution of precision for a given observer."""
        dop = self.dop[observer]
        dts = [d.time.datetime for d in dop]
        n_sats = [d.n_sats for d in dop]
        gdop = [d.gdop for d in dop]
        hdop = [d.hdop for d in dop]
        pdop = [d.pdop for d in dop]
        tdop = [d.tdop for d in dop]
        vdop = [d.vdop for d in dop]

        acc = self.acc[observer]
        gacc = [d.gacc for d in acc]
        hacc = [d.hacc for d in acc]
        pacc = [d.pacc for d in acc]
        tacc = [d.tacc for d in acc]
        vacc = [d.vacc for d in acc]

        fig, ax = plt.subplots(1, 3, figsize=(12, 8))
        plt.subplots_adjust(hspace=0.5)

        fig.suptitle(f"Navigation Performance from {dop[0].time.datetime.date()} to {dop[-1].time.datetime.date()}")

        for a in ax.flat:
            a.xaxis.set_major_locator(mdates.AutoDateLocator())
            a.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            a.xaxis.set_tick_params(rotation=45)
            a.grid()

        ax[0].plot(dts, n_sats)
        ax[0].set_title("Number of Visible Satellites")
        ax[1].plot(dts, gdop, label="GDOP")
        ax[1].plot(dts, hdop, label="HDOP")
        ax[1].plot(dts, pdop, label="PDOP")
        ax[1].plot(dts, tdop, label="TDOP")
        ax[1].plot(dts, vdop, label="VDOP")
        ax[1].set_title("Dilution of Precision")
        ax[1].legend(loc="upper right")
        ax[2].plot(dts, gacc, label="GACC")
        ax[2].plot(dts, hacc, label="HACC")
        ax[2].plot(dts, pacc, label="PACC")
        ax[2].plot(dts, tacc, label="TACC")
        ax[2].plot(dts, vacc, label="VACC")
        ax[2].set_title("Position Accuracy")
        ax[2].legend(loc="upper right")

        return fig


class Navigation(Analysis[NavigationResults]):
    """The `Navigation` analysis.

    This class analyses the dilution of precision and depth of coverage of a GNSS constellation for all observers in a
    given scenario.
    """

    scenario: Scenario = Field(description="The scenario used to perform the analysis")
    start_time: Time | None = Field(
        default=None, description="Start time (optional, if None the scenario's start time is used)"
    )
    end_time: Time | None = Field(
        default=None, description="End time (optional, if None the scenario's end time is used)"
    )
    uere: float = Field(
        gt=0.001,
        default=0.6,
        description="User Equivalent Range Error (UERE) or Pseudorange error in meters",
    )
    dop_time_step: float = Field(
        default=300.0, description="Time step for DOP computation in seconds (default 5 minutes)"
    )
    interpolate_results: bool = Field(
        default=True, description="Whether to interpolate DOP results to original time resolution"
    )

    def analyze(self, *, ensemble: Ensemble | None = None) -> NavigationResults:  # type: ignore
        """Run the analysis."""
        if not ensemble:
            ensemble = self.scenario.propagate()

        start_time = self.start_time or self.scenario.start_time
        end_time = self.end_time or self.scenario.end_time

        # Use original time resolution for final results
        times = start_time.trange(end_time, self.scenario.time_step)

        # Use coarser time step for DOP computations to improve performance
        dop_times = start_time.trange(end_time, self.dop_time_step)

        sc = {
            sc_id: tra
            for sc_id, tra in ensemble.trajectories.items()
            if isinstance(self.scenario[sc_id].model, Spacecraft)
        }
        observers = {
            asset.asset_id: asset.model for asset in self.scenario.all_assets if isinstance(asset.model, GroundStation)
        }

        from java.util import ArrayList  # type: ignore  # noqa: PLC0415

        # Cache ephemeris conversion (expensive operation)
        ephemerides = ArrayList([trajectory_to_ephemeris(t) for t in sc.values()])

        # Cache Orekit objects and computers to avoid repeated expensive setup        acc = {}

        from org.orekit.bodies import (  # type: ignore  # noqa: PLC0415
            CelestialBodyFactory,
            GeodeticPoint,
            OneAxisEllipsoid,
        )
        from org.orekit.gnss import DOPComputer  # type: ignore  # noqa: PLC0415

        # Pre-create all DOP computers (cache expensive object creation)
        computers = {}
        for obs_id, observer in observers.items():
            r_e = observer.body.equatorial_radius
            f = observer.body.flattening
            frame = CelestialBodyFactory.getBody(observer.body.name).getBodyOrientedFrame()
            shape = OneAxisEllipsoid(r_e, f, frame)
            point = GeodeticPoint(observer.latitude.radians, observer.longitude.radians, observer.altitude)
            computers[obs_id] = DOPComputer.create(shape, point)

        # Compute DOP at reduced frequency for performance
        dop_sparse = {}
        acc = {}
        for obs_id, computer in computers.items():
            dop_sparse[obs_id] = [
                DilutionOfPrecision.from_orekit(t, computer.compute(time_to_abs_date(t), ephemerides))  # type: ignore
                for t in dop_times
            ]
            acc[obs_id] = [PositionAccuracy.from_dop(d, self.uere) for d in dop_sparse[obs_id]]

        # Interpolate to original time resolution if requested
        if self.interpolate_results and len(dop_times) != len(times):
            dop = self._interpolate_dop(dop_sparse, dop_times, times)
            acc = self._interpolate_acc(acc, dop_times, times)
        else:
            dop = dop_sparse

        return NavigationResults(dop=dop, acc=acc)

    def _interpolate_dop(self, dop_sparse: dict, dop_times: list[Time], target_times: list[Time]) -> dict:
        """Interpolate DOP values from sparse computation to target time resolution."""
        dop_interpolated = {}

        # Convert times to seconds for interpolation
        dop_times_sec = np.array([float(t - dop_times[0]) for t in dop_times])
        target_times_sec = np.array([float(t - dop_times[0]) for t in target_times])

        for obs_id, dop_values in dop_sparse.items():
            # Extract DOP components for interpolation
            gdop_values = np.array([dop.gdop for dop in dop_values])
            hdop_values = np.array([dop.hdop for dop in dop_values])
            pdop_values = np.array([dop.pdop for dop in dop_values])
            tdop_values = np.array([dop.tdop for dop in dop_values])
            vdop_values = np.array([dop.vdop for dop in dop_values])
            n_sats_values = np.array([dop.n_sats for dop in dop_values])

            # Create interpolation functions
            gdop_interp = interp1d(
                dop_times_sec, gdop_values, kind="linear", bounds_error=False, fill_value="extrapolate"
            )
            hdop_interp = interp1d(
                dop_times_sec, hdop_values, kind="linear", bounds_error=False, fill_value="extrapolate"
            )
            pdop_interp = interp1d(
                dop_times_sec, pdop_values, kind="linear", bounds_error=False, fill_value="extrapolate"
            )
            tdop_interp = interp1d(
                dop_times_sec, tdop_values, kind="linear", bounds_error=False, fill_value="extrapolate"
            )
            vdop_interp = interp1d(
                dop_times_sec, vdop_values, kind="linear", bounds_error=False, fill_value="extrapolate"
            )
            n_sats_interp = interp1d(
                dop_times_sec, n_sats_values, kind="nearest", bounds_error=False, fill_value="extrapolate"
            )

            # Interpolate to target times
            dop_interpolated[obs_id] = [
                DilutionOfPrecision(
                    time=t,
                    n_sats=int(n_sats_interp(t_sec)),
                    gdop=float(gdop_interp(t_sec)),
                    hdop=float(hdop_interp(t_sec)),
                    pdop=float(pdop_interp(t_sec)),
                    tdop=float(tdop_interp(t_sec)),
                    vdop=float(vdop_interp(t_sec)),
                )
                for t, t_sec in zip(target_times, target_times_sec, strict=True)
            ]

        return dop_interpolated

    def _interpolate_acc(self, acc_sparse: dict, dop_times: list[Time], target_times: list[Time]) -> dict:
        """Interpolate accuracy values from sparse computation to target time resolution."""
        acc_interpolated = {}

        # Convert times to seconds for interpolation
        dop_times_sec = np.array([float(t - dop_times[0]) for t in dop_times])
        target_times_sec = np.array([float(t - dop_times[0]) for t in target_times])

        for obs_id, acc_values in acc_sparse.items():
            # Extract accuracy components for interpolation
            gacc_values = np.array([acc.gacc for acc in acc_values])
            hacc_values = np.array([acc.hacc for acc in acc_values])
            pacc_values = np.array([acc.pacc for acc in acc_values])
            tacc_values = np.array([acc.tacc for acc in acc_values])
            vacc_values = np.array([acc.vacc for acc in acc_values])

            # Create interpolation functions
            gacc_interp = interp1d(
                dop_times_sec, gacc_values, kind="linear", bounds_error=False, fill_value="extrapolate"
            )
            hacc_interp = interp1d(
                dop_times_sec, hacc_values, kind="linear", bounds_error=False, fill_value="extrapolate"
            )
            pacc_interp = interp1d(
                dop_times_sec, pacc_values, kind="linear", bounds_error=False, fill_value="extrapolate"
            )
            tacc_interp = interp1d(
                dop_times_sec, tacc_values, kind="linear", bounds_error=False, fill_value="extrapolate"
            )
            vacc_interp = interp1d(
                dop_times_sec, vacc_values, kind="linear", bounds_error=False, fill_value="extrapolate"
            )

            # Interpolate to target times
            acc_interpolated[obs_id] = [
                PositionAccuracy(
                    time=t,
                    gacc=float(gacc_interp(t_sec)),
                    hacc=float(hacc_interp(t_sec)),
                    pacc=float(pacc_interp(t_sec)),
                    tacc=float(tacc_interp(t_sec)),
                    vacc=float(vacc_interp(t_sec)),
                )
                for t, t_sec in zip(target_times, target_times_sec, strict=True)
            ]

        return acc_interpolated
