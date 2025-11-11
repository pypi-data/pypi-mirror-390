import unittest
import numpy as np
import numpy.testing as nt

from spacecoords import celestial
from spacecoords import constants


class TestFrames(unittest.TestCase):

    def test_geodetic_to_ITRS(self):
        dec = 3
        x = celestial.geodetic_to_ITRS(90.0, 0.0, 0.0, degrees=True)
        nt.assert_almost_equal(x[2], constants.WGS84.b, decimal=dec)

        x = celestial.geodetic_to_ITRS(-90.0, 0.0, 0.0, degrees=True)
        nt.assert_almost_equal(x[2], -constants.WGS84.b, decimal=dec)

        x = celestial.geodetic_to_ITRS(0.0, 0.0, 0.0, degrees=True)
        nt.assert_almost_equal(x[0], constants.WGS84.a, decimal=dec)

        x = celestial.geodetic_to_ITRS(0.0, 90.0, 0.0, degrees=True)
        nt.assert_almost_equal(x[1], constants.WGS84.a, decimal=dec)

        x = celestial.geodetic_to_ITRS(90.0, 0.0, 100.0, degrees=True)
        nt.assert_almost_equal(x[2], constants.WGS84.b + 100.0, decimal=dec)

    def test_ecef_geo_inverse(self):
        dec = 3
        y = np.array((90.0, 0.0, 0.0))
        x = celestial.geodetic_to_ITRS(y[0], y[1], y[2])
        y_ref = celestial.ITRS_to_geodetic(x[0], x[1], x[2])
        nt.assert_array_almost_equal(y, y_ref, decimal=dec)

        y = np.array((-90.0, 0.0, 0.0))
        x = celestial.geodetic_to_ITRS(y[0], y[1], y[2])
        y_ref = celestial.ITRS_to_geodetic(x[0], x[1], x[2])
        nt.assert_array_almost_equal(y, y_ref, decimal=dec)

        y = np.array((0.0, 0.0, 0.0))
        x = celestial.geodetic_to_ITRS(y[0], y[1], y[2])
        y_ref = celestial.ITRS_to_geodetic(x[0], x[1], x[2])
        nt.assert_array_almost_equal(y, y_ref, decimal=dec)

        y = np.array((0.0, 90.0, 0.0))
        x = celestial.geodetic_to_ITRS(y[0], y[1], y[2])
        y_ref = celestial.ITRS_to_geodetic(x[0], x[1], x[2])
        nt.assert_array_almost_equal(y, y_ref, decimal=dec)

        y = np.array((90.0, 0.0, 100.0))
        x = celestial.geodetic_to_ITRS(y[0], y[1], y[2])
        y_ref = celestial.ITRS_to_geodetic(x[0], x[1], x[2])
        nt.assert_array_almost_equal(y, y_ref, decimal=dec)

    def test_ITRS_to_geodetic(self):
        dec = 3
        x = celestial.ITRS_to_geodetic(0.0, 0.0, constants.WGS84.b)
        y = np.array((90.0, 0.0, 0.0))
        nt.assert_array_almost_equal(x, y, decimal=dec)

        x = celestial.ITRS_to_geodetic(0.0, 0.0, -constants.WGS84.b)
        y = np.array((-90.0, 0.0, 0.0))
        nt.assert_array_almost_equal(x, y, decimal=dec)

        x = celestial.ITRS_to_geodetic(constants.WGS84.a, 0.0, 0.0)
        y = np.array((0.0, 0.0, 0.0))
        nt.assert_array_almost_equal(x, y, decimal=dec)

        x = celestial.ITRS_to_geodetic(0.0, constants.WGS84.a, 0.0)
        y = np.array((0.0, 90.0, 0.0))
        nt.assert_array_almost_equal(x, y, decimal=dec)

        x = celestial.ITRS_to_geodetic(0.0, 0.0, constants.WGS84.b + 100.0)
        y = np.array((90.0, 0.0, 100.0))
        nt.assert_array_almost_equal(x, y, decimal=dec)
