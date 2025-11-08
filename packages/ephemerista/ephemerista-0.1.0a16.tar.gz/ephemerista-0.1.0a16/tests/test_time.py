import pytest

from ephemerista import BaseModel
from ephemerista.time import Time


def test_deserialization():
    class Model(BaseModel):
        time: Time

    json = r"""{
        "time": {
            "scale": "TDB",
            "timestamp": {
                "type": "iso",
                "value": "2024-01-01T12:13:14.123"
            }
        }
    }"""
    model = Model.model_validate_json(json)
    assert model.time.year == 2024
    assert model.time.month == 1
    assert model.time.day == 1
    assert model.time.hour == 12
    assert model.time.minute == 13
    assert model.time.second == 14
    assert model.time.seconds == 14.123
    assert model.time.julian_date == 2460311.0091912383

    json = r"""{
        "time": {
            "scale": "TDB",
            "timestamp": {
                "type": "jd",
                "value": 2460311.0091912383
            }
        }
    }"""
    model = Model.model_validate_json(json)
    assert model.time.year == 2024
    assert model.time.month == 1
    assert model.time.day == 1
    assert model.time.hour == 12
    assert model.time.minute == 13
    assert model.time.second == 14
    assert model.time.seconds == pytest.approx(14.123, rel=1e-4)
    assert model.time.julian_date == 2460311.0091912383


def test_iso():
    iso = "2024-01-01T12:13:14.123"
    time = Time.from_iso("TDB", iso)
    assert time.year == 2024
    assert time.month == 1
    assert time.day == 1
    assert time.hour == 12
    assert time.minute == 13
    assert time.second == 14
    assert time.seconds == 14.123
    assert time.julian_date == 2460311.0091912383


def test_utc():
    utc = "2024-01-01T12:13:14.123"
    time = Time.from_utc(utc)
    assert time.scale == "TAI"
    assert time.year == 2024
    assert time.month == 1
    assert time.day == 1
    assert time.hour == 12
    assert time.minute == 13
    assert time.second == 51
    assert time.seconds == 51.123
    assert time.julian_date == 2460311.009619479


def test_julian_date():
    jd = 2460311.0091912383
    time = Time.from_julian_date("TDB", jd)
    assert time.year == 2024
    assert time.month == 1
    assert time.day == 1
    assert time.hour == 12
    assert time.minute == 13
    assert time.second == 14
    assert time.seconds == pytest.approx(14.123, rel=1e-4)
    assert time.julian_date == 2460311.0091912383


def test_j2000():
    j2k = 8766.0091912383
    time = Time.from_j2000("TDB", j2k)
    assert time.year == 2024
    assert time.month == 1
    assert time.day == 1
    assert time.hour == 12
    assert time.minute == 13
    assert time.second == 14
    assert time.seconds == pytest.approx(14.123, rel=1e-4)
    assert time.julian_date == 2460311.0091912383
