#!/usr/bin/env python

"""Transforms between common coordinate frames without any additional dependencies"""

import numpy as np
from .spherical import sph_to_cart
from .types import (
    NDArray_N,
    NDArray_3,
    NDArray_3xN,
)


def ned_to_ecef(
    lat: float,
    lon: float,
    ned: NDArray_3xN | NDArray_3,
    degrees: bool = False,
) -> NDArray_3xN | NDArray_3:
    """NED (north/east/down) using geocentric zenith to ECEF coordinate system
    conversion, not including translation.

    Parameters
    ----------
    lat
        Latitude of the origin in geocentric spherical coordinates
    lon
        Longitude of the origin in geocentric spherical coordinates
    ned
        (3,n) input matrix of positions in the NED-convention.
    degrees
        If `True`, use degrees. Else all angles are given in radians.

    Returns
    -------
        (3,) or (3,n) array x,y and z coordinates in ECEF.
    """
    enu = np.empty(ned.size, dtype=ned.dtype)
    enu[0, ...] = ned[1, ...]
    enu[1, ...] = ned[0, ...]
    enu[2, ...] = -ned[2, ...]
    return enu_to_ecef(lat, lon, enu, degrees=degrees)


def azel_to_ecef(
    lat: float,
    lon: float,
    az: NDArray_N | float,
    el: NDArray_N | float,
    degrees: bool = False,
) -> NDArray_3xN | NDArray_3:
    """Radar pointing (az,el) using geocentric zenith to unit vector in
    ECEF, not including translation.

    Parameters
    ----------
    lat
        Latitude of the origin in geocentric spherical coordinates
    lon
        Longitude of the origin in geocentric spherical coordinates
    az
        Azimuth of the pointing direction
    el
        Elevation of the pointing direction
    degrees
        If `True`, use degrees. Else all angles are given in radians.

    Returns
    -------
        (3,) or (3,n) array x,y and z coordinates in ECEF.
    """
    shape: tuple[int, ...] = (3,)

    if isinstance(az, np.ndarray):
        if len(az.shape) == 0:
            az = float(az)
        elif len(az) > 1:
            shape = (3, len(az))
            az = az.flatten()
        else:
            az = az[0]

    if isinstance(el, np.ndarray):
        if len(el.shape) == 0:
            el = float(el)
        elif len(el) > 1:
            shape = (3, len(el))
            el = el.flatten()
        else:
            el = el[0]

    sph = np.empty(shape, dtype=np.float64)
    sph[0, ...] = az
    sph[1, ...] = el
    sph[2, ...] = 1.0
    enu = sph_to_cart(sph, degrees=degrees)
    return enu_to_ecef(lat, lon, enu, degrees=degrees)


def enu_to_ecef(
    lat: float,
    lon: float,
    enu: NDArray_3 | NDArray_3xN,
    degrees: bool = False,
) -> NDArray_3xN | NDArray_3:
    """Rotate ENU (east/north/up) using geocentric zenith to ECEF coordinate system,
    not including translation.

    Parameters
    ----------
    lat
        Latitude of the origin in geocentric spherical coordinates
    lon
        Longitude of the origin in geocentric spherical coordinates
    enu
        (3,n) input matrix of positions in the ENU-convention.
    degrees
        If `True`, use degrees. Else all angles are given in radians.

    Returns
    -------
        (3,) or (3,n) array x,y and z coordinates in ECEF.
    """
    if degrees:
        lat, lon = np.radians(lat), np.radians(lon)

    mx = np.array(
        [
            [-np.sin(lon), -np.sin(lat) * np.cos(lon), np.cos(lat) * np.cos(lon)],
            [np.cos(lon), -np.sin(lat) * np.sin(lon), np.cos(lat) * np.sin(lon)],
            [0, np.cos(lat), np.sin(lat)],
        ]
    )

    ecef = np.dot(mx, enu)
    return ecef


def ecef_to_enu(
    lat: float,
    lon: float,
    ecef: NDArray_3 | NDArray_3xN,
    degrees: bool = False,
) -> NDArray_3xN | NDArray_3:
    """Rotate ECEF coordinate system to local ENU (east,north,up) using geocentric
    zenith, not including translation.

    Parameters
    ----------
    lat
        Latitude of the origin in geocentric spherical coordinates
    lon
        Longitude of the origin in geocentric spherical coordinates
    ecef
        (3,) or (3,n) array x,y and z coordinates in ECEF.
    degrees
        If `True`, use degrees. Else all angles are given in radians.

    Returns
    -------
        (3,) or (3,n) array x, y and z coordinates in ENU.
    """
    if degrees:
        lat, lon = np.radians(lat), np.radians(lon)

    mx = np.array(
        [
            [-np.sin(lon), -np.sin(lat) * np.cos(lon), np.cos(lat) * np.cos(lon)],
            [np.cos(lon), -np.sin(lat) * np.sin(lon), np.cos(lat) * np.sin(lon)],
            [0, np.cos(lat), np.sin(lat)],
        ]
    )
    enu = np.dot(np.linalg.inv(mx), ecef)
    return enu
