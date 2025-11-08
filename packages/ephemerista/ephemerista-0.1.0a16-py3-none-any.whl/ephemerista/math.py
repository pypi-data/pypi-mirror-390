"""The math.py module.

This module provides mathematical utility functions.
"""

import math

import numpy as np


def unit_vector(vector: np.ndarray) -> np.ndarray:
    """Return the unit vector of the given vector."""
    return vector / np.linalg.norm(vector)


def angle_between(v1: np.ndarray, v2: np.ndarray) -> float:
    """Return the angle in radians between vectors `v1` and `v2`.

    Examples
    --------
    >>> angle_between((1, 0, 0), (0, 1, 0))
    1.5707963267948966
    >>> angle_between((1, 0, 0), (1, 0, 0))
    0.0
    >>> angle_between((1, 0, 0), (-1, 0, 0))
    3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def orthonormal_base_from_one_vec(v1: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Create an orthonormal base completing the given vector v1, using the Gram-Schmidt procedure.

    Source: https://stackoverflow.com/questions/33658620/generating-two-orthogonal-vectors-that-are-orthogonal-to-a-particular-direction
    """
    v1 = v1 / np.linalg.norm(v1)
    x = np.random.randn(3)  # take a random vector
    x -= x.dot(v1) * v1  # make it orthogonal to v1
    v2 = x / np.linalg.norm(x)  # normalize it
    v3 = np.cross(v1, v2)  # cross product with k
    return v1, v2, v3


def cone_vectors(
    v1: np.ndarray,
    theta_deg: float,
    angle_res_deg: float,
    include_endpoint: bool = False,  # noqa: FBT001, FBT002
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate a set of vectors representing the surface of a cone.

    Parameters
    ----------
    v1: numpy 3*1 array
        The cone's axis vector

    theta_deg: float
        The cone's half aperture. Must be in the [-90, 90°] range.

    angle_res_deg: float
        The angular resolution of the cone in degrees

    Returns
    -------
    a n*3 numpy array containing the n vectors representing the cone surface
    """
    if theta_deg > 90.0:  # noqa: PLR2004
        msg = "Cone half aperture angle cannot be higher than 90°"
        raise ValueError(msg)

    # First build the cone in the cone's coordinate frame, where the first axis is the cone's axis vector
    n_phi = int(2 * np.pi / np.deg2rad(angle_res_deg))
    phi_array = np.linspace(0, 2 * np.pi, n_phi, endpoint=include_endpoint)
    tan_theta = np.tan(np.deg2rad(theta_deg))
    cone_vecs_cone = np.array([np.ones_like(phi_array), tan_theta * np.cos(phi_array), tan_theta * np.sin(phi_array)]).T
    cone_vecs_cone = cone_vecs_cone / np.linalg.norm(cone_vecs_cone, axis=1, keepdims=True)

    # Then transform the vectors into v1's coordinate frame, which we call "body" frame here
    v1, v2, v3 = orthonormal_base_from_one_vec(v1)
    dcm_body_from_cone = np.vstack((v1, v2, v3)).T
    rotation_matrices = np.tile(dcm_body_from_cone, (len(cone_vecs_cone), 1, 1))
    cone_vecs_body = np.einsum("kij,kj->ki", rotation_matrices, cone_vecs_cone)

    return cone_vecs_body, phi_array


def normalize_two_pi(angle: float, center: float = 0.0):
    """Normalize `angle` to be in the interval `[center-π, center+π]`."""
    return angle - math.tau * math.floor((angle + math.pi - center) / math.tau)
