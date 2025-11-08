import pytest
from pydantic import Field

from ephemerista import BaseModel
from ephemerista.bodies import Origin
from ephemerista.coords import shapes

MEAN_RADIUS: float = Origin(name="Earth").mean_radius
SEMI_MAJOR_AXIS: float = 6785.024983263093
ECCENTRICITY: float = 0.0006796632490758143
APOAPSIS_RADIUS: float = 6789.636515388278
PERIAPSIS_RADIUS: float = 6780.413451137908
PERIAPSIS_ALTITUDE: float = PERIAPSIS_RADIUS - MEAN_RADIUS
APOAPSIS_ALTITUDE: float = APOAPSIS_RADIUS - MEAN_RADIUS


def test_deserialization():
    class Model(BaseModel):
        shape: shapes.Shape = Field(discriminator=shapes.DISCRIMINATOR)

    json = f"""
    {{
        "shape": {{
            "type": "semi_major",
            "semiMajorAxis": {SEMI_MAJOR_AXIS},
            "eccentricity": {ECCENTRICITY}
        }}
    }}
    """
    model = Model.model_validate_json(json)
    assert isinstance(model, Model)

    json = f"""
    {{
        "shape": {{
            "type": "radii",
            "periapsisRadius": {PERIAPSIS_RADIUS},
            "apoapsisRadius": {APOAPSIS_RADIUS}
        }}
    }}
    """
    model = Model.model_validate_json(json)
    assert isinstance(model, Model)

    json = f"""
    {{
        "shape": {{
            "type": "altitudes",
            "periapsisAltitude": {PERIAPSIS_ALTITUDE},
            "apoapsisAltitude": {APOAPSIS_ALTITUDE}
        }}
    }}
    """
    model = Model.model_validate_json(json)
    assert isinstance(model, Model)


def test_semi_major():
    shape = shapes.SemiMajorAxisShape(sma=SEMI_MAJOR_AXIS, ecc=ECCENTRICITY)
    assert shape.semi_major_axis(MEAN_RADIUS) == pytest.approx(SEMI_MAJOR_AXIS, rel=1e-8)
    assert shape.eccentricity(MEAN_RADIUS) == pytest.approx(ECCENTRICITY, abs=1e-8)
    assert shape.periapsis_radius(MEAN_RADIUS) == pytest.approx(PERIAPSIS_RADIUS, rel=1e-8)
    assert shape.apoapsis_radius(MEAN_RADIUS) == pytest.approx(APOAPSIS_RADIUS, rel=1e-8)


def test_radii():
    shape = shapes.RadiiShape(rp=PERIAPSIS_RADIUS, ra=APOAPSIS_RADIUS)
    assert shape.semi_major_axis(MEAN_RADIUS) == pytest.approx(SEMI_MAJOR_AXIS, rel=1e-8)
    assert shape.eccentricity(MEAN_RADIUS) == pytest.approx(ECCENTRICITY, abs=1e-8)
    assert shape.periapsis_radius(MEAN_RADIUS) == pytest.approx(PERIAPSIS_RADIUS, rel=1e-8)
    assert shape.apoapsis_radius(MEAN_RADIUS) == pytest.approx(APOAPSIS_RADIUS, rel=1e-8)


def test_altitudes():
    shape = shapes.AltitudesShape(periapsisAltitude=PERIAPSIS_ALTITUDE, apoapsisAltitude=APOAPSIS_ALTITUDE)
    assert shape.semi_major_axis(MEAN_RADIUS) == pytest.approx(SEMI_MAJOR_AXIS, rel=1e-8)
    assert shape.eccentricity(MEAN_RADIUS) == pytest.approx(ECCENTRICITY, abs=1e-8)
    assert shape.periapsis_radius(MEAN_RADIUS) == pytest.approx(PERIAPSIS_RADIUS, rel=1e-8)
    assert shape.apoapsis_radius(MEAN_RADIUS) == pytest.approx(APOAPSIS_RADIUS, rel=1e-8)
