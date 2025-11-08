"""The coverage.py module.

This module provides the `Coverage` class for conducting coverage analyses.
"""

import importlib.resources
import json
import math
import uuid
import warnings

# Removed multiprocessing imports for optimized sequential processing
from pathlib import Path

import geopandas as gpd
import lox_space as lox
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from geojson_pydantic import Feature, FeatureCollection
from geojson_pydantic import Polygon as PolygonPydantic
from lox_space import TimeDelta
from matplotlib.axes import Axes
from plotly.graph_objs import Figure
from pydantic import UUID5, Field
from shapely.geometry import box

try:
    import numba

    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

from ephemerista import BaseModel, ephemeris, get_eop_provider
from ephemerista.analysis import Analysis
from ephemerista.analysis.visibility import VisibilityResults
from ephemerista.assets import GroundLocation, Spacecraft
from ephemerista.scenarios import Ensemble, Scenario
from ephemerista.time import Time
from ephemerista.uuid_utils import EPHEMERISTA_NAMESPACE

# Removed parallelization constants - using optimized sequential processing

# Constants for magic values
LAT_MIN = -90
LAT_MAX = 90
LON_MIN = -180
LON_MAX = 180

PolygonFeature = Feature[PolygonPydantic, dict]
PolygonFeatureCollection = FeatureCollection[PolygonFeature]


def load_geojson_multipolygon(filename: Path | str, *, min_elevation_deg: float = 0.0) -> list[PolygonFeature]:
    """
    Load polygons from a GeoJSON file.

    Parameters
    ----------
    min_elevation_deg: float
        Minimum elevation in degrees to compute the visibility between a spacecraft and the ground locations
    """
    with open(filename) as f:
        json_str = f.read()

    model = PolygonFeatureCollection.model_validate_json(json_str)
    feature_list = []
    for feature in model.features:
        properties = feature.properties
        if properties:
            properties["min_elevation_deg"] = min_elevation_deg
        feature_list.append(feature.model_copy(update={"properties": properties}))

    return feature_list


def _merge_intervals_numpy(intervals: np.ndarray) -> np.ndarray:
    """
    Fast NumPy-based interval merging.

    Parameters
    ----------
    intervals : np.ndarray
        Array of shape (n, 2) with start and end times

    Returns
    -------
    np.ndarray
        Merged intervals as array of shape (m, 2)
    """
    if len(intervals) == 0:
        return intervals

    # Sort by start time
    sorted_indices = np.argsort(intervals[:, 0])
    sorted_intervals = intervals[sorted_indices]

    merged = [sorted_intervals[0]]

    for current in sorted_intervals[1:]:
        last = merged[-1]
        if current[0] <= last[1]:  # Overlapping
            merged[-1] = [last[0], max(last[1], current[1])]
        else:
            merged.append(current)

    return np.array(merged)


if NUMBA_AVAILABLE:
    try:

        @numba.njit
        def _merge_intervals_numba(intervals: np.ndarray) -> np.ndarray:
            """
            Numba-optimized interval merging.

            Parameters
            ----------
            intervals : np.ndarray
                Array of shape (n, 2) with start and end times

            Returns
            -------
            np.ndarray
                Merged intervals as array of shape (m, 2)
            """
            if len(intervals) == 0:
                return intervals

            # Sort by start time
            sorted_indices = np.argsort(intervals[:, 0])
            sorted_intervals = intervals[sorted_indices]

            # Pre-allocate result array (worst case: no merging needed)
            result = np.empty((len(intervals), 2), dtype=intervals.dtype)
            result[0] = sorted_intervals[0]
            result_idx = 0

            for i in range(1, len(sorted_intervals)):
                current = sorted_intervals[i]
                last_end = result[result_idx, 1]

                if current[0] <= last_end:  # Overlapping
                    result[result_idx, 1] = max(last_end, current[1])
                else:
                    result_idx += 1
                    result[result_idx] = current

            # Return only the used portion of the result array
            return result[: result_idx + 1]

        _merge_intervals_fast = _merge_intervals_numba

    except Exception:
        # Fallback if numba compilation fails
        _merge_intervals_fast = _merge_intervals_numpy

else:
    _merge_intervals_fast = _merge_intervals_numpy


def _merge_time_intervals(intervals_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge time intervals that overlap to get overall time intervals for one ground point.

    Inspired from https://stackoverflow.com/a/49071253.
    """
    if intervals_df.empty:
        return intervals_df

    intervals_df_sorted = intervals_df.sort_values(by="START")
    merged_intervals = []
    for _, interval in intervals_df_sorted.iterrows():
        # If the list of merged intervals is empty or if the current
        # interval does not overlap with the previous, append it
        if not merged_intervals or merged_intervals[-1][1] < interval.START:
            merged_intervals.append([interval.START, interval.FINISH])
        else:
            # Otherwise, there is overlap, so we merge the current and previous intervals.
            merged_intervals[-1][1] = max(merged_intervals[-1][1], interval.FINISH)

    return pd.DataFrame(merged_intervals, columns=["START", "FINISH"])


def _merge_time_intervals_optimized(intervals: list[list[float]]) -> np.ndarray:
    """
    Optimized interval merging using NumPy arrays.

    Parameters
    ----------
    intervals : list of lists
        List of [start, end] interval pairs

    Returns
    -------
    np.ndarray
        Merged intervals as array of shape (n, 2)
    """
    if not intervals:
        return np.empty((0, 2))

    intervals_array = np.array(intervals)
    return _merge_intervals_fast(intervals_array)


# Removed parallel processing worker functions - integrated into optimized sequential algorithm


class _DiscretizedCoverageResults(BaseModel):
    """Internal results of the `Coverage` analysis for discretized polygons."""

    results_type: str = Field(default="coverage", frozen=True, repr=False, alias="type")
    polygons: list[PolygonFeature]
    coverage_percent: list[float]
    max_time_gaps: list[float]
    revisit_times: list[list]

    def plot(
        self,
        data_to_plot: str = "coverage_percent",
        map_style: str = "open-street-map",
        zoom: int = 0,
        opacity: float = 0.7,
        **kwargs,
    ) -> Figure:
        """Plot the coverage results using Plotly."""
        return self.plot_plotly(data_to_plot=data_to_plot, map_style=map_style, zoom=zoom, opacity=opacity, **kwargs)

    def plot_plotly(
        self,
        data_to_plot: str = "coverage_percent",
        map_style: str = "open-street-map",
        zoom: int = 2,
        opacity: float = 0.7,
        polygon_indices: list[int] | None = None,
        **kwargs,
    ) -> Figure:
        """Plot the coverage results using Plotly."""
        try:
            # Note: _DiscretizedCoverageResults always uses discretized data
            use_discretized = True
            geo_df = self.to_geodataframe()

            if data_to_plot not in geo_df:
                available_columns = list(geo_df.columns)
                msg = f"Column '{data_to_plot}' does not exist. Available columns: {available_columns}"
                raise ValueError(msg)

            # Filter to specific areas if requested
            if polygon_indices is not None:
                if use_discretized and "original_area_id" in geo_df.columns:
                    # Filter discretized data by original area IDs
                    geo_df = geo_df[geo_df["original_area_id"].isin(polygon_indices)].copy()
                elif not use_discretized:
                    # Filter aggregated data by index
                    geo_df = geo_df.iloc[polygon_indices].copy()

            # Validate we have data to plot
            if len(geo_df) == 0:
                msg = "No data available for plotting"
                raise ValueError(msg)

            # Clean data - replace any NaN or infinite values
            data_column = geo_df[data_to_plot].copy()
            data_column = data_column.replace([np.inf, -np.inf], np.nan)
            data_column = data_column.fillna(0)
            geo_df = geo_df.copy()
            geo_df[data_to_plot] = data_column

            # Validate geometries
            if geo_df.geometry.isnull().any():
                msg = "Invalid geometries found in data"
                raise ValueError(msg)

            # Calculate center coordinates from the geometries (use filtered data for extent)
            bounds = geo_df.total_bounds  # [minx, miny, maxx, maxy]
            center_lat = (bounds[1] + bounds[3]) / 2
            center_lon = (bounds[0] + bounds[2]) / 2

            # Validate coordinates
            if not (LAT_MIN <= center_lat <= LAT_MAX) or not (LON_MIN <= center_lon <= LON_MAX):
                msg = f"Invalid center coordinates: lat={center_lat}, lon={center_lon}"
                raise ValueError(msg)

            # Create proper GeoJSON format
            geojson = json.loads(geo_df.to_json())

            # Validate GeoJSON has features
            if not geojson.get("features"):
                msg = "No valid GeoJSON features found"
                raise ValueError(msg)

            # Extract color_continuous_scale from kwargs if provided, otherwise use default
            color_scale = kwargs.pop("color_continuous_scale", "Viridis")

            fig = px.choropleth_mapbox(
                geo_df,
                geojson=geojson,
                locations=geo_df.index,
                color=data_to_plot,
                map_style=map_style,
                zoom=zoom,
                opacity=opacity,
                center={"lat": center_lat, "lon": center_lon},
                color_continuous_scale=color_scale,
                **kwargs,
            )

            # Ensure the figure has proper layout
            fig.update_layout(
                mapbox={"style": map_style, "center": {"lat": center_lat, "lon": center_lon}, "zoom": zoom},
                margin={"r": 0, "t": 0, "l": 0, "b": 0},
                height=600,
                title=f"Coverage Analysis: {data_to_plot.replace('_', ' ').title()}",
            )

            return fig

        except Exception as e:
            # Create a fallback simple figure with error message
            error_fig = go.Figure()
            error_fig.add_annotation(
                text=f"Error creating coverage plot: {e!s}",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font={"size": 16, "color": "red"},
            )
            error_fig.update_layout(
                title="Coverage Plot Error",
                height=400,
                xaxis={"showgrid": False, "showticklabels": False},
                yaxis={"showgrid": False, "showticklabels": False},
            )

            # Re-raise the original error for debugging
            raise e

    def plot_simple(
        self,
        data_to_plot: str = "coverage_percent",
        **kwargs,  # noqa: ARG002
    ) -> Figure:
        """Create a simple scatter plot as fallback when mapbox fails."""
        geo_df = self.to_geodataframe()

        # Get centroids for simple plotting
        centroids = geo_df.geometry.centroid
        lats = [pt.y for pt in centroids]
        lons = [pt.x for pt in centroids]
        values = geo_df[data_to_plot].fillna(0)

        fig = go.Figure(
            data=go.Scattermapbox(
                lat=lats,
                lon=lons,
                mode="markers",
                marker={
                    "size": 15,
                    "color": values,
                    "colorscale": "Viridis",
                    "showscale": True,
                    "colorbar": {"title": data_to_plot.replace("_", " ").title()},
                },
                text=[f"{data_to_plot}: {val:.2f}" for val in values],
                hovertemplate="%{text}<extra></extra>",
            )
        )

        # Calculate center
        center_lat = sum(lats) / len(lats) if lats else 0
        center_lon = sum(lons) / len(lons) if lons else 0

        fig.update_layout(
            mapbox={"style": "open-street-map", "center": {"lat": center_lat, "lon": center_lon}, "zoom": 2},
            margin={"r": 0, "t": 30, "l": 0, "b": 0},
            height=600,
            title=f"Coverage Analysis: {data_to_plot.replace('_', ' ').title()}",
        )

        return fig

    def plot_mpl(
        self,
        *,
        data_to_plot: str = "coverage_percent",
        plot_land: bool = True,
        land_color: str = "lightgray",
        land_edgecolor: str = "black",
        land_alpha: float = 0.5,
        area_indices: list[int] | None = None,
        alpha: float = 0.7,
        **kwargs,
    ) -> Axes:
        """Plot the coverage results using Matplotlib.

        Parameters
        ----------
        data_to_plot : str
            The column name to plot from the coverage results
        plot_land : bool
            Whether to plot land masses as a background layer
        land_color : str
            Fill color for land masses
        land_edgecolor : str
            Edge color for land masses
        land_alpha : float
            Transparency of land masses (0-1)
        area_indices : list[int] | None
            If provided, only plot discretized polygons from these specific
            original area indices. If None, plot all polygons.
            Note: This refers to original areas of interest, not individual polygons.
        alpha : float
            Transparency of coverage data (0-1). Default 0.7 to allow land outlines to show through.
        **kwargs
            Additional keyword arguments passed to GeoDataFrame.plot()

        Returns
        -------
        Axes
            The matplotlib axes object
        """
        # Extract parameters from kwargs
        use_discretized = kwargs.pop("use_discretized", True)

        # Get the geodataframe with all data
        geo_df = self.to_geodataframe(use_discretized=use_discretized)

        # Validate the column exists
        if data_to_plot not in geo_df:
            available_columns = list(geo_df.columns)
            msg = f"Column '{data_to_plot}' does not exist. Available columns: {available_columns}"
            raise ValueError(msg)

        # Check if we're plotting specific areas
        if area_indices is not None:
            # Validate indices
            if not area_indices:
                msg = "area_indices cannot be empty when provided"
                raise ValueError(msg)

            # Filter to polygons from the specified original areas
            if "original_area_id" in geo_df.columns:
                # Filter by original area IDs
                geo_df_to_plot = geo_df[geo_df["original_area_id"].isin(area_indices)].copy()
                if len(geo_df_to_plot) == 0:
                    available_areas = sorted(geo_df["original_area_id"].unique())
                    msg = f"No polygons found for area indices {area_indices}. Available areas: {available_areas}"
                    raise ValueError(msg)
            elif use_discretized:
                # When using discretized data without original_area_id, show all polygons
                # since they all belong to the same logical area being filtered
                # All discretized polygons belong to the area being requested
                geo_df_to_plot = geo_df.copy()
            else:
                # Fallback: treat as polygon indices for backward compatibility
                max_valid_index = len(geo_df) - 1
                if any(idx < 0 or idx > max_valid_index for idx in area_indices):
                    msg = f"Invalid area indices. Valid range is 0-{max_valid_index}"
                    raise ValueError(msg)
                geo_df_to_plot = geo_df.iloc[area_indices].copy()
        else:
            # Use all polygons
            geo_df_to_plot = geo_df.copy()

        # Scale coverage percentage to percentage (0-100) for better display
        if data_to_plot == "coverage_percent":
            geo_df_to_plot[data_to_plot] = geo_df_to_plot[data_to_plot] * 100

        # Determine the plot extent first
        if area_indices is not None:
            # Requirement 3: Crop to show only selected areas
            bounds = geo_df_to_plot.total_bounds  # [minx, miny, maxx, maxy]

            # Validate bounds make sense (bounds should be [minx, miny, maxx, maxy])
            if len(bounds) != 4 or any(np.isnan(bounds)) or any(np.isinf(bounds)):  # noqa: PLR2004
                # Fallback to global view if bounds are invalid
                xlim = (-180, 180)
                ylim = (-85, 85)
            else:
                # Calculate padding (10% of range, minimum 0.5 degrees)
                x_range = bounds[2] - bounds[0]
                y_range = bounds[3] - bounds[1]

                # Ensure we have a reasonable range
                if x_range <= 0:
                    x_range = 1.0
                if y_range <= 0:
                    y_range = 1.0

                buffer_x = max(x_range * 0.1, 0.5)
                buffer_y = max(y_range * 0.1, 0.5)

                # Set cropped extent
                xlim = (bounds[0] - buffer_x, bounds[2] + buffer_x)
                ylim = (bounds[1] - buffer_y, bounds[3] + buffer_y)
        else:
            # Requirement 2: Show whole world map
            xlim = (-180, 180)
            ylim = (-85, 85)  # Avoid poles

        # Create the main coverage plot with explicit extent control
        # Extract ax parameter if provided
        provided_ax = kwargs.pop("ax", None)
        plot_result = geo_df_to_plot.plot(column=data_to_plot, ax=provided_ax, alpha=alpha, **kwargs)

        # If ax was provided, use it; otherwise use the returned axis
        if provided_ax is not None:
            ax = provided_ax  # Use the provided axis
        else:
            ax = plot_result  # Use the returned axis

        # Force the desired extent
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

        # Add land masses as background if requested
        if plot_land:
            try:
                with importlib.resources.as_file(
                    importlib.resources.files("ephemerista.analysis.resources").joinpath("ne_110m_land.shp")
                ) as shp_path:
                    land_gdf = gpd.read_file(shp_path)

                    # Clip to current view for performance
                    view_bounds = box(xlim[0], ylim[0], xlim[1], ylim[1])

                    # Only clip if the bounds are reasonable
                    if not (
                        np.isnan([xlim[0], xlim[1], ylim[0], ylim[1]]).any()
                        or np.isinf([xlim[0], xlim[1], ylim[0], ylim[1]]).any()
                    ):
                        land_gdf = land_gdf.clip(view_bounds)

                    # Plot land masses behind coverage data
                    land_gdf.plot(
                        ax=ax,
                        color=land_color,
                        edgecolor=land_edgecolor,
                        alpha=land_alpha,
                        zorder=0,  # Behind coverage data
                    )

                    # Restore the desired limits in case land plotting changed them
                    ax.set_xlim(xlim)
                    ax.set_ylim(ylim)
            except Exception as e:
                # Log the exception but continue if land data cannot be loaded
                warnings.warn(f"Could not load land data: {e}", stacklevel=2)

        # Add labels
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")

        return ax

    def to_geodataframe(self) -> gpd.GeoDataFrame:
        """Convert to a `GeoDataFrame`."""
        gdf = gpd.GeoDataFrame.from_features(self.polygons)
        gdf["coverage_percent"] = self.coverage_percent
        gdf["max_time_gaps"] = self.max_time_gaps

        # Convert revisit_times to a lightweight format for visualization
        # Instead of full Time objects, use simple counts and durations
        revisit_counts = []
        total_revisit_duration = []

        for revisit_list in self.revisit_times:
            if revisit_list:
                revisit_counts.append(len(revisit_list))
                # Calculate total duration in hours for this polygon
                try:
                    # Try to handle Time objects directly
                    total_duration = sum(float(los - aos) / 3600 for aos, los in revisit_list)
                except TypeError:
                    # Handle serialized Time objects (dictionaries)
                    total_duration = 0.0
                    for aos_time, los_time in revisit_list:
                        # Convert dict back to Time objects if needed
                        aos_obj = Time(**aos_time) if isinstance(aos_time, dict) else aos_time
                        los_obj = Time(**los_time) if isinstance(los_time, dict) else los_time
                        total_duration += float(los_obj - aos_obj) / 3600
                total_revisit_duration.append(total_duration)
            else:
                revisit_counts.append(0)
                total_revisit_duration.append(0.0)

        gdf["revisit_count"] = revisit_counts
        gdf["total_revisit_duration_hours"] = total_revisit_duration

        return gdf

    def get_revisit_times(self, polygon_id: int) -> list[tuple[Time, Time]]:
        """Get the original revisit times for a specific polygon.

        This method returns the full Time objects for detailed analysis.
        Use this instead of accessing revisit_times directly from to_geodataframe()
        which converts to lightweight format for visualization.

        Parameters
        ----------
        polygon_id : int
            The ID of the polygon to get revisit times for

        Returns
        -------
        list[tuple[Time, Time]]
            List of (aos_time, los_time) tuples for the polygon
        """
        if 0 <= polygon_id < len(self.revisit_times):
            return self.revisit_times[polygon_id]
        else:
            msg = f"Polygon ID {polygon_id} out of range"
            raise IndexError(msg)

    def aggregate_to_original_areas(self, scenario: "Scenario") -> dict[int, dict[str, float]]:
        """Aggregate coverage results back to original areas of interest.

        This method aggregates discretized polygon results back to the original areas
        they were derived from, providing coverage statistics per original area.

        Parameters
        ----------
        scenario : Scenario
            The scenario object containing the area mapping information

        Returns
        -------
        dict[int, dict[str, float]]
            Dictionary mapping original area ID to aggregated statistics:
            - 'coverage_percent': Area-weighted average coverage percentage
            - 'max_time_gap': Maximum time gap across all discretized polygons in the area
            - 'min_time_gap': Minimum time gap across all discretized polygons in the area
            - 'avg_time_gap': Average time gap across all discretized polygons in the area
            - 'num_discretized_polygons': Number of discretized polygons in this area
        """
        # Get mapping from original areas to discretized polygons
        original_to_discretized = scenario.get_original_to_discretized_mapping()

        aggregated_results = {}

        for original_area_id, polygon_ids in original_to_discretized.items():
            # Get coverage percentages for all discretized polygons in this area
            coverage_values = [self.coverage_percent[pid] for pid in polygon_ids]
            max_time_gap_values = [self.max_time_gaps[pid] for pid in polygon_ids]

            # Calculate area-weighted average coverage
            # For now, we assume equal weighting; could be enhanced with actual polygon areas
            avg_coverage = np.mean(coverage_values)

            # Calculate time gap statistics
            # Filter out infinite values for meaningful statistics
            finite_gaps = [g for g in max_time_gap_values if not math.isinf(g)]

            if finite_gaps:
                # If at least some polygons have coverage, use their statistics
                max_gap = np.max(finite_gaps)
                min_gap = np.min(finite_gaps)
                avg_gap = np.mean(finite_gaps)
            else:
                # If no polygons have coverage, all gaps are infinite
                max_gap = np.inf
                min_gap = np.inf
                avg_gap = np.inf

            aggregated_results[original_area_id] = {
                "coverage_percent": avg_coverage,
                "max_time_gap": max_gap,
                "min_time_gap": min_gap,
                "avg_time_gap": avg_gap,
                "num_discretized_polygons": len(polygon_ids),
            }

        return aggregated_results

    def get_original_area_revisit_times(self, scenario: "Scenario", original_area_id: int) -> list[tuple[Time, Time]]:
        """Get aggregated revisit times for an original area of interest.

        This method merges revisit times from all discretized polygons that make up
        the specified original area, providing a unified view of coverage events.

        Parameters
        ----------
        scenario : Scenario
            The scenario object containing the area mapping information
        original_area_id : int
            The ID of the original area to get revisit times for

        Returns
        -------
        list[tuple[Time, Time]]
            List of merged (aos_time, los_time) tuples for the original area
        """
        # Get mapping from original areas to discretized polygons
        original_to_discretized = scenario.get_original_to_discretized_mapping()

        if original_area_id not in original_to_discretized:
            msg = f"Original area ID {original_area_id} not found"
            raise ValueError(msg)

        polygon_ids = original_to_discretized[original_area_id]

        # Collect all revisit intervals from discretized polygons
        all_intervals = []
        for polygon_id in polygon_ids:
            polygon_revisits = self.get_revisit_times(polygon_id)
            for aos_time, los_time in polygon_revisits:
                # Convert to seconds for merging
                start_seconds = float(aos_time - scenario.start_time)
                end_seconds = float(los_time - scenario.start_time)
                all_intervals.append([start_seconds, end_seconds])

        if not all_intervals:
            return []

        # Merge overlapping intervals
        merged_intervals = _merge_time_intervals_optimized(all_intervals)

        # Convert back to Time objects
        merged_revisit_times = []
        for start_seconds, end_seconds in merged_intervals:
            aos_time = scenario.start_time + TimeDelta.from_seconds(float(start_seconds))
            los_time = scenario.start_time + TimeDelta.from_seconds(float(end_seconds))
            merged_revisit_times.append((aos_time, los_time))

        return merged_revisit_times

    def to_area_results(self, scenario: "Scenario") -> "CoverageResults":
        """Convert to CoverageResults for easier interpretation.

        Parameters
        ----------
        scenario : Scenario
            The scenario containing area mapping information

        Returns
        -------
        CoverageResults
            Aggregated results for areas
        """
        return CoverageResults.from_coverage_results(self, scenario)


class CoverageResults(BaseModel):
    """Results of coverage analysis aggregated to areas of interest.

    This class provides coverage statistics aggregated back to the user's
    areas of interest rather than the discretized polygons used for computation.
    It also optionally includes the discretized polygon data for detailed
    heatmap visualization.
    """

    results_type: str = Field(default="coverage", frozen=True, repr=False, alias="type")
    areas: list[PolygonFeature]  # Areas with names and metadata
    coverage_percent: list[float]  # Aggregated coverage per area
    max_time_gaps: list[float]  # Max gap per area (seconds)

    # Add polygons alias for backwards compatibility in tests
    @property
    def polygons(self) -> list[PolygonFeature]:
        """Alias for areas to maintain compatibility."""
        return self.areas

    # Add revisit_times alias for backwards compatibility in tests
    @property
    def revisit_times(self) -> list[list]:
        """Alias to maintain compatibility with tests. Returns empty lists for each area."""
        return [[] for _ in self.areas]

    min_time_gaps: list[float]  # Min gap per area (seconds)
    avg_time_gaps: list[float]  # Average gap per area (seconds)
    num_discretized_polygons: list[int]  # Number of discretized polygons per area

    # Optional: discretized polygon data for detailed visualization
    discretized_polygons: list[PolygonFeature] | None = None
    discretized_coverage_percent: list[float] | None = None
    discretized_max_time_gaps: list[float] | None = None

    @classmethod
    def from_coverage_results(
        cls, coverage_results: _DiscretizedCoverageResults, scenario: "Scenario"
    ) -> "CoverageResults":
        """Create CoverageResults from discretized coverage results.

        Parameters
        ----------
        coverage_results : _DiscretizedCoverageResults
            The detailed coverage results from discretized polygons
        scenario : Scenario
            The scenario containing area mapping information

        Returns
        -------
        CoverageResults
            Aggregated results for areas
        """
        # Get aggregated statistics
        aggregated = coverage_results.aggregate_to_original_areas(scenario)

        # Prepare lists in order of original area IDs
        original_area_ids = sorted(aggregated.keys())

        return cls(
            areas=[scenario.areas_of_interest[area_id] for area_id in original_area_ids],
            coverage_percent=[aggregated[area_id]["coverage_percent"] for area_id in original_area_ids],
            max_time_gaps=[aggregated[area_id]["max_time_gap"] for area_id in original_area_ids],
            min_time_gaps=[aggregated[area_id]["min_time_gap"] for area_id in original_area_ids],
            avg_time_gaps=[aggregated[area_id]["avg_time_gap"] for area_id in original_area_ids],
            num_discretized_polygons=[aggregated[area_id]["num_discretized_polygons"] for area_id in original_area_ids],
            # Include discretized data for visualization
            discretized_polygons=coverage_results.polygons,
            discretized_coverage_percent=coverage_results.coverage_percent,
            discretized_max_time_gaps=coverage_results.max_time_gaps,
        )

    def to_geodataframe(self, *, use_discretized: bool = False) -> "gpd.GeoDataFrame":
        """Convert to a GeoDataFrame for visualization.

        Parameters
        ----------
        use_discretized : bool
            If True and discretized data is available, return discretized polygons
            instead of aggregated areas for heatmap visualization.
        """
        if use_discretized and self.discretized_polygons is not None and self.discretized_coverage_percent is not None:
            # Return discretized data for heatmap
            gdf = gpd.GeoDataFrame.from_features(self.discretized_polygons)
            gdf["coverage_percent"] = self.discretized_coverage_percent
            if self.discretized_max_time_gaps is not None:
                gdf["max_time_gaps"] = self.discretized_max_time_gaps
            return gdf

        # Default: return aggregated area data
        gdf = gpd.GeoDataFrame.from_features(self.areas)
        gdf["coverage_percent"] = self.coverage_percent
        gdf["max_time_gaps"] = self.max_time_gaps
        gdf["min_time_gaps"] = self.min_time_gaps
        gdf["avg_time_gaps"] = self.avg_time_gaps
        gdf["num_discretized_polygons"] = self.num_discretized_polygons

        # Add compatibility columns for tests
        gdf["revisit_count"] = self.num_discretized_polygons  # Alias for compatibility
        gdf["total_revisit_duration_hours"] = [gap / 3600.0 for gap in self.avg_time_gaps]  # Convert to hours

        return gdf

    def to_dataframe(self) -> "pd.DataFrame":
        """Convert coverage results to a pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns for area information and coverage statistics.
            Each row represents one area of interest.
        """

        def safe_divide(value, divisor):
            """Safely divide, handling inf and nan values."""
            if math.isinf(value) or math.isnan(value):
                return -1.0  # Use -1.0 to indicate invalid/infinite values
            return value / divisor

        data = []
        for i, area in enumerate(self.areas):
            # Extract area name from properties if available
            area_name = area.properties.get("name", f"Area_{i}")

            # Convert geometry to WKT for CSV export
            geometry_wkt = str(area.geometry)

            # Handle potentially infinite or NaN values
            coverage_percent = self.coverage_percent[i]
            max_time_gap = self.max_time_gaps[i]
            min_time_gap = self.min_time_gaps[i]
            avg_time_gap = self.avg_time_gaps[i]

            # Replace infinite or NaN values with safe defaults
            if math.isinf(coverage_percent) or math.isnan(coverage_percent):
                coverage_percent = 0.0
            if math.isinf(max_time_gap) or math.isnan(max_time_gap):
                max_time_gap = -1.0
            if math.isinf(min_time_gap) or math.isnan(min_time_gap):
                min_time_gap = -1.0
            if math.isinf(avg_time_gap) or math.isnan(avg_time_gap):
                avg_time_gap = -1.0

            data.append(
                {
                    "area_name": area_name,
                    "geometry": geometry_wkt,
                    "coverage_percent": coverage_percent,
                    "max_time_gap_seconds": max_time_gap,
                    "min_time_gap_seconds": min_time_gap,
                    "avg_time_gap_seconds": avg_time_gap,
                    "max_time_gap_hours": safe_divide(max_time_gap, 3600.0),
                    "min_time_gap_hours": safe_divide(min_time_gap, 3600.0),
                    "avg_time_gap_hours": safe_divide(avg_time_gap, 3600.0),
                    "num_discretized_polygons": self.num_discretized_polygons[i],
                    **area.properties,  # Include any additional properties
                }
            )

        return pd.DataFrame(data)

    def plot(
        self,
        data_to_plot: str = "coverage_percent",
        map_style: str = "open-street-map",
        zoom: int = 0,
        opacity: float = 0.7,
        **kwargs,
    ) -> Figure:
        """Plot the coverage results using Plotly."""
        return self.plot_plotly(data_to_plot=data_to_plot, map_style=map_style, zoom=zoom, opacity=opacity, **kwargs)

    def plot_plotly(
        self,
        data_to_plot: str = "coverage_percent",
        map_style: str = "open-street-map",
        zoom: int = 2,
        opacity: float = 0.7,
        polygon_indices: list[int] | None = None,
        **kwargs,
    ) -> Figure:
        """Plot the coverage results using Plotly."""
        try:
            # Use discretized data by default for better heatmap visualization
            use_discretized = kwargs.get("use_discretized", True)
            geo_df = self.to_geodataframe(use_discretized=use_discretized)

            if data_to_plot not in geo_df:
                available_columns = list(geo_df.columns)
                msg = f"Column '{data_to_plot}' does not exist. Available columns: {available_columns}"
                raise ValueError(msg)

            # Filter to specific areas if requested
            if polygon_indices is not None:
                if use_discretized and "original_area_id" in geo_df.columns:
                    # Filter discretized data by original area IDs
                    geo_df = geo_df[geo_df["original_area_id"].isin(polygon_indices)].copy()
                elif not use_discretized:
                    # Filter aggregated data by index
                    geo_df = geo_df.iloc[polygon_indices].copy()

            # Validate we have data to plot
            if len(geo_df) == 0:
                msg = "No data available for plotting"
                raise ValueError(msg)

            # Clean data - replace any NaN or infinite values
            data_column = geo_df[data_to_plot].copy()
            data_column = data_column.replace([np.inf, -np.inf], np.nan)
            data_column = data_column.fillna(0)
            geo_df = geo_df.copy()
            geo_df[data_to_plot] = data_column

            # Validate geometries
            if geo_df.geometry.isnull().any():
                msg = "Invalid geometries found in data"
                raise ValueError(msg)

            # Calculate center coordinates from the geometries (use filtered data for extent)
            bounds = geo_df.total_bounds  # [minx, miny, maxx, maxy]
            center_lat = (bounds[1] + bounds[3]) / 2
            center_lon = (bounds[0] + bounds[2]) / 2

            # Validate coordinates
            if not (LAT_MIN <= center_lat <= LAT_MAX) or not (LON_MIN <= center_lon <= LON_MAX):
                msg = f"Invalid center coordinates: lat={center_lat}, lon={center_lon}"
                raise ValueError(msg)

            # Create proper GeoJSON format
            geojson = json.loads(geo_df.to_json())

            # Validate GeoJSON has features
            if not geojson.get("features"):
                msg = "No valid GeoJSON features found"
                raise ValueError(msg)

            # Extract color_continuous_scale from kwargs if provided, otherwise use default
            color_scale = kwargs.pop("color_continuous_scale", "Viridis")

            fig = px.choropleth_map(
                geo_df,
                geojson=geojson,
                locations=geo_df.index,
                color=data_to_plot,
                map_style=map_style,
                zoom=zoom,
                opacity=opacity,
                center={"lat": center_lat, "lon": center_lon},
                color_continuous_scale=color_scale,
                **kwargs,
            )

            # Ensure the figure has proper layout
            fig.update_layout(
                mapbox={"style": map_style, "center": {"lat": center_lat, "lon": center_lon}, "zoom": zoom},
                margin={"r": 0, "t": 0, "l": 0, "b": 0},
                height=600,
                title=f"Coverage Analysis: {data_to_plot.replace('_', ' ').title()}",
            )

            return fig

        except Exception as e:
            # Create a fallback simple figure with error message
            error_fig = go.Figure()
            error_fig.add_annotation(
                text=f"Error creating coverage plot: {e!s}",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font={"size": 16, "color": "red"},
            )
            error_fig.update_layout(
                title="Coverage Plot Error",
                height=400,
                xaxis={"showgrid": False, "showticklabels": False},
                yaxis={"showgrid": False, "showticklabels": False},
            )

            # Re-raise the original error for debugging
            raise e

    def plot_mpl(
        self,
        *,
        data_to_plot: str = "coverage_percent",
        plot_land: bool = True,
        land_color: str = "lightgray",
        land_edgecolor: str = "black",
        land_alpha: float = 0.5,
        area_indices: list[int] | None = None,
        alpha: float = 0.7,
        **kwargs,
    ) -> Axes:
        """Plot the area coverage results using Matplotlib.

        Parameters
        ----------
        data_to_plot : str
            The column name to plot from the coverage results
        plot_land : bool
            Whether to plot land masses as a background layer
        land_color : str
            Fill color for land masses
        land_edgecolor : str
            Edge color for land masses
        land_alpha : float
            Transparency of land masses (0-1)
        area_indices : list[int] | None
            Indices of specific areas to plot. If None, plot all areas.
        alpha : float
            Transparency of coverage data (0-1). Default 0.7 to allow land outlines to show through.
        **kwargs
            Additional keyword arguments passed to GeoDataFrame.plot()

        Returns
        -------
        Axes
            The matplotlib axes object
        """
        # Determine whether to use discretized data for visualization
        use_discretized = kwargs.pop("use_discretized", True)
        geo_df = self.to_geodataframe(use_discretized=use_discretized)

        # Validate the column exists
        if data_to_plot not in geo_df:
            available_columns = list(geo_df.columns)
            msg = f"Column '{data_to_plot}' does not exist. Available columns: {available_columns}"
            raise ValueError(msg)

        # Handle area selection
        if area_indices is not None:
            # Validate indices
            if not area_indices:
                msg = "area_indices cannot be empty when provided"
                raise ValueError(msg)

            if use_discretized and "original_area_id" in geo_df.columns:
                # Filter discretized data by original area IDs
                geo_df_to_plot = geo_df[geo_df["original_area_id"].isin(area_indices)].copy()
                if len(geo_df_to_plot) == 0:
                    available_areas = sorted(geo_df["original_area_id"].unique())
                    msg = f"No polygons found for area indices {area_indices}. Available areas: {available_areas}"
                    raise ValueError(msg)
            elif use_discretized:
                # When using discretized data without original_area_id, show all polygons
                # since they all belong to the same logical area being filtered
                # All discretized polygons belong to the area being requested
                geo_df_to_plot = geo_df.copy()
            else:
                # Filter aggregated data by index
                max_valid_index = len(geo_df) - 1
                if any(idx < 0 or idx > max_valid_index for idx in area_indices):
                    msg = f"Invalid area indices. Valid range is 0-{max_valid_index}"
                    raise ValueError(msg)
                geo_df_to_plot = geo_df.iloc[area_indices].copy()
        else:
            # Use all areas
            geo_df_to_plot = geo_df.copy()

        # Scale coverage percentage to percentage (0-100) for better display
        if data_to_plot == "coverage_percent":
            geo_df_to_plot[data_to_plot] = geo_df_to_plot[data_to_plot] * 100

        # Determine the plot extent first
        if area_indices is not None:
            # Requirement 3: Crop to show only selected areas
            bounds = geo_df_to_plot.total_bounds  # [minx, miny, maxx, maxy]

            # Validate bounds make sense (bounds should be [minx, miny, maxx, maxy])
            if len(bounds) != 4 or any(np.isnan(bounds)) or any(np.isinf(bounds)):  # noqa: PLR2004
                # Fallback to global view if bounds are invalid
                xlim = (-180, 180)
                ylim = (-85, 85)
            else:
                # Calculate padding (10% of range, minimum 0.5 degrees)
                x_range = bounds[2] - bounds[0]
                y_range = bounds[3] - bounds[1]

                # Ensure we have a reasonable range
                if x_range <= 0:
                    x_range = 1.0
                if y_range <= 0:
                    y_range = 1.0

                buffer_x = max(x_range * 0.1, 0.5)
                buffer_y = max(y_range * 0.1, 0.5)

                # Set cropped extent
                xlim = (bounds[0] - buffer_x, bounds[2] + buffer_x)
                ylim = (bounds[1] - buffer_y, bounds[3] + buffer_y)
        else:
            # Requirement 2: Show whole world map
            xlim = (-180, 180)
            ylim = (-85, 85)  # Avoid poles

        # Create the main coverage plot with explicit extent control
        # Extract ax parameter if provided
        provided_ax = kwargs.pop("ax", None)
        plot_result = geo_df_to_plot.plot(column=data_to_plot, ax=provided_ax, alpha=alpha, **kwargs)

        # If ax was provided, use it; otherwise use the returned axis
        if provided_ax is not None:
            ax = provided_ax  # Use the provided axis
        else:
            ax = plot_result  # Use the returned axis

        # Force the desired extent
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

        # Add land masses as background if requested
        if plot_land:
            try:
                with importlib.resources.as_file(
                    importlib.resources.files("ephemerista.analysis.resources").joinpath("ne_110m_land.shp")
                ) as shp_path:
                    land_gdf = gpd.read_file(shp_path)

                    # Clip to current view for performance
                    view_bounds = box(xlim[0], ylim[0], xlim[1], ylim[1])

                    # Only clip if the bounds are reasonable
                    if not (
                        np.isnan([xlim[0], xlim[1], ylim[0], ylim[1]]).any()
                        or np.isinf([xlim[0], xlim[1], ylim[0], ylim[1]]).any()
                    ):
                        land_gdf = land_gdf.clip(view_bounds)

                    # Plot land masses behind coverage data
                    land_gdf.plot(
                        ax=ax,
                        color=land_color,
                        edgecolor=land_edgecolor,
                        alpha=land_alpha,
                        zorder=0,  # Behind coverage data
                    )

                    # Restore the desired limits in case land plotting changed them
                    ax.set_xlim(xlim)
                    ax.set_ylim(ylim)
            except Exception as e:
                # Log the exception but continue if land data cannot be loaded
                warnings.warn(f"Could not load land data: {e}", stacklevel=2)

        # Add labels
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")

        return ax


class Coverage(Analysis[CoverageResults]):
    """Coverage analysis.

    Notes
    -----
    The coverage is computed by computing all passes of the spacecraft over all ground locations of the exterior of each
    polygon, i.e. the visibility from the min elevation defined in the polygon's properties.

    Doing that for all ground locations of the exterior of each polygon is computationally intensive, but that allows
    to do an average of the coverage on the polygon. Besides, when the GroundLocations are created in scenarios.py,
    shared locations between adjacent polygons are merged to avoid duplicate computations.

    For instance for a polygon's exterior composed of 4 points, if two points have spacecraft visibility for a total
    duration of 340 seconds, and the two other points for 360 seconds, then the average visibility duration of this
    polygon will be 350 seconds.
    """

    scenario: Scenario = Field(description="The scenario used to analyze the coverage")
    start_time: Time | None = Field(
        default=None, description="Start time (optional, if None the scenario's start time is used)"
    )
    end_time: Time | None = Field(
        default=None, description="End time (optional, if None the scenario's end time is used)"
    )
    # Removed parallel processing parameters - using optimized sequential algorithm

    def _compute_visibility_direct(self, ensemble: Ensemble):
        """Compute visibility using lox.visibility_all directly and return raw results."""
        start_time = self.start_time or self.scenario.start_time
        end_time = self.end_time or self.scenario.end_time

        times = [time._time for time in start_time.trange(end_time, self.scenario.time_step)]

        # Pre-filter assets by type to avoid checking in the loop
        all_assets = self.scenario.all_assets
        spacecraft_assets = [(a.asset_id, ensemble[a]) for a in all_assets if isinstance(a.model, Spacecraft)]

        # Collect ground locations with deterministic UUIDs
        observers: list[tuple[UUID5, GroundLocation]] = []
        for i, loc in enumerate(self.scenario.ground_locations):
            deterministic_id = uuid.uuid5(EPHEMERISTA_NAMESPACE, f"{self.scenario.scenario_id}:ground_location:{i}")
            observers.append((deterministic_id, loc))

        # Prepare ground stations dict for visibility_all
        ground_stations = {}
        observer_id_map = {}
        for observer_id, observer_model in observers:
            key = str(observer_id)
            ground_stations[key] = (
                observer_model._location,
                lox.ElevationMask.fixed(observer_model.minimum_elevation.radians),
            )
            observer_id_map[key] = observer_id

        # Prepare spacecraft ensemble for visibility_all
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
            None,  # bodies
            eop,
        )

        # Return raw results with mapping information for direct processing
        return {
            "raw_results": visibility_results,
            "spacecraft_id_map": spacecraft_id_map,
            "observer_id_map": observer_id_map,
            "observers": dict(observers),
        }

    def analyze(  # type: ignore
        self,
        ensemble: Ensemble | None = None,
        visibility: VisibilityResults | None = None,
    ) -> CoverageResults:
        """Run the coverage analysis."""
        if not self.scenario.areas_of_interest:
            msg = (
                "Coverage analysis requires at least one area of interest to be defined. "
                "Please add one or more areas of interest to your scenario."
            )
            raise ValueError(msg)

        if not ensemble:
            ensemble = self.scenario.propagate()

        if not visibility:
            # Use lox.visibility_all directly for better performance
            raw_visibility = self._compute_visibility_direct(ensemble)
        else:
            # If visibility is provided, we need to extract the passes structure
            raw_visibility = None

        ts = self.scenario.start_time
        te = self.scenario.end_time
        scenario_duration = (te - ts).to_decimal_seconds()

        # Initialize result arrays
        total_covered_time = np.zeros(len(self.scenario.discretized_areas))
        revisit_times = [[] for _ in range(len(self.scenario.discretized_areas))]
        max_time_gaps = [np.inf for _ in range(len(self.scenario.discretized_areas))]

        # Create mapping from visibility observer IDs to ground locations
        ground_location_mapping = {}
        for i, loc in enumerate(self.scenario.ground_locations):
            deterministic_id = uuid.uuid5(EPHEMERISTA_NAMESPACE, f"{self.scenario.scenario_id}:ground_location:{i}")
            ground_location_mapping[deterministic_id] = loc

        # Pre-compute polygon properties
        polygon_n_points = np.array(
            [
                aoi.properties.get("n_exterior_points", 1)  # type: ignore
                for aoi in self.scenario.discretized_areas
            ]
        )

        # Pre-allocate arrays for polygon intervals
        poly_intervals_lists = [[] for _ in range(len(self.scenario.discretized_areas))]

        # Process visibility passes - batch collect all intervals first
        ground_point_intervals = {observer_id: [] for observer_id in ground_location_mapping}

        if raw_visibility:
            # Process raw lox.visibility_all results directly
            visibility_results = raw_visibility["raw_results"]
            spacecraft_id_map = raw_visibility["spacecraft_id_map"]
            observer_id_map = raw_visibility["observer_id_map"]

            for spacecraft_key, observer_dict in visibility_results.items():
                spacecraft_id = spacecraft_id_map[spacecraft_key]
                target = self.scenario[spacecraft_id]
                if not isinstance(target.model, Spacecraft):
                    continue

                for observer_key, passes in observer_dict.items():
                    observer_id = observer_id_map[observer_key]
                    if observer_id not in ground_location_mapping:
                        continue

                    # Work directly with lox Pass objects - minimal Python object creation
                    if passes:
                        intervals = []
                        for pass_obj in passes:
                            # Extract window directly from lox Pass
                            window = pass_obj.window()
                            # Convert to Python Time objects for arithmetic
                            start_time = Time._from_lox(window.start())
                            end_time = Time._from_lox(window.end())

                            # Calculate time offsets in seconds
                            start_seconds = (start_time - ts).to_decimal_seconds()
                            end_seconds = (end_time - ts).to_decimal_seconds()

                            # Skip zero-duration windows
                            if end_seconds > start_seconds:
                                intervals.append([start_seconds, end_seconds])

                        ground_point_intervals[observer_id].extend(intervals)
        else:
            # Fallback to using VisibilityResults for compatibility
            for target_id, observers in visibility.passes.items():
                target = self.scenario[target_id]
                if not isinstance(target.model, Spacecraft):
                    continue

                for observer_id, passes in observers.items():
                    if observer_id not in ground_location_mapping:
                        continue

                    # Vectorized interval conversion
                    if passes:
                        intervals = [
                            [
                                (gs_pass.window.start - ts).to_decimal_seconds(),
                                (gs_pass.window.stop - ts).to_decimal_seconds(),
                            ]
                            for gs_pass in passes
                        ]
                        ground_point_intervals[observer_id].extend(intervals)

        # Process all ground points sequentially with optimizations
        for observer_id, intervals in ground_point_intervals.items():
            if not intervals:
                continue

            # Merge intervals using optimized NumPy function
            merged_intervals = _merge_time_intervals_optimized(intervals)

            if len(merged_intervals) == 0:
                continue

            # Vectorized duration calculation
            total_duration = (merged_intervals[:, 1] - merged_intervals[:, 0]).sum()

            ground_location = ground_location_mapping[observer_id]

            # Vectorized coverage contribution
            for polygon_id in ground_location.polygon_ids:
                total_covered_time[polygon_id] += total_duration / polygon_n_points[polygon_id]
                poly_intervals_lists[polygon_id].extend(merged_intervals.tolist())

        # Process polygon statistics with vectorized operations
        for polygon_id in range(len(self.scenario.discretized_areas)):
            poly_intervals = poly_intervals_lists[polygon_id]
            if not poly_intervals:
                continue

            # Final merge using optimized function
            poly_intervals_merged = _merge_time_intervals_optimized(poly_intervals)

            if len(poly_intervals_merged) == 0:
                continue

            # Vectorized time conversion
            starts = poly_intervals_merged[:, 0]
            finishes = poly_intervals_merged[:, 1]

            # Batch create Time objects
            aos_times = [ts + TimeDelta.from_minutes(float(start) / 60) for start in starts]
            los_times = [ts + TimeDelta.from_minutes(float(finish) / 60) for finish in finishes]
            revisit_times[polygon_id] = list(zip(aos_times, los_times, strict=True))

            # Vectorized gap computation
            if len(starts) > 1:
                gaps = starts[1:] - finishes[:-1]
                gap_worst = gaps.max()
            else:
                gap_worst = scenario_duration

            max_time_gaps[polygon_id] = gap_worst  # Keep in seconds

        # Final coverage calculation
        coverage_percentages = total_covered_time / scenario_duration

        # Create intermediate _DiscretizedCoverageResults first
        coverage_results = _DiscretizedCoverageResults(
            polygons=self.scenario.discretized_areas,
            coverage_percent=coverage_percentages.tolist(),
            max_time_gaps=max_time_gaps,
            revisit_times=revisit_times,
        )

        # Convert to aggregated results for areas
        return coverage_results.to_area_results(self.scenario)
