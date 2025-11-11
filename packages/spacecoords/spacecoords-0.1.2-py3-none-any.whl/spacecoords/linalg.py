#!/usr/bin/env python

"""Useful utility functions related to linear algebra"""

import numpy as np
import numpy.typing as npt
from .types import (
    NDArray_3,
    NDArray_3xN,
    NDArray_N,
    NDArray_3x3,
    NDArray_3x3xN,
    NDArray_2x2,
    NDArray_NxN,
)


def vector_angle(
    a: NDArray_3 | NDArray_3xN, b: NDArray_3 | NDArray_3xN, degrees: bool = False
) -> NDArray_N | float:
    """Angle between two vectors.

    Parameters
    ----------
    a
        (3, N) or (3,) vector of Cartesian coordinates.
        This argument is vectorized in the second array dimension.
    b
        (3, N) or (3,) vector of Cartesian coordinates.
        This argument is vectorized in the second array dimension.
    degrees
        If `True`, use degrees. Else all angles are given in radians.

    Returns
    -------
        (N, ) or float vector of angles between input vectors.

    Notes
    -----
    Definition
        $$
            \\theta = \\cos^{-1}\\frac{
                \\langle\\mathbf{a},\\mathbf{b}\\rangle
            }{
                |\\mathbf{a}||\\mathbf{b}|
            }
        $$
        where $\\langle\\mathbf{a},\\mathbf{b}\\rangle$ is the dot
        product and $|\\mathbf{a}|$ denotes the norm.

    """
    a_norm = np.linalg.norm(a, axis=0)
    b_norm = np.linalg.norm(b, axis=0)

    if len(a.shape) == 1:
        proj = np.dot(a, b) / (a_norm * b_norm)
    elif len(b.shape) == 1:
        proj = np.dot(b, a) / (a_norm * b_norm)
    else:
        assert a.shape == b.shape, "Input shapes do not match"
        proj = np.sum(a * b, axis=0) / (a_norm * b_norm)

    if len(a.shape) == 1 and len(b.shape) == 1:
        if proj > 1.0:
            proj = 1.0
        elif proj < -1.0:
            proj = -1.0
    else:
        proj[proj > 1.0] = 1.0
        proj[proj < -1.0] = -1.0

    theta = np.arccos(proj)
    if degrees:
        theta = np.degrees(theta)

    return theta


def rot_mat_x(
    theta: NDArray_N | float, dtype: npt.DTypeLike = np.float64, degrees: bool = False
) -> NDArray_3x3xN | NDArray_3x3:
    """Compute matrix for rotation of R3 vector through angle theta
    around the X-axis. For frame rotation, use the transpose.

    Parameters
    ----------
    theta
        Angle to rotate.
    dtype
        Numpy datatype of the rotation matrix.
    degrees
        If `True`, use degrees. Else all angles are given in radians.

    Returns
    -------
        (3, 3) Rotation matrix, or (3, 3, n) tensor if theta is vector input.

    """
    if degrees:
        theta = np.radians(theta)
    size: tuple[int, ...]
    if isinstance(theta, np.ndarray) and theta.ndim > 0:
        size = (3, 3, len(theta))
    else:
        size = (3, 3)

    ca, sa = np.cos(theta), np.sin(theta)
    rot = np.zeros(size, dtype=dtype)
    rot[0, 0, ...] = 1
    rot[1, 1, ...] = ca
    rot[1, 2, ...] = -sa
    rot[2, 1, ...] = sa
    rot[2, 2, ...] = ca
    return rot


def rot_mat_y(
    theta: NDArray_N | float, dtype: npt.DTypeLike = np.float64, degrees: bool = False
) -> NDArray_3x3xN | NDArray_3x3:
    """Compute matrix for rotation of R3 vector through angle theta
    around the Y-axis. For frame rotation, use the transpose.

    Parameters
    ----------
    theta
        Angle to rotate.
    dtype
        Numpy datatype of the rotation matrix.
    degrees
        If `True`, use degrees. Else all angles are given in radians.

    Returns
    -------
        (3, 3) Rotation matrix, or (3, 3, n) tensor if theta is vector input.

    """
    if degrees:
        theta = np.radians(theta)
    size: tuple[int, ...]
    if isinstance(theta, np.ndarray) and theta.ndim > 0:
        size = (3, 3, len(theta))
    else:
        size = (3, 3)

    ca, sa = np.cos(theta), np.sin(theta)
    rot = np.zeros(size, dtype=dtype)
    rot[0, 0, ...] = ca
    rot[0, 2, ...] = sa
    rot[1, 1, ...] = 1
    rot[2, 0, ...] = -sa
    rot[2, 2, ...] = ca
    return rot


def rot_mat_z(
    theta: NDArray_N | float, dtype: npt.DTypeLike = np.float64, degrees: bool = False
) -> NDArray_3x3xN | NDArray_3x3:
    """Compute matrix for rotation of R3 vector through angle theta
    around the Z-axis. For frame rotation, use the transpose.

    Parameters
    ----------
    theta
        Angle to rotate.
    dtype
        Numpy datatype of the rotation matrix.
    degrees
        If `True`, use degrees. Else all angles are given in radians.

    Returns
    -------
        (3, 3) Rotation matrix, or (3, 3, n) tensor if theta is vector input.

    """
    if degrees:
        theta = np.radians(theta)
    size: tuple[int, ...]
    if isinstance(theta, np.ndarray) and theta.ndim > 0:
        size = (3, 3, len(theta))
    else:
        size = (3, 3)

    ca, sa = np.cos(theta), np.sin(theta)
    rot = np.zeros(size, dtype=dtype)
    rot[0, 0, ...] = ca
    rot[0, 1, ...] = -sa
    rot[1, 0, ...] = sa
    rot[1, 1, ...] = ca
    rot[2, 2, ...] = 1
    return rot


def rot_mat_2d(
    theta: float,
    dtype: npt.DTypeLike = np.float64,
    degrees: bool = False,
) -> NDArray_2x2:
    """Matrix for rotation of R2 vector in the plane through angle theta
    For frame rotation, use the transpose.

    Parameters
    ----------
    theta : float
        Angle to rotate.
    dtype : numpy.dtype
        Numpy datatype of the rotation matrix.
    degrees : bool
        If :code:`True`, use degrees. Else all angles are given in radians.

    Returns
    -------
    numpy.ndarray
        (2, 2) Rotation matrix.

    """
    if degrees:
        theta = np.radians(theta)

    ca, sa = np.cos(theta), np.sin(theta)
    return np.array([[ca, -sa], [sa, ca]], dtype=dtype)


def scale_mat_2d(
    x: float,
    y: float,
    dtype: npt.DTypeLike = np.float64,
) -> NDArray_2x2:
    """Matrix for 2d scaling.

    Parameters
    ----------
    x
        Scaling coefficient for first coordinate axis.
    y
        Scaling coefficient for second coordinate axis.

    Returns
    -------
        (2, 2) Scaling matrix.
    """
    M_scale = np.zeros((2, 2), dtype=dtype)
    M_scale[0, 0] = x
    M_scale[1, 1] = y
    return M_scale


def vec_to_vec(vec_in: NDArray_N, vec_out: NDArray_N) -> NDArray_NxN:
    """Get the rotation matrix that rotates `vec_in` to `vec_out` along the
    plane containing both. Uses quaternion calculations.
    """
    N = len(vec_in)
    if N != len(vec_out):
        raise ValueError("Input and output vectors must be same dimensionality.")
    assert N == 3, "Only implemented for 3d vectors"

    a = vec_in / np.linalg.norm(vec_in)
    b = vec_out / np.linalg.norm(vec_out)

    adotb = np.dot(a, b)
    axb = np.cross(a, b)
    axb_norm = np.linalg.norm(axb)

    # rotation in the plane frame of `vec_in` and `vec_out`
    G = np.zeros((N, N), dtype=vec_in.dtype)
    G[0, 0] = adotb
    G[0, 1] = -axb_norm
    G[1, 0] = axb_norm
    G[1, 1] = adotb
    G[2, 2] = 1

    # inverse of change of basis from standard orthonormal to `vec_in` and `vec_out` plane
    F = np.zeros((N, N), dtype=vec_in.dtype)
    F[:, 0] = a
    F[:, 1] = (b - adotb * a) / np.linalg.norm(b - adotb * a)
    F[:, 2] = axb

    # go to frame, rotation in plane, leave frame
    R = F @ G @ np.linalg.inv(F)

    return R
