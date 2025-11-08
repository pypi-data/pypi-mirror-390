import pytest

from ephemerista import BaseModel
from ephemerista.bodies import Origin


def test_invalid():
    with pytest.raises(ValueError):
        Origin(name="Rupert")


def test_deserialization():
    class Model(BaseModel):
        body: Origin

    json = r'{"body": {"name": "sun"}}'
    model = Model.model_validate_json(json)
    assert isinstance(model, Model)
    assert model.body.name == "Sun"

    json = r'{"body": {"name": "ssb"}}'
    model = Model.model_validate_json(json)
    assert isinstance(model, Model)
    assert model.body.name == "Solar System Barycenter"

    json = r'{"body": {"name": "Earth"}}'
    model = Model.model_validate_json(json)
    assert isinstance(model, Model)
    assert model.body.name == "Earth"

    json = r'{"body": {"name": "Moon"}}'
    model = Model.model_validate_json(json)
    assert isinstance(model, Model)
    assert model.body.name == "Moon"

    json = r'{"body": {"name": "Ceres"}}'
    model = Model.model_validate_json(json)
    assert isinstance(model, Model)
    assert model.body.name == "Ceres"


def test_barycenter():
    ssb = Origin(name="ssb")
    assert ssb.name == "Solar System Barycenter"
    assert ssb.naif_id == 0
    assert ssb.gravitational_parameter == pytest.approx(132712440041.27942, rel=1e-8)


def test_sun():
    sun = Origin(name="Sun")
    assert sun.name == "Sun"
    assert sun.naif_id == 10
    assert sun.gravitational_parameter == pytest.approx(132712440041.27942, rel=1e-8)
    # assert sun.mean_radius == pytest.approx(695700.0, rel=1e-8)
    assert sun.polar_radius == pytest.approx(695700.0, rel=1e-8)
    assert sun.equatorial_radius == pytest.approx(695700.0, rel=1e-8)


def test_planet():
    earth = Origin(name="earth")
    assert earth.name == "Earth"
    assert earth.naif_id == 399
    assert earth.gravitational_parameter == pytest.approx(398600.43550702266, rel=1e-8)
    assert earth.mean_radius == pytest.approx(6371.008367, rel=1e-8)
    assert earth.polar_radius == pytest.approx(6356.7519, rel=1e-8)
    assert earth.equatorial_radius == pytest.approx(6378.1366, rel=1e-8)


def test_satellite():
    moon = Origin(name="luna")
    assert moon.name == "Moon"
    assert moon.naif_id == 301
    assert moon.mean_radius == pytest.approx(1737.4, rel=1e-8)
    assert moon.polar_radius == pytest.approx(1737.4, rel=1e-8)
    assert moon.equatorial_radius == pytest.approx(1737.4, rel=1e-8)


def test_minor_body():
    ceres = Origin(name="ceres")
    assert ceres.name == "Ceres"
    assert ceres.naif_id == 2000001
    assert ceres.mean_radius == pytest.approx(470.0, rel=1e-8)
    assert ceres.equatorial_radius == pytest.approx(487.3, rel=1e-8)
    assert ceres.polar_radius == pytest.approx(446.0, rel=1e-8)
