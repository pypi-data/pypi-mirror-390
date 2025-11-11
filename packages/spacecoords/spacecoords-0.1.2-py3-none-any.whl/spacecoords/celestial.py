#!/usr/bin/env python

"""Coordinate frame transformations and related functions.
Main usage is the `convert` function that wraps Astropy frame transformations.
"""
from typing import Type, Any
from pathlib import Path
import numpy as np
from astropy.time import Time
import astropy.coordinates as coord
import astropy.units as units
import astropy.config as config

from .types import (
    NDArray_N,
    NDArray_3,
    NDArray_6,
    NDArray_3xN,
    NDArray_6xN,
    T,
)

"""List of astropy frames
"""
ASTROPY_FRAMES = {
    "TEME": "TEME",
    "ITRS": "ITRS",
    "ITRF": "ITRS",
    "ICRS": "ICRS",
    "ICRF": "ICRS",
    "GCRS": "GCRS",
    "GCRF": "GCRS",
    "HCRS": "HCRS",
    "HCRF": "HCRS",
    "HeliocentricMeanEcliptic".upper(): "HeliocentricMeanEcliptic",
    "GeocentricMeanEcliptic".upper(): "GeocentricMeanEcliptic",
    "HeliocentricTrueEcliptic".upper(): "HeliocentricTrueEcliptic",
    "GeocentricTrueEcliptic".upper(): "GeocentricTrueEcliptic",
    "BarycentricMeanEcliptic".upper(): "BarycentricMeanEcliptic",
    "BarycentricTrueEcliptic".upper(): "BarycentricTrueEcliptic",
    "SPICEJ2000": "ICRS",
}

"""List of frames that are not time-dependant
"""
ASTROPY_NOT_OBSTIME = [
    "ICRS",
    "BarycentricMeanEcliptic",
    "BarycentricTrueEcliptic",
]


def get_solarsystem_body_state(
    body: str,
    time: Time,
    kernel_dir: Path,
    ephemeris: str = "jpl",
) -> NDArray_6xN | NDArray_6:
    """

    This is to not have to remember how to do this astropy config stuff
    # https://docs.astropy.org/en/stable/api/astropy.coordinates.solar_system_ephemeris.html
    """
    with config.set_temp_cache(path=str(kernel_dir), delete=False):
        pos, vel = coord.get_body_barycentric_posvel(body, time, ephemeris=ephemeris)

    size = len(time)
    shape: tuple[int, ...] = (6, size) if size > 0 else (6,)
    state = np.empty(shape, dtype=np.float64)
    state[:3, ...] = pos.xyz.to(units.m).value
    state[3:, ...] = vel.d_xyz.to(units.m / units.s).value
    return state


def not_geocentric(frame: str) -> bool:
    """Check if the given frame name is one of the non-geocentric frames."""
    frame = frame.upper()
    return frame in ["ICRS", "ICRF", "HCRS", "HCRF"] or frame.startswith("Heliocentric".upper())


def is_geocentric(frame: str) -> bool:
    """Check if the frame name is a supported geocentric frame"""
    return not not_geocentric(frame)


def convert(
    t: NDArray_N,
    states: NDArray_6xN,
    in_frame: str,
    out_frame: str,
    frame_kwargs: dict[str, Any],
) -> NDArray_6xN:
    """Perform predefined coordinate transformations using Astropy.
    Always returns a copy of the array.

    Parameters
    ----------
    t
        Absolute time corresponding to the input states.
    states
        Size `(6,n)` matrix of states in SI units where rows 1-3
        are position and 4-6 are velocity.
    in_frame
        Name of the frame the input states are currently in.
    out_frame
        Name of the state to transform to.
    frame_kwargs
        Any arguments needed for the specific transform detailed by `astropy`
        in their documentation

    Returns
    -------
        Size `(6,n)` matrix of states in SI units where rows
        1-3 are position and 4-6 are velocity.

    """

    in_frame = in_frame.upper()
    out_frame = out_frame.upper()

    if in_frame == out_frame:
        return states.copy()

    if in_frame in ASTROPY_FRAMES:
        in_frame_ = ASTROPY_FRAMES[in_frame]
        in_frame_cls = getattr(coord, in_frame_)
    else:
        err_str = [
            f"In frame '{in_frame}' not recognized, ",
            "please check spelling or perform manual transformation",
        ]
        raise ValueError("".join(err_str))

    kw = {}
    kw.update(frame_kwargs)
    if in_frame_ not in ASTROPY_NOT_OBSTIME:
        kw["obstime"] = t

    astropy_states = _convert_to_astropy(states, in_frame_cls, kw)

    if out_frame in ASTROPY_FRAMES:
        out_frame_ = ASTROPY_FRAMES[out_frame]
        out_frame_cls = getattr(coord, out_frame_)
    else:
        err_str = [
            f"Out frame '{out_frame}' not recognized, ",
            "please check spelling or perform manual transformation",
        ]
        raise ValueError("".join(err_str))

    kw = {}
    kw.update(frame_kwargs)
    if out_frame_ not in ASTROPY_NOT_OBSTIME:
        kw["obstime"] = t

    out_states = astropy_states.transform_to(out_frame_cls(**kw))

    rets = states.copy()
    rets[:3, ...] = out_states.cartesian.xyz.to(units.m).value
    rets[3:, ...] = out_states.velocity.d_xyz.to(units.m / units.s).value

    return rets


def _convert_to_astropy(
    states: NDArray_6xN | NDArray_6,
    frame: Type[T],
    frame_kwargs: dict[str, Any],
) -> T:
    state_p = coord.CartesianRepresentation(states[:3, ...] * units.m)
    state_v = coord.CartesianDifferential(states[3:, ...] * units.m / units.s)
    astropy_states = frame(state_p.with_differentials(state_v), **frame_kwargs)  # type: ignore
    return astropy_states


def geodetic_to_ITRS(
    lat: NDArray_N | float,
    lon: NDArray_N | float,
    alt: NDArray_N | float,
    degrees: bool = True,
) -> NDArray_3xN | NDArray_3:
    """Use `astropy.coordinates.WGS84GeodeticRepresentation` to transform from WGS84 to ITRS."""
    ang_unit = units.deg if degrees else units.rad

    wgs_cord = coord.WGS84GeodeticRepresentation(
        lon=lon * ang_unit,
        lat=lat * ang_unit,
        height=alt * units.m,
    )
    itrs_cord = coord.ITRS(wgs_cord)

    if isinstance(lat, np.ndarray):
        size = lat.size
    else:
        size = 0

    shape: tuple[int, ...] = (6, size) if size > 0 else (6,)
    state = np.empty(shape, dtype=np.float64)
    state[:3, ...] = itrs_cord.cartesian.xyz.to(units.m).value
    state[3:, ...] = itrs_cord.velocity.d_xyz.to(units.m / units.s).value

    return state


def ITRS_to_geodetic(
    state: NDArray_3xN | NDArray_N,
    degrees: bool = True,
) -> tuple[NDArray_N | float, NDArray_N | float, NDArray_N | float]:
    """Use `astropy.coordinates.WGS84GeodeticRepresentation` to transform from ITRS to WGS84."""
    ang_unit = units.deg if degrees else units.rad

    itrs_cord = _convert_to_astropy(state, coord.ITRS, {})
    wgs_cord = coord.WGS84GeodeticRepresentation(itrs_cord)
    return (
        wgs_cord.lat.to(ang_unit).value,
        wgs_cord.lon.to(ang_unit).value,
        wgs_cord.height.to(units.m).value,
    )
