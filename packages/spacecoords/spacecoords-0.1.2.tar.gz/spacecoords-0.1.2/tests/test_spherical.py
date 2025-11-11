#!/usr/bin/env python

""" """

import unittest
import numpy as np
import numpy.testing as nt
from numpy import pi

from spacecoords import spherical


class TestCartSph(unittest.TestCase):

    def setUp(self):
        self.X = np.array(
            [
                [1, 0, 0],
                [0, 1, 0],
                [-1, 0, 0],
                [0, -1, 0],
                [0, 0, 1],
                [0, 0, -1],
                [1, 1, 1],
                [0, 1, 1],
            ],
            dtype=np.float64,
        )
        self.X = self.X.T
        self.Y = np.array(
            [
                [pi / 2, 0, 1],
                [0, 0, 1],
                [-pi / 2, 0, 1],
                [pi, 0, 1],
                [0, pi / 2, 1],
                [0, -pi / 2, 1],
                [pi / 4, np.arccos(np.sqrt(2 / 3)), np.sqrt(3)],
                [0, pi / 4, np.sqrt(2)],
            ],
            dtype=np.float64,
        )
        self.Y = self.Y.T
        self.num = self.X.shape[1]

        self.Yd = self.Y.copy()
        self.Yd[:2, :] = np.degrees(self.Yd[:2, :])

    def test_cart_to_sph(self):
        for ind in range(self.num):
            y = spherical.cart_to_sph(self.X[:, ind], degrees=False)
            print(f"T({self.X[:, ind]}) = {y} == {self.Y[:, ind]}")
            nt.assert_array_almost_equal(self.Y[:, ind], y)

    def test_sph_to_cart(self):
        for ind in range(self.num):
            x = spherical.sph_to_cart(self.Y[:, ind], degrees=False)
            print(f"T^-1({self.Y[:, ind]}) = {x} == {self.X[:, ind]}")
            nt.assert_array_almost_equal(self.X[:, ind], x)

    def test_cart_to_sph_vectorized(self):
        Y = spherical.cart_to_sph(self.X, degrees=False)
        nt.assert_array_almost_equal(self.Y, Y)

    def test_sph_to_cart_vectorized(self):
        X = spherical.sph_to_cart(self.Y, degrees=False)
        nt.assert_array_almost_equal(self.X, X)

    def test_degrees_keyword(self):
        Yd = spherical.cart_to_sph(self.X, degrees=True)
        nt.assert_array_almost_equal(self.Yd, Yd)

        X = spherical.sph_to_cart(self.Yd, degrees=True)
        nt.assert_array_almost_equal(self.X, X)

    def test_inverse_consistency(self):
        num = 100
        [az, el] = np.meshgrid(
            np.linspace(-pi, pi, num),
            np.linspace(-pi / 2, pi / 2, num),
        )
        az = az.flatten()
        el = el.flatten()

        # By convention, azimuth information is lost at pole
        az[np.abs(el) > spherical.CLOSE_TO_POLE_LIMIT_rad] = 0

        vec = np.ones((3,), dtype=np.float64)
        for ind in range(num**2):
            vec[0] = az[ind]
            vec[1] = el[ind]
            cart = spherical.sph_to_cart(vec, degrees=False)
            ang = spherical.cart_to_sph(cart, degrees=False)
            nt.assert_array_almost_equal(vec, ang)

    def test_inverse_edge_cases(self):
        Y = np.array(
            [
                [np.pi, 0, 1],
                [-np.pi, 0, 1],
            ],
            dtype=np.float64,
        ).T

        for ind in range(Y.shape[1]):
            X = spherical.sph_to_cart(Y[:, ind], degrees=False)
            Yp = spherical.cart_to_sph(X, degrees=False)
            nt.assert_array_almost_equal(Yp, Y[:, ind])
