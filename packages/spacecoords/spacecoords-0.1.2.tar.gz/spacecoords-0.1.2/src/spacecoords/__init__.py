"""General purpose convenience functions for different coordinate systems and linear algebra
functions
"""

from types import ModuleType
import importlib.util
from .version import __version__

from . import linalg
from . import spherical
from . import constants
from . import projection


def _make_missing_module(name: str, dep: str):
    class _MissingModule(ModuleType):
        def __getattr__(self, key):
            raise ImportError(
                f"The optional dependency `{dep}` for is missing.\n"
                f"Install it with `pip install spacecoords[all]` or `pip install {dep}`."
            )

    return _MissingModule(name)


# Optional modules
if importlib.util.find_spec("astropy") is not None:
    from . import celestial
else:
    astropy = _make_missing_module("celestial", "astropy")

if importlib.util.find_spec("jplephem") is not None:
    from . import spk_basic
else:
    naif_ephemeris = _make_missing_module("spk_basic", "jplephem")

if importlib.util.find_spec("spice") is not None:
    from . import spice
else:
    naif_spice = _make_missing_module("spice", "spiceypy")

if importlib.util.find_spec("requests") is not None:
    from . import download
else:
    download = _make_missing_module("download", "requests")
