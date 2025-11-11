#!/usr/bin/env python

""" """

import unittest
import numpy as np
import numpy.testing as nt

from spacecoords import frames


class ECEFRelatedFuncs(unittest.TestCase):

    def test_ned_to_ecef_pre_calc(self):
        dec = 3

        lat, lon = 0.0, 0.0
        x = np.array([0.0, 0.0, 0.0])
        g = frames.ned_to_ecef(lat, lon, x, degrees=True)
        nt.assert_array_almost_equal(g, x, decimal=dec)

        lat, lon = 0.0, 0.0
        x = np.array([0.0, 0.0, -100.0])
        g = frames.ned_to_ecef(lat, lon, x, degrees=True)
        g_ref = np.array([-x[2], 0.0, 0.0])
        nt.assert_array_almost_equal(g, g_ref, decimal=dec)

        x = np.array([0.0, 0.0, 100.0])
        g = frames.ned_to_ecef(lat, lon, x, degrees=True)
        g_ref = np.array([-x[2], 0.0, 0.0])
        nt.assert_array_almost_equal(g, g_ref, decimal=dec)

        lat, lon = 90.0, 0.0
        x = np.array([0.0, 0.0, 100.0])
        g = frames.ned_to_ecef(lat, lon, x, degrees=True)
        g_ref = np.array([0.0, 0.0, -x[2]])
        nt.assert_array_almost_equal(g, g_ref, decimal=dec)

        lat, lon = 45.0, 0.0
        x = np.array([0.0, 0.0, -np.sqrt(2.0)])
        g = frames.ned_to_ecef(lat, lon, x, degrees=True)
        g_ref = np.array([1.0, 0.0, 1.0])
        nt.assert_array_almost_equal(g, g_ref, decimal=dec)

    def test_ecef_to_enu_pre_calc(self):
        dec = 3

        lat, lon = 0.0, 0.0
        x_ref = np.array([0.0, 0.0, 100.0])  # enu
        ecef = np.array([100.0, 0.0, 0.0])
        x = frames.ecef_to_enu(lat, lon, ecef, degrees=True)
        nt.assert_array_almost_equal(x_ref, x, decimal=dec)

        x_ref = np.array([0.0, 100.0, 0.0])
        ecef = np.array([0.0, 0.0, 100.0])
        x = frames.ecef_to_enu(lat, lon, ecef, degrees=True)
        nt.assert_array_almost_equal(x_ref, x, decimal=dec)

        x_ref = np.array([100.0, 0.0, 0.0])
        ecef = np.array([0.0, 100.0, 0.0])
        x = frames.ecef_to_enu(lat, lon, ecef, degrees=True)
        nt.assert_array_almost_equal(x_ref, x, decimal=dec)

        lat, lon = 0.0, 180.0
        x_ref = np.array([0.0, 0.0, 100.0])
        ecef = np.array([-100.0, 0.0, 0.0])
        x = frames.ecef_to_enu(lat, lon, ecef, degrees=True)
        nt.assert_array_almost_equal(x_ref, x, decimal=dec)

        lat, lon = 90.0, 0.0
        x_ref = np.array([0.0, 0.0, 100.0])
        ecef = np.array([0.0, 0.0, 100.0])
        x = frames.ecef_to_enu(lat, lon, ecef, degrees=True)
        nt.assert_array_almost_equal(x_ref, x, decimal=dec)

        lat, lon = 45.0, 0.0
        x_ref = np.array([0.0, 0.0, np.sqrt(200.0)])
        ecef = np.array([10.0, 0.0, 10.0])
        x = frames.ecef_to_enu(lat, lon, ecef, degrees=True)
        nt.assert_array_almost_equal(x_ref, x, decimal=dec)

    def test_enu_to_ecef_to_enu(self):
        dec = 3

        lat, lon = 0.0, 0.0
        x = np.array([0.0, 0.0, 0.0])
        g = frames.enu_to_ecef(lat, lon, x, degrees=True)
        x_ref = frames.ecef_to_enu(lat, lon, g, degrees=True)
        nt.assert_array_almost_equal(x_ref, x, decimal=dec)

        lat, lon = 0.0, 0.0
        x = np.array([0.0, 0.0, -100.0])
        g = frames.enu_to_ecef(lat, lon, x, degrees=True)
        x_ref = frames.ecef_to_enu(lat, lon, g, degrees=True)
        nt.assert_array_almost_equal(x_ref, x, decimal=dec)

        x = np.array([0.0, 0.0, 100.0])
        g = frames.enu_to_ecef(lat, lon, x, degrees=True)
        x_ref = frames.ecef_to_enu(lat, lon, g, degrees=True)
        nt.assert_array_almost_equal(x_ref, x, decimal=dec)

        lat, lon = 90.0, 0.0
        x = np.array([0.0, 0.0, 100.0])
        g = frames.enu_to_ecef(lat, lon, x, degrees=True)
        x_ref = frames.ecef_to_enu(lat, lon, g, degrees=True)
        nt.assert_array_almost_equal(x_ref, x, decimal=dec)

        lat, lon = 45.0, 0.0
        x = np.array([0.0, 0.0, -np.sqrt(2.0)])
        g = frames.enu_to_ecef(lat, lon, x, degrees=True)
        x_ref = frames.ecef_to_enu(lat, lon, g, degrees=True)
        nt.assert_array_almost_equal(x_ref, x, decimal=dec)

    def test_enu_to_ecef_pre_calc(self):
        raise NotImplementedError()

    def test_azel_to_ecef_pre_calc(self):
        raise NotImplementedError()

    def test_ecef_to_enu_to_ecef(self):
        raise NotImplementedError()
