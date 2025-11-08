import numpy as np
import pytest
from pytest import approx

from ephemerista.math import cone_vectors, orthonormal_base_from_one_vec


def test_create_orthogonal_base():
    v1 = np.array([0.5, 0.6, 0.7])
    v1_actual, v2_actual, v3_actual = orthonormal_base_from_one_vec(v1)
    np.testing.assert_allclose(v1_actual, v1 / np.linalg.norm(v1))
    assert np.linalg.norm(v1_actual) == approx(1.0, abs=1e-9)
    assert np.linalg.norm(v2_actual) == approx(1.0, abs=1e-9)
    assert np.linalg.norm(v3_actual) == approx(1.0, abs=1e-9)
    assert np.dot(v1_actual, v2_actual) == approx(0.0, abs=1e-9)
    assert np.dot(v2_actual, v3_actual) == approx(0.0, abs=1e-9)
    assert np.dot(v1_actual, v3_actual) == approx(0.0, abs=1e-9)
    np.testing.assert_allclose(np.cross(v1_actual, v2_actual), v3_actual)
    np.testing.assert_allclose(np.cross(v2_actual, v3_actual), v1_actual)


@pytest.mark.parametrize("theta_deg", [135.0])
def test_cone_vectors_invalid(theta_deg):
    v1 = np.array([0.5, 0.6, 0.7])

    angle_res_deg = 1.0
    with pytest.raises(ValueError):
        cone_vectors(v1, theta_deg, angle_res_deg)


@pytest.mark.parametrize("theta_deg", [-90.0, -45.0, 0.0, 45.0, 90.0])
def test_cone_vectors(theta_deg):
    v1 = np.array([0.5, 0.6, 0.7])

    angle_res_deg = 1.0
    cone_vecs, _ = cone_vectors(v1, theta_deg, angle_res_deg)

    v1_normalized = v1 / np.linalg.norm(v1)
    cos_theta = np.cos(np.deg2rad(theta_deg))
    for cone_vec in cone_vecs:
        assert np.linalg.norm(cone_vec) == approx(1.0, abs=1e-9)
        assert np.dot(cone_vec, v1_normalized) == approx(cos_theta, abs=1e-9)
