from collections import OrderedDict
import numpy as np
from jplephem.spk import SPK

"""Mapping from body name to integer id's used by the kernels.

#todo: these can be expanded to get any body probably? and do more than astropy implementation does
"""
BODY_NAME_TO_KERNEL_SPEC = OrderedDict(
    [
        ("sun", [(0, 10)]),
        ("mercury", [(0, 1), (1, 199)]),
        ("venus", [(0, 2), (2, 299)]),
        ("earth-moon-barycenter", [(0, 3)]),
        ("earth", [(0, 3), (3, 399)]),
        ("moon", [(0, 3), (3, 301)]),
        ("mars", [(0, 4)]),
        ("jupiter", [(0, 5)]),
        ("saturn", [(0, 6)]),
        ("uranus", [(0, 7)]),
        ("neptune", [(0, 8)]),
        ("pluto", [(0, 9)]),
    ]
)


def get_solarsystem_body_states(bodies, epoch, kernel, units=None):
    """Open a kernel file and get the statates of the given bodies at epoch in ICRS.

    Note: All outputs from kernel computations are in the Barycentric (ICRS) "eternal" frame.
    """
    assert SPK is not None, "jplephem package needed to directly interact with kernels"
    states = {}

    kernel = SPK.open(kernel)

    epoch_ = epoch.tdb  # jplephem uses Barycentric Dynamical Time (TDB)
    jd1, jd2 = epoch_.jd1, epoch_.jd2

    for body in bodies:
        body_ = body.lower().strip()

        if body_ not in BODY_NAME_TO_KERNEL_SPEC:
            raise ValueError(f'Body name "{body}" not recognized')

        states[body] = np.zeros((6,), dtype=np.float64)

        # if there are multiple steps to go from states to
        # ICRS barycentric, iterate trough and combine
        for pair in BODY_NAME_TO_KERNEL_SPEC[body_]:
            spk = kernel[pair]
            if spk.data_type == 3:
                # Type 3 kernels contain both position and velocity.
                posvel = spk.compute(jd1, jd2).flatten()
            else:
                pos_, vel_ = spk.compute_and_differentiate(jd1, jd2)
                posvel = np.zeros((6,), dtype=np.float64)
                posvel[:3] = pos_
                posvel[3:] = vel_

            states[body] += posvel

        # units from kernels are usually in km and km/day
        if units is None:
            states[body] *= 1e3
            states[body][3:] /= 86400.0
        else:
            states[body] *= units[0]
            states[body][3:] /= units[1]

    return states
