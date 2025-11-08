"""The groundtrack.py module.

This module provides the `GroundTrack` class for plotting satellite ground tracks with plotly.
"""

from typing import Literal

import lox_space as lox
import numpy as np
import plotly.graph_objects as go

from ephemerista.assets import Asset, GroundStation
from ephemerista.coords.trajectories import Trajectory

DEFAULT_CONFIG = {
    "ground_track_color": "rgb(248,248,255)",
    "land_color": "rgb(169,169,169)",
    "ocean_color": "rgb(47,79,79)",
    "ground_station_color": "rgb(68,178,0)",
    "ground_station_size": 8,
    "plotly_theme": "plotly_dark",
    "grid_color": "rgb(102, 102, 102)",
}


class GroundTrack:
    """A class for plotting satellite ground tracks in various projections."""

    def __init__(
        self,
        trajectory: Trajectory,
        *,
        animate: bool = False,
        label: str | None = None,
        title: str | None = None,
        projection: str | None = None,
        config: dict[str, str] | None = None,
    ) -> None:
        self.config = config if config else {} | DEFAULT_CONFIG
        self.fig = go.Figure(go.Scattergeo())

        # Update to relevant theme. Default: dark mode
        self.fig.update_layout(template=self.config["plotly_theme"])

        self.trajectory = trajectory
        self.projection = projection if projection else "orthographic"

        self.label = label if label else "My Satellite"
        self.title = title if title else f"{self.label} GroundTrack"
        self.ground_station_trace = []

        # Plot a naked Earth
        self._trace_earth()

        if animate:
            self.animate()
        else:
            # Plot the ground track
            self.fig.add_trace(self._trace_groundtrack(self.trajectory))

    def animate(self, *, show=True):
        """Animate the ground track plot.

        Parameters
        ----------
        show: bool, optional
            Update the plot or pass show=True to display the plot immediately. Defaults to True.
        """
        # Compute the ground track once
        self.ground_track_trace = self._trace_groundtrack(self.trajectory, name=f"{self.label}")

        # Compute & trace the spacecraft's position at every epoch
        self._animate_groundtrack()

        if show:
            self.fig.show()

    def _trace_earth(self) -> None:
        self.fig.update_layout(
            title_text=self.title,
            # showlegend=False,
            geo={
                "showland": True,
                "showcountries": True,
                "showcoastlines": True,
                "showocean": True,
                "countrywidth": 0.5,
                "landcolor": self.config["land_color"],
                "lakecolor": self.config["ocean_color"],
                "oceancolor": self.config["ocean_color"],
                "projection": {"type": self.projection},
                "lonaxis": {"showgrid": True, "gridcolor": self.config["grid_color"], "gridwidth": 0.5},
                "lataxis": {"showgrid": True, "gridcolor": self.config["grid_color"], "gridwidth": 0.5},
            },
        )

    def _ephemeris_j2000_to_itrs(self, trajectory: Trajectory) -> tuple[np.ndarray, np.ndarray]:
        ground_locations = [
            state.to_frame(lox.Frame("IAU_EARTH")).to_ground_location() for state in trajectory._trajectory.states()
        ]
        lon = np.degrees(np.array([loc.longitude() for loc in ground_locations]))
        lat = np.degrees(np.array([loc.latitude() for loc in ground_locations]))
        return lon, lat

    def _trace_groundtrack(self, trajectory: Trajectory, name=None) -> go.Scattergeo:
        # Convert ephemeris to lat/lon
        lon, lat = self._ephemeris_j2000_to_itrs(trajectory)

        # Return ground track
        return go.Scattergeo(
            lat=lat,
            lon=lon,
            hovertext=trajectory.datetimes,
            mode="lines",
            name=name if name else f"{self.label} Groundtrack",
            line={"color": "rgb(253,245,230)"},
        )

    def plot_groundstation(
        self,
        gs: Asset,
        color: str | None = None,
        size: float | None = None,
        name: str | None = None,
        hovertext: str | None = None,
    ) -> None:
        """Plot a `GroundStation`'s location on the map.

        Parameters
        ----------
        gs: GroundStation)
            Ground station object
        color: str, optional)
            Colour of the ground station marker. Defaults to DEFAULT_GROUND_STATION_COLOR.
        size: float, optional)
            Size of the ground station marker. Defaults to DEFAULT_GROUND_STATION_SIZE.
        name: str, optional)
            Name of the ground station. Defaults to `GroundStation.name`.
        hovertext: str, optional)
            Desired hover text info for the ground station. Defaults to `GroundStation.name`.
        """
        if not isinstance(gs.model, GroundStation):
            msg = "Asset is not a GroundStation object"
            raise ValueError(msg)
        # Define the marker
        marker = {
            "size": size if size else self.config["ground_station_size"],
            "color": color if color else self.config["ground_station_color"],
            "line": {"width": 2, "color": color if color else self.config["ground_station_color"]},
            "symbol": "circle",
            "opacity": 0.7,
        }

        trace = go.Scattergeo(
            name=gs.name if not name else name,
            lat=[gs.model.latitude.degrees],
            lon=[gs.model.longitude.degrees],
            mode="markers",
            marker=marker,
            hovertext=f"{gs.name}" if not hovertext else hovertext,
        )

        self.ground_station_trace.append(trace)
        self.fig.add_trace(trace)

    def plot_ground_station_network(
        self,
        network: list[Asset],
        color: str | None = None,
        size: float | None = None,
    ):
        """Plot the locations of all ground stations in a list on the map.

        Parameters
        ----------
        network: list[GroundStation]:
            A list of ground stations
        color: str, optional
            Colour of the ground station marker. Defaults to DEFAULT_GROUND_STATION_COLOR.
        size: float, optional
            Size of the ground station marker. Defaults to DEFAULT_GROUND_STATION_SIZE.
        """
        color = color if color else self.config["ground_station_color"]
        size = size if size else float(self.config["ground_station_size"])

        for station in network:
            self.plot_groundstation(station, color, size)

        return self.fig.show()

    def update_projection(self, p: Literal["orthographic", "equirectangular"]) -> None:
        """Update the map projection."""
        self.fig.update_geos(projection_type=p)
        self.projection = p

    def plot(self):
        """Plot the ground track."""
        return self.fig.show()
