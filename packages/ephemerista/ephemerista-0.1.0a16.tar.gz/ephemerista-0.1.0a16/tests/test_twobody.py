import math

import numpy as np
import numpy.testing as npt
import pytest
from pydantic import Field
from pytest import approx

from ephemerista import BaseModel
from ephemerista.bodies import Origin
from ephemerista.coords.twobody import GEO, LEO, MEO, SSO, Cartesian, Keplerian, TwoBodyType
from ephemerista.time import Time


def test_deserialization():
    class Model(BaseModel):
        state: TwoBodyType = Field(discriminator="state_type")

    json = r"""{
        "state": {
            "time": {
                "scale": "TAI",
                "timestamp": {
                    "type": "utc",
                    "value": "2025-03-20T00:00:00.000Z"
                }
            },
            "origin": {"name": "Earth"},
            "type": "cartesian",
            "frame": {"abbreviation": "ICRF"},
            "x": 6068.27927,
            "y": -1692.84394,
            "z": -2516.61918,
            "vx": -0.660415582,
            "vy": 5.495938726,
            "vz": -5.303093233
        }
    }"""
    model = Model.model_validate_json(json)
    assert isinstance(model.state, Cartesian)


def test_elliptic():
    time = Time.from_iso("TDB", "2016-05-30T12:00:00")
    r = np.array([6068.27927, -1692.84394, -2516.61918])
    v = np.array([-0.660415582, 5.495938726, -5.303093233])

    elements = np.array(
        [
            6785.0281175534465,
            0.0006796632490758745,
            51.698121020902995,
            146.0217323119771,
            130.632025321773,
            77.57833314372851,
        ]
    )

    c = Cartesian.from_rv(time, r, v)
    k = Keplerian.from_elements(time, *elements, angle_unit="degrees")

    c1 = k.to_cartesian()
    k1 = c.to_keplerian()

    assert c1.x == approx(c.x)
    assert c1.y == approx(c.y)
    assert c1.z == approx(c.z)
    assert c1.vx == approx(c.vx)
    assert c1.vy == approx(c.vy)
    assert c1.vz == approx(c.vz)

    assert k1.semi_major_axis == approx(k.semi_major_axis)
    assert k1.eccentricity == approx(k.eccentricity)
    assert k1.inclination == approx(k.inclination)
    assert k1.ascending_node == approx(k.ascending_node)
    assert k1.periapsis_argument == approx(k.periapsis_argument)
    assert k1.true_anomaly == approx(k.true_anomaly)


def test_radii():
    elements = np.array([24464560.0, 0.7311, 0.122138, 1.00681, 3.10686, 0.44369564302687126])
    time = Time.from_iso("TDB", "2024-01-22T12:50:00")
    k = Keplerian.from_elements(time, *elements, angle_unit="radians")
    rm = k.origin.mean_radius
    ra = k.apoapsis_radius
    rp = k.periapsis_radius
    aa = ra - rm
    ap = rp - rm
    k1 = Keplerian.from_radii(time, ra, rp, *elements[2:])
    k2 = Keplerian.from_altitudes(time, aa, ap, *elements[2:])
    assert k.semi_major_axis == approx(k1.semi_major_axis)
    assert k.semi_major_axis == approx(k2.semi_major_axis)
    assert k.eccentricity == approx(k1.eccentricity)
    assert k.eccentricity == approx(k2.eccentricity)


def test_mean_anomaly():
    elements = np.array([24464560.0, 0.7311, 0.122138, 1.00681, 3.10686, 0.44369564302687126])
    elements_mean = np.array([24464560.0, 0.7311, 0.122138, 1.00681, 3.10686, 0.04836300000000002])
    true_anomaly = elements[-1]
    mean_anomaly = elements_mean[-1]
    time = Time.from_iso("TDB", "2024-01-22T12:50:00")
    k = Keplerian.from_elements(time, *elements, angle_unit="radians")
    k1 = Keplerian.from_elements(time, *elements_mean, angle_unit="radians", anomaly_type="mean")
    assert k.true_anomaly == approx(true_anomaly)
    assert k1.true_anomaly == approx(true_anomaly)
    assert k.mean_anomaly == approx(mean_anomaly)
    assert k1.mean_anomaly == approx(mean_anomaly)


def test_lvlh():
    jd = 2.4591771079398147e6
    time = Time.from_julian_date("TDB", jd)
    semi_major = 7210.008367
    eccentricity = 0.0001807
    inclination = 51.6428
    ascending_node = 279.6468
    periapsis_arg = 68.3174
    true_anomaly = -68.2025
    k = Keplerian.from_elements(
        time, semi_major, eccentricity, inclination, ascending_node, periapsis_arg, true_anomaly
    )
    s = k.to_cartesian()
    rot = s.rotation_lvlh()
    r = s.position
    rn = r / np.linalg.norm(r)
    v = s.velocity
    vn = v / np.linalg.norm(v)
    npt.assert_allclose(rot.T @ vn, np.array([1, 0, 0]), atol=1e-3)
    npt.assert_allclose(rot.T @ -rn, np.array([0, 0, 1]), atol=1e-3)


def test_new_orbital_types_deserialization():
    """Test that new orbital types can be deserialized with discriminators."""

    class Model(BaseModel):
        state: TwoBodyType = Field(discriminator="state_type")

    # Test LEO deserialization
    leo_json = r"""{
        "state": {
            "time": {
                "scale": "TAI",
                "timestamp": {
                    "type": "utc",
                    "value": "2024-06-01T12:00:00.000Z"
                }
            },
            "origin": {"name": "Earth"},
            "type": "leo",
            "altitude": 400.0,
            "inclination": 51.6
        }
    }"""
    model = Model.model_validate_json(leo_json)
    assert isinstance(model.state, LEO)
    assert model.state.altitude == 400.0
    assert model.state.inclination == approx(51.6)

    # Test SSO deserialization
    sso_json = r"""{
        "state": {
            "time": {
                "scale": "TAI",
                "timestamp": {
                    "type": "utc",
                    "value": "2024-06-01T12:00:00.000Z"
                }
            },
            "origin": {"name": "Earth"},
            "type": "sso",
            "altitude": 800.0,
            "ltan": 10.5
        }
    }"""
    model = Model.model_validate_json(sso_json)
    assert isinstance(model.state, SSO)
    assert model.state.altitude == 800.0
    assert model.state.ltan == approx(10.5)


def test_leo_altitude_validation():
    """Test LEO altitude validation limits."""
    time = Time.from_components("TAI", 2024, 6, 1, 12, 0, 0.0)
    earth = Origin(name="Earth")

    # Valid LEO altitudes
    leo_valid = LEO(time=time, altitude=400.0, origin=earth)
    assert leo_valid.altitude == 400.0

    leo_min = LEO(time=time, altitude=160.0, origin=earth)
    assert leo_min.altitude == 160.0

    leo_max = LEO(time=time, altitude=2000.0, origin=earth)
    assert leo_max.altitude == 2000.0

    # Invalid LEO altitudes
    with pytest.raises(ValueError, match="LEO altitude must be between"):
        LEO(time=time, altitude=50.0, origin=earth)

    with pytest.raises(ValueError, match="LEO altitude must be between"):
        LEO(time=time, altitude=2001.0, origin=earth)


def test_meo_altitude_validation():
    """Test MEO altitude validation limits."""
    time = Time.from_components("TAI", 2024, 6, 1, 12, 0, 0.0)
    earth = Origin(name="Earth")

    # Valid MEO altitudes
    meo_valid = MEO(time=time, altitude=20200.0, origin=earth)
    assert meo_valid.altitude == 20200.0

    meo_min = MEO(time=time, altitude=2000.0, origin=earth)
    assert meo_min.altitude == 2000.0

    meo_max = MEO(time=time, altitude=35786.0, origin=earth)
    assert meo_max.altitude == 35786.0

    # Invalid MEO altitudes
    with pytest.raises(ValueError, match="MEO altitude must be between"):
        MEO(time=time, altitude=1999.0, origin=earth)

    with pytest.raises(ValueError, match="MEO altitude must be between"):
        MEO(time=time, altitude=40000.0, origin=earth)


def test_leo_to_keplerian_conversion():
    """Test LEO to Keplerian conversion."""
    time = Time.from_components("TAI", 2024, 6, 1, 12, 0, 0.0)
    earth = Origin(name="Earth")

    # Create ISS-like LEO
    leo = LEO(time=time, altitude=408.0, inclination=51.6, origin=earth)
    kep = leo.to_keplerian()

    # Verify conversion
    assert kep.semi_major_axis == approx(6371.01 + 408.0, rel=1e-3)  # Earth radius + altitude
    assert kep.eccentricity == approx(0.0, abs=1e-6)  # Circular orbit
    assert math.degrees(kep.inclination) == approx(51.6, rel=1e-3)
    assert kep.orbital_period.to_decimal_seconds() == approx(5565.0, rel=1e-2)  # ~92.7 minutes


def test_meo_to_keplerian_conversion():
    """Test MEO to Keplerian conversion."""
    time = Time.from_components("TAI", 2024, 6, 1, 12, 0, 0.0)
    earth = Origin(name="Earth")

    # Create GPS-like MEO
    meo = MEO(time=time, altitude=20200.0, inclination=55.0, origin=earth)
    kep = meo.to_keplerian()

    # Verify conversion
    assert kep.semi_major_axis == approx(6371.01 + 20200.0, rel=1e-3)
    assert kep.eccentricity == approx(0.0, abs=1e-6)
    assert math.degrees(kep.inclination) == approx(55.0, rel=1e-3)
    assert kep.orbital_period.to_decimal_seconds() == approx(43082.0, rel=1e-2)  # ~12 hours


def test_geo_properties():
    """Test GEO specific properties."""
    time = Time.from_components("TAI", 2024, 6, 1, 12, 0, 0.0)
    earth = Origin(name="Earth")

    geo = GEO(time=time, longitude=75.0, origin=earth)

    # Test fixed properties
    assert geo.altitude == 35786.0
    assert geo.longitude == 75.0
    assert geo.inclination == 0.0

    # Test conversion to Keplerian
    kep = geo.to_keplerian()
    assert kep.semi_major_axis == approx(42157.01, rel=1e-3)
    assert math.degrees(kep.inclination) == approx(0.0, abs=1e-6)

    # Test geostationary period (~24 hours)
    period_hours = kep.orbital_period.to_decimal_seconds() / 3600
    assert period_hours == approx(23.934, rel=1e-2)


def test_sso_ltan_to_raan_conversion():
    """Test SSO LTAN to RAAN conversion."""
    time = Time.from_components("TAI", 2024, 6, 1, 12, 0, 0.0)
    earth = Origin(name="Earth")

    # Create sun-synchronous orbit
    sso = SSO(time=time, altitude=800.0, ltan=10.5, origin=earth)
    kep = sso.to_keplerian()

    # Test that LTAN affects RAAN
    sso_different_ltan = SSO(time=time, altitude=800.0, ltan=14.5, origin=earth)
    kep_different = sso_different_ltan.to_keplerian()

    # Different LTAN should produce different RAAN
    raan_diff = abs(math.degrees(kep.ascending_node) - math.degrees(kep_different.ascending_node))
    raan_diff = min(raan_diff, 360 - raan_diff)  # Handle wraparound
    expected_diff = abs(10.5 - 14.5) * 15  # 4 hours * 15 deg/hour = 60 degrees
    assert raan_diff == approx(expected_diff, rel=1e-1)


def test_sso_inclination_calculation():
    """Test SSO sun-synchronous inclination calculation."""
    time = Time.from_components("TAI", 2024, 6, 1, 12, 0, 0.0)
    earth = Origin(name="Earth")

    # Test different altitudes produce different inclinations
    altitudes = [600.0, 800.0, 1000.0]
    inclinations = []

    for alt in altitudes:
        sso = SSO(time=time, altitude=alt, ltan=10.5, origin=earth)
        kep = sso.to_keplerian()
        inclinations.append(math.degrees(kep.inclination))

    # Higher altitude should require higher inclination for sun-synchronous orbit
    assert inclinations[1] > inclinations[0]  # 800km > 600km inclination
    assert inclinations[2] > inclinations[1]  # 1000km > 800km inclination

    # All should be reasonable sun-synchronous inclinations (typically 97-102 degrees)
    for inc in inclinations:
        assert 95 < inc < 105


def test_round_trip_conversions():
    """Test round-trip conversions between new orbital types and standard forms."""
    time = Time.from_components("TAI", 2024, 6, 1, 12, 0, 0.0)
    earth = Origin(name="Earth")

    # Test LEO round-trip
    leo_original = LEO(time=time, altitude=500.0, inclination=60.0, origin=earth)
    leo_kep = leo_original.to_keplerian()
    leo_cart = leo_kep.to_cartesian()
    leo_kep_back = leo_cart.to_keplerian()

    assert leo_kep.semi_major_axis == approx(leo_kep_back.semi_major_axis, rel=1e-6)
    assert leo_kep.eccentricity == approx(leo_kep_back.eccentricity, abs=1e-8)
    assert leo_kep.inclination == approx(leo_kep_back.inclination, rel=1e-6)

    # Test MEO round-trip
    meo_original = MEO(time=time, altitude=15000.0, inclination=45.0, origin=earth)
    meo_kep = meo_original.to_keplerian()
    meo_cart = meo_kep.to_cartesian()
    meo_kep_back = meo_cart.to_keplerian()

    assert meo_kep.semi_major_axis == approx(meo_kep_back.semi_major_axis, rel=1e-6)
    assert meo_kep.eccentricity == approx(meo_kep_back.eccentricity, abs=1e-8)
    assert meo_kep.inclination == approx(meo_kep_back.inclination, rel=1e-6)


def test_state_type_discriminators():
    """Test that all new orbital types have correct state_type discriminators."""
    time = Time.from_components("TAI", 2024, 6, 1, 12, 0, 0.0)
    earth = Origin(name="Earth")

    sso = SSO(time=time, altitude=800.0, ltan=10.5, origin=earth)
    leo = LEO(time=time, altitude=400.0, origin=earth)
    meo = MEO(time=time, altitude=20200.0, origin=earth)
    geo = GEO(time=time, longitude=0.0, origin=earth)

    assert sso.state_type == "sso"
    assert leo.state_type == "leo"
    assert meo.state_type == "meo"
    assert geo.state_type == "geo"

    # Test serialization includes type
    sso_dict = sso.model_dump(by_alias=True)
    assert sso_dict["type"] == "sso"

    leo_dict = leo.model_dump(by_alias=True)
    assert leo_dict["type"] == "leo"


def test_orbital_periods():
    """Test that orbital periods are physically reasonable."""
    time = Time.from_components("TAI", 2024, 6, 1, 12, 0, 0.0)
    earth = Origin(name="Earth")

    # LEO period should be ~90-120 minutes
    leo = LEO(time=time, altitude=400.0, origin=earth)
    leo_period_min = leo.to_keplerian().orbital_period.to_decimal_seconds() / 60
    assert 85 < leo_period_min < 125

    # MEO (GPS) period should be ~12 hours
    meo = MEO(time=time, altitude=20200.0, origin=earth)
    meo_period_hours = meo.to_keplerian().orbital_period.to_decimal_seconds() / 3600
    assert 11 < meo_period_hours < 13

    # GEO period should be ~24 hours (sidereal day)
    geo = GEO(time=time, longitude=0.0, origin=earth)
    geo_period_hours = geo.to_keplerian().orbital_period.to_decimal_seconds() / 3600
    assert 23.5 < geo_period_hours < 24.5


def test_dataframe_conversion():
    """Test DataFrame conversion for new orbital types."""
    time = Time.from_components("TAI", 2024, 6, 1, 12, 0, 0.0)
    earth = Origin(name="Earth")

    # Test LEO DataFrame
    leo = LEO(time=time, altitude=400.0, inclination=51.6, origin=earth)
    leo_df = leo.to_dataframe()
    assert "orbit_type" in leo_df.columns
    assert leo_df["orbit_type"].iloc[0] == "LEO"
    assert leo_df["altitude"].iloc[0] == 400.0
    assert leo_df["inclination"].iloc[0] == 51.6

    # Test SSO DataFrame
    sso = SSO(time=time, altitude=800.0, ltan=10.5, origin=earth)
    sso_df = sso.to_dataframe()
    assert "orbit_type" in sso_df.columns
    assert sso_df["orbit_type"].iloc[0] == "SSO"
    assert sso_df["altitude"].iloc[0] == 800.0
    assert sso_df["ltan"].iloc[0] == 10.5

    # Test GEO DataFrame
    geo = GEO(time=time, longitude=75.0, origin=earth)
    geo_df = geo.to_dataframe()
    assert "orbit_type" in geo_df.columns
    assert geo_df["orbit_type"].iloc[0] == "GEO"
    assert geo_df["longitude"].iloc[0] == 75.0
    assert geo_df["altitude"].iloc[0] == 35786.0


def test_boundary_conditions():
    """Test boundary conditions for altitude limits."""
    time = Time.from_components("TAI", 2024, 6, 1, 12, 0, 0.0)
    earth = Origin(name="Earth")

    # Test 2000 km boundary (valid for both LEO and MEO)
    leo_boundary = LEO(time=time, altitude=2000.0, origin=earth)
    meo_boundary = MEO(time=time, altitude=2000.0, origin=earth)

    # Both should work and produce same orbital characteristics
    leo_kep = leo_boundary.to_keplerian()
    meo_kep = meo_boundary.to_keplerian()

    assert leo_kep.semi_major_axis == approx(meo_kep.semi_major_axis, rel=1e-6)
    assert leo_kep.orbital_period.to_decimal_seconds() == approx(meo_kep.orbital_period.to_decimal_seconds(), rel=1e-6)


def test_real_world_examples():
    """Test real-world satellite examples."""
    time = Time.from_components("TAI", 2024, 6, 1, 12, 0, 0.0)
    earth = Origin(name="Earth")

    # ISS
    iss = LEO(time=time, altitude=408.0, inclination=51.6, origin=earth)
    iss_period = iss.to_keplerian().orbital_period.to_decimal_seconds() / 60
    assert 90 < iss_period < 95  # ISS period is ~92.7 minutes

    # GPS constellation
    gps = MEO(time=time, altitude=20200.0, inclination=55.0, origin=earth)
    gps_period = gps.to_keplerian().orbital_period.to_decimal_seconds() / 3600
    assert 11.9 < gps_period < 12.1  # GPS period is ~11.97 hours

    # Landsat (sun-synchronous)
    landsat = SSO(time=time, altitude=705.0, ltan=10.0, origin=earth)
    landsat_kep = landsat.to_keplerian()
    landsat_inc = math.degrees(landsat_kep.inclination)
    assert 97 < landsat_inc < 99  # Landsat inclination is ~98.2 degrees

    # GOES (geostationary)
    goes = GEO(time=time, longitude=-75.0, origin=earth)  # GOES-East position
    goes_period = goes.to_keplerian().orbital_period.to_decimal_seconds() / 3600
    assert 23.8 < goes_period < 24.1  # Sidereal day
