"""The scenarios.py module.

This module provides the `Scenario` class which collects all required inputs such as assets, communications channels,
points and areas of interest for orbit propagation and analyses.
"""

import json as json_module
import os
from functools import cached_property
from math import asin, degrees, radians, sin
from pathlib import Path
from typing import Literal, Self

import antimeridian
import h3
import lox_space as lox
import numpy as np
import pyproj
from geojson_pydantic import Feature, Point, Polygon  # type: ignore
from pydantic import UUID5, Field, PrivateAttr
from shapely import MultiPolygon
from shapely import Polygon as ShapelyPolygon

from ephemerista import BaseModel
from ephemerista.angles import Angle
from ephemerista.assets import Asset, AssetKey, GroundLocation, _asset_id
from ephemerista.bodies import Origin
from ephemerista.comms.channels import Channel
from ephemerista.constellation.design import Constellation
from ephemerista.coords.trajectories import Trajectory
from ephemerista.coords.twobody import DEFAULT_FRAME, DEFAULT_ORIGIN
from ephemerista.frames import ReferenceFrame
from ephemerista.propagators.orekit.conversions import time_to_abs_date
from ephemerista.time import Time
from ephemerista.uuid_utils import generate_scenario_uuid

# Current scenario schema version
CURRENT_SCENARIO_VERSION = 1


class Rectangle:
    """
    A rectangle type that has a simple Geo JSON interface.

    Created so we don't use the costly to create Shapely. Polygon objects that are not needed. We only need
    the __geo_interface__ implementation.
    Note that we are checking nothing here, as we expect a well-formed rectangle.

    Reference https://gist.github.com/sgillies/2217756#__geo_interface
    """

    def __init__(self, coords: list[tuple[float, float]]):
        self.coords = coords

    @property
    def __geo_interface__(self):
        """The __geo_interface__ property of the rectangle."""
        return {"type": "Polygon", "coordinates": [self.coords]}


def _get_latitude_range_equal_area(min_lat: float, max_lat: float, n_bands: int) -> list[tuple]:
    """Get latitudes list for polygonize_aoi_rectangles with equal rectangle areas.

    Get a list of n_bands latitude values from min_lat to max_lat that would have equal area if
    used to generate rectangles.
    """
    sin_min = sin(radians(min_lat))
    sin_max = sin(radians(max_lat))
    sin_edges = np.linspace(sin_min, sin_max, n_bands + 1)
    lat_edges = [degrees(asin(s)) for s in sin_edges]
    heights = np.diff(lat_edges)
    lat_and_height_range = [(lat_edges[i], heights[i]) for i in range(len(heights))]
    return lat_and_height_range


def polygonize_aoi(aoi_geom_dict: dict, res: int, min_elevation_deg: float = 0.0) -> list[Feature[Polygon, dict]]:
    """
    Polygonize an area of interest using h3.

    Parameters
    ----------
    aoi_geom_dict: dict
        A GeoJSON-compatible dict containing a "coordinates" key, usually from a __geo_interface__
    res: int
        h3 res parameter
    min_elevation_deg: float
        Minimum elevation in degrees to compute the visibility between a spacecraft and the ground cells
    """
    cell_list = h3.geo_to_cells(aoi_geom_dict, res=res)

    feature_list = []
    for cell in cell_list:
        boundary = h3.cell_to_boundary(cell)
        lon_lat_tuples = []
        for bound_coords in boundary:
            lon_lat_tuples.append((bound_coords[1], bound_coords[0]))
        polygon = ShapelyPolygon(lon_lat_tuples)
        poly_or_multipoly = antimeridian.fix_polygon(polygon)
        if isinstance(
            poly_or_multipoly, MultiPolygon
        ):  # antimeridian sometimes has to split a polygon and returns a MultiPolygon instead
            for poly in poly_or_multipoly.geoms:
                feature_list.append(
                    Feature[Polygon, dict](
                        geometry=poly, properties={"min_elevation_deg": min_elevation_deg}, type="Feature"
                    )  # type: ignore
                )
        else:
            feature_list.append(
                Feature[Polygon, dict](
                    geometry=poly_or_multipoly,  # type: ignore
                    properties={"min_elevation_deg": min_elevation_deg},
                    type="Feature",
                )
            )

    return feature_list


def polygonize_aoi_rectangles(
    aoi_geom_dict: dict,
    vertex_degrees: int | float,
    min_elevation_deg: float = 0.0,
) -> list[Feature[Polygon, dict]]:
    """
    Polygonize an area of interest using rectangles of equal lat/long degrees.

    Polygons crossing the antimeridian are divided in two, so no malformed features are created.

    Parameters
    ----------
    aoi_geom_dict: dict
        A GeoJSON-compatible dict containing a "coordinates" key, usually from a __geo_interface__
        The AOI is the bounding box of this polygon, so the rectangles are arranged as a grid.
    vertex_degrees: int | float
        Size of the latitude and longitude vertexes in degrees
    min_elevation_deg: float
        Minimum elevation in degrees to compute the visibility between a spacecraft and the ground cells
    """
    aoi_geom_dict_poly = ShapelyPolygon(aoi_geom_dict["coordinates"][0])
    aoi_geom_fixed_poly_or_multipoly = antimeridian.fix_polygon(aoi_geom_dict_poly)
    aoi_geom_fixed = []
    if isinstance(
        aoi_geom_fixed_poly_or_multipoly, MultiPolygon
    ):  # antimeridian sometimes has to split a polygon and returns a MultiPolygon instead
        for geom in aoi_geom_fixed_poly_or_multipoly.geoms:
            aoi_geom_fixed.append(geom.envelope)
    else:
        aoi_geom_fixed.append(aoi_geom_fixed_poly_or_multipoly.envelope)

    # min and max latitudes are fixed to all fixtures in aoi_geom_fixed so the output is like a grid
    _, min_lat, _, max_lat = aoi_geom_fixed[0].bounds
    for aoi_geom in aoi_geom_fixed[1:]:
        min_lat = min(min_lat, aoi_geom.bounds[1])
        max_lat = max(max_lat, aoi_geom.bounds[3])
    lat_and_height_range = _get_latitude_range_equal_area(
        min_lat, max_lat, int((max_lat - min_lat) / vertex_degrees) + 1
    )

    feature_list = []
    for aoi_geom in aoi_geom_fixed:
        min_lon, _, max_lon, _ = aoi_geom.bounds

        lon_range = np.arange(min_lon, max_lon, vertex_degrees)

        for lon in lon_range:
            for lat, height in lat_and_height_range:
                lon_plus_square_degrees = min(180, lon + vertex_degrees)
                square_coords = [
                    (lon, lat),
                    (lon_plus_square_degrees, lat),
                    (lon_plus_square_degrees, lat + height),
                    (lon, lat + height),
                    (lon, lat),
                ]
                polygon = Rectangle(square_coords)
                feature_list.append(
                    Feature[Polygon, dict](
                        geometry=polygon,  # type: ignore
                        properties={"min_elevation_deg": min_elevation_deg},
                        type="Feature",
                    )
                )

    return feature_list


def _earth_rotation(time: Time):
    from org.orekit.bodies import CelestialBodyFactory  # type: ignore  # noqa: PLC0415
    from org.orekit.frames import FramesFactory  # type: ignore  # noqa: PLC0415

    icrf = FramesFactory.getICRF()
    body_fixed = CelestialBodyFactory.getEarth().getBodyOrientedFrame()
    return icrf.getTransformTo(body_fixed, time_to_abs_date(time)).getRotation()


class Ensemble(BaseModel):
    """The `Ensemble` model.

    This class collects the resulting trajectories from propagating the state of all assets within a scenario.
    """

    trajectories: dict[UUID5, Trajectory] = Field(description="Dictionary of trajectories indexed by asset IDs")
    ephemerides: dict[str, Trajectory] = Field(default={})
    _ensemble: lox.Ensemble = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._ensemble = lox.Ensemble(
            {str(asset_id): trajectory._trajectory for asset_id, trajectory in self.trajectories.items()}
        )

    def __getitem__(self, asset: AssetKey) -> Trajectory:
        """Return the trajectory for a given asset."""
        return self.trajectories[_asset_id(asset)]

    def add_earth_attitude(self):
        """Add attitude quaternions for Earth to the ensemble."""
        if not self.trajectories:
            return
        trajectory = next(iter(self.trajectories.values()))
        n = len(trajectory.simulation_time)
        states = np.zeros((n, 7))
        states[:, 0] = trajectory.simulation_time
        rotations = [_earth_rotation(t) for t in trajectory.times]
        attitude = [(rot.getQ0(), rot.getQ1(), rot.getQ2(), rot.getQ3()) for rot in rotations]

        self.ephemerides["earth"] = Trajectory(
            trajectory_type="ephemeris", start_time=trajectory.times[0], states=states, attitude=attitude
        )


class Scenario(BaseModel):
    """The `Scenario` model."""

    version: int = Field(default=CURRENT_SCENARIO_VERSION, description="Scenario JSON schema version")
    scenario_id: UUID5 = Field(alias="id", default_factory=generate_scenario_uuid, description="Scenario ID")
    name: str = Field(description="The name of the scenario", default="Scenario")
    start_time: Time = Field(description="Start time of the scenario")
    end_time: Time = Field(description="End time of the scenario")
    time_step: float = Field(default=60, description="Time step in seconds")
    origin: Origin = Field(
        default=DEFAULT_ORIGIN,
        description="Origin of the coordinate system",
    )
    frame: ReferenceFrame = Field(default=DEFAULT_FRAME, description="Reference frame of the coordinate system")
    assets: list[Asset] = Field(default=[], description="List of assets")
    constellations: list[Constellation] = Field(default=[], description="List of constellations")
    channels: list[Channel] = Field(default=[], description="List of RF channels")
    points_of_interest: list[Feature[Point, dict]] = Field(default=[], description="List of points of interest")
    areas_of_interest: list[Feature[Polygon, dict]] = Field(default=[], description="List of areas of interest")
    discretization_method: Literal["rectangles", "h3"] = Field(
        default="rectangles", description="Method for discretizing areas of interest"
    )
    discretization_resolution: int | float = Field(
        default=1, description="Resolution for discretization (degrees for rectangles, h3 resolution for h3)"
    )
    auto_discretize: bool = Field(default=True, description="Whether to automatically discretize areas of interest")
    _ground_locations: list[GroundLocation] = PrivateAttr(default=[])
    _discretized_areas: list[Feature[Polygon, dict]] = PrivateAttr(default=[])

    def __init__(self, **data):
        super().__init__(**data)
        self._discretize_areas_of_interest()
        self._gen_points_from_aoi()

    def _discretize_areas_of_interest(self):
        """Discretize areas of interest into smaller polygons based on the configured method and resolution."""
        if not self.areas_of_interest:
            return

        if not self.auto_discretize:
            # Use areas as-is when auto_discretize is False
            # Add original_area_id to each area for consistency
            self._discretized_areas = []
            for original_area_id, area in enumerate(self.areas_of_interest):
                area_copy = area.model_copy(deep=True)
                if area_copy.properties is None:
                    area_copy.properties = {}
                area_copy.properties["original_area_id"] = original_area_id  # type: ignore
                self._discretized_areas.append(area_copy)
            return

        discretized_areas = []

        for original_area_id, area in enumerate(self.areas_of_interest):
            min_elevation_deg = area.properties.get("min_elevation_deg", 0.0)  # type: ignore
            aoi_geom_dict = area.geometry.__geo_interface__

            if self.discretization_method == "rectangles":
                discretized_polys = polygonize_aoi_rectangles(
                    aoi_geom_dict, vertex_degrees=self.discretization_resolution, min_elevation_deg=min_elevation_deg
                )
            elif self.discretization_method == "h3":
                discretized_polys = polygonize_aoi(
                    aoi_geom_dict, res=int(self.discretization_resolution), min_elevation_deg=min_elevation_deg
                )
            else:
                # Fallback to original areas if method unknown
                discretized_polys = [area]

            # Add original_area_id to each discretized polygon
            for poly in discretized_polys:
                if poly.properties is None:
                    poly.properties = {}
                poly.properties["original_area_id"] = original_area_id  # type: ignore

            discretized_areas.extend(discretized_polys)

        self._discretized_areas = discretized_areas

    def _gen_points_from_aoi(self):
        # Generate GroundLocation objects representing the exterior points of the polygons
        # defined by the scenario's discretized areas of interest.
        # In a grid represented by adjacent polygons, points are shared between multiple polygons,
        # therefore to avoid duplicate ground points (and thus extra computations), we do the following:
        #   - identify which points are shared between polygons
        #   - only keep one point but keep track of all polygons this point belongs to
        delta_m_max = 1.0  # distance threshold in meters to decide if a point belongs to a polygon's exterior

        if not self._discretized_areas:
            return

        wgs84 = pyproj.CRS("EPSG:4326")
        mercator = pyproj.CRS("EPSG:3857")
        project = pyproj.Transformer.from_crs(wgs84, mercator, always_xy=True).transform

        # Collect all points first to enable batch processing
        all_points_data = []

        for polygon_id, polygon in enumerate(self._discretized_areas):
            geometry = polygon.geometry
            exterior = geometry.exterior  # type: ignore
            polygon.properties["polygon_id"] = polygon_id  # type: ignore
            # Omitting the last point which is the same as the first point
            n_points = len(exterior) - 1  # type: ignore
            polygon.properties["n_exterior_points"] = n_points  # type: ignore
            min_elevation_deg = polygon.properties.get("min_elevation_deg", 0.0)  # type: ignore

            for point_id in range(n_points):
                point = exterior[point_id]  # type: ignore
                all_points_data.append(
                    {
                        "lon": point.longitude,
                        "lat": point.latitude,
                        "polygon_id": polygon_id,
                        "min_elevation_deg": min_elevation_deg,
                    }
                )

        if not all_points_data:
            return

        # Batch transform all coordinates
        lons = [p["lon"] for p in all_points_data]
        lats = [p["lat"] for p in all_points_data]
        x_coords, y_coords = project(lons, lats)

        # Use a more efficient spatial indexing approach
        unique_points = {}  # (x_rounded, y_rounded) -> ground_point_data
        point_to_polygons = {}  # point_key -> list of polygon_ids

        # Round coordinates to create a coarse spatial grid for fast lookup
        # Use a grid size that's smaller than delta_m_max for accurate results
        grid_size = delta_m_max * 0.5  # 0.5 meter grid

        for i, (x, y) in enumerate(zip(x_coords, y_coords, strict=True)):
            point_data = all_points_data[i]

            # Create a spatial key for fast lookup
            x_key = round(x / grid_size)
            y_key = round(y / grid_size)

            # Check nearby grid cells for existing points
            found_match = False
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    check_key = (x_key + dx, y_key + dy)
                    if check_key in unique_points:
                        existing_x, existing_y = unique_points[check_key]["coords"]
                        distance = ((x - existing_x) ** 2 + (y - existing_y) ** 2) ** 0.5

                        if distance < delta_m_max:
                            # Found a nearby point, add this polygon to its list
                            point_to_polygons[check_key].append(point_data["polygon_id"])
                            found_match = True
                            break

                if found_match:
                    break

            if not found_match:
                # Create new unique point
                spatial_key = (x_key, y_key)
                unique_points[spatial_key] = {
                    "coords": (x, y),
                    "ground_location": GroundLocation.from_lla(
                        latitude=point_data["lat"],
                        longitude=point_data["lon"],
                        polygon_ids=[point_data["polygon_id"]],
                        minimum_elevation=Angle.from_degrees(point_data["min_elevation_deg"]),
                    ),
                }
                point_to_polygons[spatial_key] = [point_data["polygon_id"]]

        # Update polygon_ids for all unique points
        for spatial_key, point_data in unique_points.items():
            polygon_ids = point_to_polygons[spatial_key]
            point_data["ground_location"].polygon_ids = polygon_ids

        # Store ground locations in private field
        self._ground_locations = [point_data["ground_location"] for point_data in unique_points.values()]

    @classmethod
    def load_from_file(cls, path: str | os.PathLike) -> Self:
        """Load a scenario from a JSON file with version checking and migration support."""
        json_text = Path(path).read_text()

        # Parse JSON to check version
        data = json_module.loads(json_text)

        # Get the version from the JSON data (default to 0 for legacy files)
        file_version = data.get("version", 0)

        # Apply migrations if needed
        if file_version < CURRENT_SCENARIO_VERSION:
            data = cls._migrate_scenario_data(data, file_version)
            # Update to current version after migration
            data["version"] = CURRENT_SCENARIO_VERSION
            json_text = json_module.dumps(data)
        elif file_version > CURRENT_SCENARIO_VERSION:
            error_message = (
                f"Scenario file version {file_version} is newer than supported version {CURRENT_SCENARIO_VERSION}. "
                f"Please update the ephemerista package."
            )
            raise ValueError(error_message)

        return cls.model_validate_json(json_text)

    @classmethod
    def _migrate_scenario_data(cls, data: dict, from_version: int) -> dict:
        """Migrate scenario data from an older version to the current version."""
        # Version 0 to 1: Legacy files without version field
        if from_version == 0:
            # No structural changes needed, just adding version field
            # which is handled in load_from_file
            pass

        # Future migrations would be added here
        # Example:
        # if from_version < 2:
        #     data = cls._migrate_v1_to_v2(data)

        return data

    def _get_asset(self, asset: AssetKey | str) -> Asset | None:
        if isinstance(asset, str):
            return next((a for a in self.all_assets if a.name == asset), None)
        return next((a for a in self.all_assets if a.asset_id == _asset_id(asset)), None)

    def __getitem__(self, key: AssetKey | str) -> Asset:
        """Look up an asset based on its name or UUID."""
        asset = self._get_asset(key)
        if not asset:
            raise KeyError()
        return asset

    def channel_by_id(self, channel_id: UUID5) -> Channel:
        """Look up a communications channel based on its UUID."""
        return next(c for c in self.channels if c.channel_id == channel_id)

    @property
    def times(self) -> list[Time]:
        """list[Time]: Time steps."""
        return self.start_time.trange(self.end_time, self.time_step)

    @cached_property
    def all_assets(self) -> list[Asset]:
        """list[Asset]: All constellation assets and additional assets."""
        assets = self.assets.copy()
        for constellation in self.constellations:
            assets.extend(constellation.assets)
        return assets

    @property
    def ground_locations(self) -> list[GroundLocation]:
        """list[GroundLocation]: All ground locations from areas of interest."""
        return self._ground_locations

    @property
    def discretized_areas(self) -> list[Feature[Polygon, dict]]:
        """list[Feature[Polygon, dict]]: Discretized areas of interest."""
        return self._discretized_areas

    def get_discretized_to_original_mapping(self) -> dict[int, int]:
        """Get mapping from discretized polygon ID to original area ID.

        Returns
        -------
        dict[int, int]
            Dictionary mapping discretized polygon index to original area index
        """
        mapping = {}
        for polygon_id, polygon in enumerate(self._discretized_areas):
            original_area_id = polygon.properties.get("original_area_id")  # type: ignore
            if original_area_id is not None:
                mapping[polygon_id] = original_area_id
        return mapping

    def get_original_to_discretized_mapping(self) -> dict[int, list[int]]:
        """Get mapping from original area ID to list of discretized polygon IDs.

        Returns
        -------
        dict[int, list[int]]
            Dictionary mapping original area index to list of discretized polygon indices
        """
        mapping = {}
        for polygon_id, polygon in enumerate(self._discretized_areas):
            original_area_id = polygon.properties.get("original_area_id")  # type: ignore
            if original_area_id is not None:
                if original_area_id not in mapping:
                    mapping[original_area_id] = []
                mapping[original_area_id].append(polygon_id)
        return mapping

    def propagate(self) -> Ensemble:
        """Propagate the state of all assets in the scenario.

        Returns
        -------
        Ensemble
            A collection of all propagated trajectories
        """
        trajectories = {}

        for asset in self.all_assets:
            trajectories[asset.asset_id] = asset.model.propagate(self.times)

        return Ensemble(trajectories=trajectories)
