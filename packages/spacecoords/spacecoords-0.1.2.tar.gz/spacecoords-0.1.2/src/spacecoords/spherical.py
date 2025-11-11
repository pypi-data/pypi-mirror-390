#!/usr/bin/env python

"""Functions related to spherical coordinate systems"""

import numpy as np
from numpy.typing import NDArray
from .types import NDArray_3, NDArray_3xN, NDArray_N

from . import linalg

CLOSE_TO_POLE_LIMIT = 1e-9**2
CLOSE_TO_POLE_LIMIT_rad = np.arctan(1 / np.sqrt(CLOSE_TO_POLE_LIMIT))


def arctime_to_degrees(minutes: NDArray | float, seconds: NDArray | float) -> NDArray | float:
    return (minutes + seconds / 60.0) / 60.0


def cart_to_sph(vec: NDArray_3 | NDArray_3xN, degrees: bool = False) -> NDArray_3 | NDArray_3xN:
    """Convert from Cartesian coordinates (east, north, up) to Spherical
    coordinates (azimuth, elevation, range) in a angle east of north and
    elevation fashion. Returns azimuth between [-pi, pi] and elevation between
    [-pi/2, pi/2].

    Parameters
    ----------
    vec
        (3, N) or (3,) vector of Cartesian coordinates (east, north, up).
        This argument is vectorized in the second array dimension.
    degrees
        If `True`, use degrees. Else all angles are given in radians.

    Returns
    -------
        (3, N) or (3, ) vector of Spherical coordinates
        (azimuth, elevation, range).

    Notes
    -----
    Azimuth close to pole convention
        Uses a :code:`CLOSE_TO_POLE_LIMIT` constant when transforming determine
        if the point is close to the pole and sets the azimuth by definition
        to 0 "at" the poles for consistency.

    """

    r2_ = vec[0, ...] ** 2 + vec[1, ...] ** 2

    sph = np.empty(vec.shape, dtype=vec.dtype)

    if len(vec.shape) == 1:
        if r2_ < CLOSE_TO_POLE_LIMIT:
            sph[0] = 0.0
            sph[1] = np.sign(vec[2]) * np.pi * 0.5
        else:
            sph[0] = np.arctan2(vec[0], vec[1])
            sph[1] = np.arctan(vec[2] / np.sqrt(r2_))
    else:
        inds_ = r2_ < CLOSE_TO_POLE_LIMIT
        not_inds_ = np.logical_not(inds_)

        sph[0, inds_] = 0.0
        sph[1, inds_] = np.sign(vec[2, inds_]) * np.pi * 0.5
        sph[0, not_inds_] = np.arctan2(vec[0, not_inds_], vec[1, not_inds_])
        sph[1, not_inds_] = np.arctan(vec[2, not_inds_] / np.sqrt(r2_[not_inds_]))

    sph[2, ...] = np.sqrt(r2_ + vec[2, ...] ** 2)
    if degrees:
        sph[:2, ...] = np.degrees(sph[:2, ...])

    return sph


def sph_to_cart(vec: NDArray_3 | NDArray_3xN, degrees: bool = False) -> NDArray_3 | NDArray_3xN:
    """Convert from spherical coordinates (azimuth, elevation, range) to
    Cartesian (east, north, up) in a angle east of north and elevation fashion.


    Parameters
    ----------
    vec
        (3, N) or (3,) vector of Cartesian Spherical
        (azimuth, elevation, range).
        This argument is vectorized in the second array dimension.
    degrees
        If :code:`True`, use degrees. Else all angles are given in radians.

    Returns
    -------
        (3, N) or (3, ) vector of Cartesian coordinates (east, north, up).

    """

    _az = vec[0, ...]
    _el = vec[1, ...]
    if degrees:
        _az, _el = np.radians(_az), np.radians(_el)
    cart = np.empty(vec.shape, dtype=vec.dtype)

    cart[0, ...] = vec[2, ...] * np.sin(_az) * np.cos(_el)
    cart[1, ...] = vec[2, ...] * np.cos(_az) * np.cos(_el)
    cart[2, ...] = vec[2, ...] * np.sin(_el)

    return cart


def az_el_to_sph(
    azimuth: NDArray_N | float,
    elevation: NDArray_N | float,
) -> NDArray_3xN | NDArray_3:
    """Convert input azimuth and elevation to spherical coordinates states,
    i.e a `shape=(3,n)` numpy array.
    """

    az_len = azimuth.size if isinstance(azimuth, np.ndarray) else None
    el_len = elevation.size if isinstance(elevation, np.ndarray) else None

    if el_len is not None and az_len is not None:
        assert el_len == az_len, f"azimuth {az_len} and elevation {el_len} sizes must agree"

    shape: tuple[int] | tuple[int, int]
    if az_len is not None:
        shape = (3, az_len)
    elif el_len is not None:
        shape = (3, el_len)
    else:
        shape = (3,)

    sph = np.empty(shape, dtype=np.float64)
    sph[0, ...] = azimuth
    sph[1, ...] = elevation
    sph[2, ...] = 1.0

    return sph


def az_el_point(
    azimuth: NDArray_N | float, elevation: NDArray_N | float, degrees: bool = False
) -> NDArray_3xN | NDArray_3:
    """Point beam towards azimuth and elevation coordinate.

    Parameters
    ----------
    azimuth : float
        Azimuth east of north of pointing direction.
    elevation : float
        Elevation from horizon of pointing direction.
    degrees : bool
        If :code:`True` all input/output angles are in degrees,
        else they are in radians. Defaults to instance
        settings :code:`self.radians`.

    """
    sph = az_el_to_sph(azimuth, elevation)
    return sph_to_cart(sph, degrees=degrees)


def az_el_vs_cart_angle(
    azimuth: NDArray_N | float,
    elevation: NDArray_N | float,
    cart: NDArray_3xN | NDArray_3,
    degrees: bool = False,
) -> NDArray_N | float:
    """Get angle between azimuth and elevation and pointing direction.

    Parameters
    ----------
    azimuth : float or NDArray
        Azimuth east of north of pointing direction.
    elevation : float or NDArray
        Elevation from horizon of pointing direction.
    degrees : bool
        If :code:`True` all input/output angles are in degrees,
        else they are in radians.

    Returns
    -------
    float or NDArray
        Angle between pointing and given direction.

    """
    sph = az_el_to_sph(azimuth, elevation)
    k = sph_to_cart(sph, degrees=degrees)
    return linalg.vector_angle(cart, k, degrees=degrees)
