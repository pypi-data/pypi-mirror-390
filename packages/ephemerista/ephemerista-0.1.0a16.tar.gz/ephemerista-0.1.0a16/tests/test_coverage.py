import pytest
from pyproj import Geod
from shapely.geometry import Polygon

from ephemerista.scenarios import polygonize_aoi, polygonize_aoi_rectangles
from tests.conftest import get_validated_coverage_geojson_dict


@pytest.mark.parametrize(
    "aoi_geom_dict, expected_len_of_polygons",
    [
        (get_validated_coverage_geojson_dict(file_name="single_aoi.geojson"), 222),
        (get_validated_coverage_geojson_dict(file_name="simple_polygons.geojson"), 3),
        (get_validated_coverage_geojson_dict(file_name="single_aoi_crosses_antimeridian.geojson"), 4),
    ],
)
def test_polygonize_aoi(
    aoi_geom_dict: dict,
    expected_len_of_polygons: int,
):
    """polygonize_aoi shall be able to compute a list of polygons for a given area of interest (AOI) geometry"""
    feature_list = polygonize_aoi(aoi_geom_dict=aoi_geom_dict, res=1)
    assert len(feature_list) == expected_len_of_polygons


@pytest.mark.parametrize(
    "aoi_geom_dict, expected_len_of_polygons",
    [
        (get_validated_coverage_geojson_dict(file_name="single_aoi.geojson"), 378),
        (get_validated_coverage_geojson_dict(file_name="simple_polygons.geojson"), 12),
        (get_validated_coverage_geojson_dict(file_name="single_aoi_crosses_antimeridian.geojson"), 12),
    ],
)
def test_polygonize_aoi_rectangles(
    aoi_geom_dict: dict,
    expected_len_of_polygons: int,
):
    """polygonize_aoi_rectangles shall be able to compute a list of polygons
    for a given area of interest (AOI) geometry"""
    feature_list = polygonize_aoi_rectangles(aoi_geom_dict=aoi_geom_dict, vertex_degrees=6)
    assert len(feature_list) == expected_len_of_polygons


@pytest.mark.parametrize(
    "aoi_geom_dict, expected_error_in_percentage",
    [
        (get_validated_coverage_geojson_dict(file_name="single_aoi_full_latitude_range.geojson"), 1.0),
    ],
)
def test_polygonize_aoi_rectangles_generate_similar_areas(
    aoi_geom_dict: dict,
    expected_error_in_percentage: float,
):
    """polygonize_aoi_rectangles shall generate polygons with similar areas
    for a given area of interest (AOI) geometry"""
    feature_list = polygonize_aoi_rectangles(aoi_geom_dict=aoi_geom_dict, vertex_degrees=6)
    max_area = 0
    min_area = 0
    for feature in feature_list:
        polygon = Polygon([(p.longitude, p.latitude) for p in feature.geometry.coordinates[0]])
        geod = Geod(ellps="WGS84")
        poly_area, _ = geod.geometry_area_perimeter(polygon)
        max_area = max(max_area, poly_area)
        if min_area == 0 or poly_area < min_area:
            min_area = poly_area

    error_in_percentage = (max_area - min_area) / max_area * 100
    assert error_in_percentage < expected_error_in_percentage, (
        f"Error in area is {error_in_percentage:.2f}%, "
        f"which is greater than the expected {expected_error_in_percentage}%"
    )
