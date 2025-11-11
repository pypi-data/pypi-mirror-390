#!/usr/bin/env python

"""Constants useful for different coordinate systems"""


G: float = 6.67430e-11
"""Newtonian constant of gravitation (m^3 kg^-1 s^-2), CODATA Recommended Values of the Fundamental
Physical Constants 2022.
"""


class WGS84:
    """World Geodetic System 1984 constants."""

    a: float = 6378.137 * 1e3
    """float: semi-major axis parameter in meters of the World Geodetic System 1984 (WGS84)
    """

    b: float = 6356.7523142 * 1e3
    """float: semi-minor axis parameter in meters of the World Geodetic System 1984 (WGS84)
    """

    esq: float = 6.69437999014 * 0.001
    """float: `esq` parameter in meters of the World Geodetic System 1984 (WGS84)
    """

    e1sq: float = 6.73949674228 * 0.001
    """float: `e1sq` parameter in meters of the World Geodetic System 1984 (WGS84)
    """

    f: float = 1 / 298.257223563
    """float: `f` parameter of the World Geodetic System 1984 (WGS84)
    """


R_earth: float = 6371.0088e3
"""float: Radius of the Earth using the International
Union of Geodesy and Geophysics (IUGG) definition
"""


class WGS72:
    """World Geodetic System 1972 constants."""

    MU_earth: float = 398600.8 * 1e9
    """float: Standard gravitational parameter of the Earth using the WGS72 convention.
    """

    M_earth: float = MU_earth / G
    """float: Mass of the Earth using the WGS72 convention.
    """
