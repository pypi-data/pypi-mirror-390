import numpy.typing as npt
import numpy as np


def latlon_to_hammer(
    lon: npt.NDArray | float,
    lat: npt.NDArray | float,
    ref_lon: npt.NDArray | float | None = None,
    degrees: bool = False,
) -> tuple[npt.NDArray | float, npt.NDArray | float]:
    """Project given Latitudes and Longitudes with the Hammer projection, can include a reference
    Longitude to align the data against.

    Typical usage is producing sun centered hammer projection
    of ecliptic radians."""
    if degrees:
        lon = np.radians(lon)
        lat = np.radians(lat)
        if ref_lon is not None:
            ref_lon = np.radians(ref_lon)

    if ref_lon is not None:
        # sun centered
        lambdas = np.mod(np.mod(-(lon - ref_lon - 1.5 * np.pi), 2 * np.pi) + 2 * np.pi, 2 * np.pi)
    else:
        lambdas = lon
    lambdas = np.array(lambdas)

    # Make longitude -pi:pi but make sure pi -> pi and not -pi
    inds = lambdas == np.pi
    lambdas = np.mod(lambdas + np.pi, 2 * np.pi) - np.pi
    if len(lambdas.shape) == 0:
        if inds:
            lambdas = np.pi
    else:
        lambdas[inds] = np.pi

    # hammer transform
    norm = np.sqrt(1 + np.cos(lat) * np.cos(lambdas * 0.5))
    hx = 2 * np.cos(lat) * np.sin(lambdas * 0.5) / norm
    hy = np.sin(lat) / norm

    return hx, hy
