"""The visibility.py module.

This module provides the `Visibility` class for conducting visibility analyses.
"""

import uuid
from concurrent.futures import ThreadPoolExecutor
from functools import cached_property
from typing import Literal, Self
from uuid import UUID

import lox_space as lox
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from pydantic import Field, computed_field

from ephemerista import BaseModel, ephemeris, get_eop_provider
from ephemerista.analysis import Analysis
from ephemerista.angles import Angle
from ephemerista.assets import GroundLocation, GroundStation, Observables, Spacecraft, _asset_id
from ephemerista.bodies import Origin
from ephemerista.scenarios import AssetKey, Ensemble, Scenario
from ephemerista.time import Time
from ephemerista.uuid_utils import EPHEMERISTA_NAMESPACE


class Window(BaseModel):
    """The `Window` class.

    This class models a visibility window.
    """

    start: Time = Field(description="Start time of the window.")
    stop: Time = Field(description="End time of the window.")

    @classmethod
    def _from_lox(cls, window: lox.Window) -> Self:
        return cls(start=Time._from_lox(window.start()), stop=Time._from_lox(window.end()))

    @computed_field
    @property
    def duration(self) -> float:
        """float: duration of the window in seconds."""
        return float(self.stop - self.start)


class Pass(BaseModel):
    """The `Pass` class.

    This class models a ground station pass and provides modelled observables.
    """

    window: Window = Field(description="The visibility window.")
    times: list[Time] = Field(description="Time steps for observables.")
    observables: list[Observables] = Field(description="Observables.")

    @cached_property
    def _range(self) -> lox.Series:
        """Lazily create range series."""
        t = [float(t - self.window.start) for t in self.times]
        return lox.Series(t, [obs.rng for obs in self.observables])

    @cached_property
    def _range_rate(self) -> lox.Series:
        """Lazily create range rate series."""
        t = [float(t - self.window.start) for t in self.times]
        return lox.Series(t, [obs.rng_rate for obs in self.observables])

    @cached_property
    def _azimuth(self) -> lox.Series:
        """Lazily create azimuth series."""
        t = [float(t - self.window.start) for t in self.times]
        return lox.Series(t, [obs.azimuth.radians for obs in self.observables])

    @cached_property
    def _elevation(self) -> lox.Series:
        """Lazily create elevation series."""
        t = [float(t - self.window.start) for t in self.times]
        return lox.Series(t, [obs.elevation.radians for obs in self.observables])

    def interpolate(self, time: Time) -> Observables:
        """Interpolate observables for a given time within the window."""
        t = float(time - self.window.start)
        return Observables(
            azimuth=Angle.from_radians(self._azimuth.interpolate(t)),
            elevation=Angle.from_radians(self._elevation.interpolate(t)),
            rng=self._range.interpolate(t),
            rng_rate=self._range_rate.interpolate(t),
        )

    def plot(self):
        """Plot the observables."""
        dts = [t.datetime for t in self.times]
        rng = [obs.rng for obs in self.observables]
        rng_rate = [obs.rng_rate for obs in self.observables]
        azimuth = [obs.azimuth.degrees for obs in self.observables]
        elevation = [obs.elevation.degrees for obs in self.observables]

        fig, ax = plt.subplots(2, 2, figsize=(12, 8))
        plt.subplots_adjust(hspace=0.3)

        fig.suptitle(f"Pass from {self.window.start.to_utc()} to {self.window.stop.to_utc()}")

        for a in ax.flat:
            a.xaxis.set_major_locator(mdates.HourLocator())
            a.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            a.xaxis.set_tick_params(rotation=45)
            a.grid()

        ax[0, 0].plot(dts, rng)
        ax[0, 0].set_title("Range")
        ax[0, 0].set_ylabel("km")

        ax[0, 1].plot(dts, rng_rate)
        ax[0, 1].set_title("Range Rate")
        ax[0, 1].set_ylabel("km/s")

        ax[1, 0].plot(dts, azimuth)
        ax[1, 0].set_title("Azimuth")
        ax[1, 0].set_ylabel("degrees")

        ax[1, 1].plot(dts, elevation)
        ax[1, 1].set_title("Elevation")
        ax[1, 1].set_ylabel("degrees")
        return fig

    def to_dataframe(self) -> pd.DataFrame:
        """Convert the pass observables to a Pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns for time, azimuth_deg, elevation_deg,
            range_km, and range_rate_km_s.
        """
        data = []
        for time, obs in zip(self.times, self.observables, strict=True):
            data.append(
                {
                    "time": time.datetime,
                    "azimuth_deg": obs.azimuth.degrees,
                    "elevation_deg": obs.elevation.degrees,
                    "range_km": obs.rng,
                    "range_rate_km_s": obs.rng_rate,
                }
            )

        return pd.DataFrame(data)


class VisibilityResults(BaseModel):
    """Results of the `Visibility` analysis."""

    results_type: Literal["visibility"] = Field(default="visibility", frozen=True, repr=False, alias="type")
    passes: dict[UUID, dict[UUID, list[Pass]]]

    def get(self, observer: AssetKey, target: AssetKey) -> list[Pass]:
        """Return all passes for a given observer and target combination."""
        target_passes = self.passes.get(_asset_id(target), {})
        return target_passes.get(_asset_id(observer), [])

    def __getitem__(self, key: tuple[AssetKey, AssetKey]) -> list[Pass]:
        """Return all passes for a given observer and target combination."""
        return self.get(*key)

    def total_duration(self, observer: AssetKey, target: AssetKey) -> float:
        """Return the sum of all visibility durations for a given observer and target combination."""
        return sum(p.window.duration for p in self.get(observer, target))

    def to_dataframe(self, observer: AssetKey, target: AssetKey) -> pd.DataFrame:
        """Convert the results to a Pandas DataFrame.

        Parameters
        ----------
        observer : AssetKey
            Observer asset key for the specific observer-target combination.
        target : AssetKey
            Target asset key for the specific observer-target combination.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns 'start', 'end', 'duration' for the specified
            observer-target combination.
        """
        passes = self.get(observer, target)
        data = []
        for p in passes:
            data.append(
                {
                    "start": p.window.start.datetime,
                    "end": p.window.stop.datetime,
                    "duration": p.window.duration,
                }
            )
        return pd.DataFrame(data)


class Visibility(Analysis[VisibilityResults]):
    """The `Visibility` analysis.

    This analysis finds windows of visibility between ground stations and spacecraft within the provided scenario.
    """

    scenario: Scenario
    start_time: Time | None = Field(default=None)
    end_time: Time | None = Field(default=None)
    bodies: list[Origin] = Field(default=[])
    use_ground_locations: bool = Field(default=False, description="Include ground locations from areas of interest")
    parallel: bool = Field(default=False, description="Use parallel execution with visibility_all from lox_space")

    def analyze(  # type: ignore
        self,
        ensemble: Ensemble | None = None,
    ) -> VisibilityResults:
        """Run the analysis."""
        if not ensemble:
            ensemble = self.scenario.propagate()

        if self.parallel:
            return self._analyze_parallel(ensemble)
        else:
            return self._analyze_sequential(ensemble)

    def _analyze_sequential(self, ensemble: Ensemble) -> VisibilityResults:
        """Run the analysis using the original sequential approach."""
        start_time = self.start_time or self.scenario.start_time
        end_time = self.end_time or self.scenario.end_time

        times = [time._time for time in start_time.trange(end_time, self.scenario.time_step)]

        bodies = [body._origin for body in self.bodies]

        passes: dict[UUID, dict[UUID, list[Pass]]] = {}

        # Pre-filter assets by type to avoid checking in the loop
        all_assets = self.scenario.all_assets
        spacecraft = [(a.asset_id, ensemble[a]) for a in all_assets if isinstance(a.model, Spacecraft)]

        # Collect observers based on configuration
        observers: list[tuple[UUID, GroundStation | GroundLocation]] = []

        # Always include ground station assets
        observers.extend([(a.asset_id, a.model) for a in all_assets if isinstance(a.model, GroundStation)])

        # Optionally include ground locations from areas of interest
        if self.use_ground_locations:
            # Create deterministic UUIDs for ground locations based on their index
            for i, loc in enumerate(self.scenario.ground_locations):
                # Create a deterministic UUID based on scenario ID and location index
                deterministic_id = uuid.uuid5(EPHEMERISTA_NAMESPACE, f"{self.scenario.scenario_id}:ground_location:{i}")
                observers.append((deterministic_id, loc))

        # Cache ephemeris and EOP provider to avoid repeated calls
        eph = ephemeris()
        eop = get_eop_provider()

        # Only iterate over valid observer/target combinations
        for observer_id, observer_model in observers:
            mask = lox.ElevationMask.fixed(observer_model.minimum_elevation.radians)

            for target_id, target_trajectory in spacecraft:
                windows = lox.visibility(
                    times,
                    observer_model._location,
                    mask,
                    target_trajectory._trajectory,
                    eph,
                    bodies,
                    eop,
                )

                if target_id not in passes:
                    passes[target_id] = {}

                passes[target_id][observer_id] = []

                for pass_obj in windows:
                    # lox.visibility_all now returns Pass objects directly!
                    # Convert lox Pass to Python Pass
                    window = Window._from_lox(pass_obj.window())
                    if window.duration == 0:
                        continue

                    # Convert lox times to Python times
                    pass_times = [Time._from_lox(t) for t in pass_obj.times()]

                    # Convert lox observables to Python observables
                    observables = [Observables._from_lox(obs) for obs in pass_obj.observables()]

                    passes[target_id][observer_id].append(
                        Pass(window=window, times=pass_times, observables=observables)
                    )

        return VisibilityResults(passes=passes)

    def _analyze_parallel(self, ensemble: Ensemble) -> VisibilityResults:
        """Run the analysis using parallel execution with lox.visibility_all."""
        start_time = self.start_time or self.scenario.start_time
        end_time = self.end_time or self.scenario.end_time

        times = [time._time for time in start_time.trange(end_time, self.scenario.time_step)]

        bodies = [body._origin for body in self.bodies] if self.bodies else None

        # Pre-filter assets by type to avoid checking in the loop
        all_assets = self.scenario.all_assets
        spacecraft_assets = [(a.asset_id, ensemble[a]) for a in all_assets if isinstance(a.model, Spacecraft)]

        # Collect observers based on configuration
        observers: list[tuple[UUID, GroundStation | GroundLocation]] = []

        # Always include ground station assets
        observers.extend([(a.asset_id, a.model) for a in all_assets if isinstance(a.model, GroundStation)])

        # Optionally include ground locations from areas of interest
        if self.use_ground_locations:
            # Create deterministic UUIDs for ground locations based on their index
            for i, loc in enumerate(self.scenario.ground_locations):
                # Create a deterministic UUID based on scenario ID and location index
                deterministic_id = uuid.uuid5(EPHEMERISTA_NAMESPACE, f"{self.scenario.scenario_id}:ground_location:{i}")
                observers.append((deterministic_id, loc))

        # Prepare ground stations dict for visibility_all
        ground_stations = {}
        observer_id_map = {}
        for observer_id, observer_model in observers:
            # Create string key for lox.visibility_all
            key = str(observer_id)
            ground_stations[key] = (
                observer_model._location,
                lox.ElevationMask.fixed(observer_model.minimum_elevation.radians),
            )
            observer_id_map[key] = observer_id

        # Prepare spacecraft ensemble for visibility_all
        # We need to create a new Ensemble with only spacecraft and map the keys
        spacecraft_id_map = {}
        spacecraft_ensemble_dict = {}
        for spacecraft_id, trajectory in spacecraft_assets:
            key = str(spacecraft_id)
            spacecraft_ensemble_dict[key] = trajectory
            spacecraft_id_map[key] = spacecraft_id

        # Create a new Ensemble with string keys for visibility_all
        spacecraft_ensemble = Ensemble(trajectories=spacecraft_ensemble_dict, ephemerides={})

        # Cache ephemeris and EOP provider to avoid repeated calls
        eph = ephemeris()
        eop = get_eop_provider()

        # Call lox.visibility_all with the internal lox.Ensemble
        visibility_results = lox.visibility_all(
            times,
            ground_stations,
            spacecraft_ensemble._ensemble,
            eph,
            bodies,
            eop,
        )

        # Convert results back to the expected format
        passes: dict[UUID, dict[UUID, list[Pass]]] = {}

        # Helper function to process spacecraft windows
        def process_spacecraft(spacecraft_data):
            spacecraft_key, observer_dict = spacecraft_data
            spacecraft_id = spacecraft_id_map[spacecraft_key]
            spacecraft_passes = {}

            for observer_key, windows in observer_dict.items():
                observer_id = observer_id_map[observer_key]
                observer_passes = []

                for pass_obj in windows:
                    # lox.visibility_all now returns Pass objects directly!
                    # Convert lox Pass to Python Pass
                    window = Window._from_lox(pass_obj.window())
                    if window.duration == 0:
                        continue

                    # Convert lox times to Python times
                    pass_times = [Time._from_lox(t) for t in pass_obj.times()]

                    # Convert lox observables to Python observables
                    observables = [Observables._from_lox(obs) for obs in pass_obj.observables()]

                    observer_passes.append(Pass(window=window, times=pass_times, observables=observables))

                spacecraft_passes[observer_id] = observer_passes

            return spacecraft_id, spacecraft_passes

        # Process spacecraft in parallel if there are multiple
        if len(visibility_results) > 1 and self.parallel:
            with ThreadPoolExecutor(max_workers=min(len(visibility_results), 4)) as executor:
                results = list(executor.map(process_spacecraft, visibility_results.items()))

            for spacecraft_id, spacecraft_passes in results:
                passes[spacecraft_id] = spacecraft_passes
        else:
            # Process sequentially for single spacecraft or non-parallel mode
            for spacecraft_key, observer_dict in visibility_results.items():
                spacecraft_id, spacecraft_passes = process_spacecraft((spacecraft_key, observer_dict))
                passes[spacecraft_id] = spacecraft_passes

        return VisibilityResults(passes=passes)
