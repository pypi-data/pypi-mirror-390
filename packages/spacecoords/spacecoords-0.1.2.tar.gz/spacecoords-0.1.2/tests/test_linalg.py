#!/usr/bin/env python

""" """

import unittest
import numpy as np
import numpy.testing as nt
from numpy import pi

from spacecoords import linalg


class TestAngles(unittest.TestCase):

    def setUp(self):
        self.A = np.array(
            [
                [1, 0, 0],
                [1, 0, 0],
                [0, 1, 0],
                [1, 0, 0],
                [0, 0, 1],
                [1, 1, 0],
                [1, 1, 0],
            ],
            dtype=np.float64,
        )
        self.A = self.A.T
        self.B = np.array(
            [
                [1, 0, 0],
                [0, 1, 0],
                [1, 0, 0],
                [-1, 0, 0],
                [0, 0, -1],
                [1, 0, 0],
                [0, 1, 0],
            ],
            dtype=np.float64,
        )
        self.B = self.B.T
        self.theta = np.array(
            [
                0,
                pi / 2,
                pi / 2,
                pi,
                pi,
                pi / 4,
                pi / 4,
            ],
            dtype=np.float64,
        )
        self.p = np.array([0, 1, 0], dtype=np.float64)
        self.P = np.array(
            [
                [1, 0, 0],
                [1, 1, 0],
                [1, 0, 0],
                [1, 1, 0],
            ],
            dtype=np.float64,
        ).T
        self.phi = np.array(
            [
                pi / 2,
                pi / 4,
                pi / 2,
                pi / 4,
            ],
            dtype=np.float64,
        )

    def test_vector_angle(self):
        for ind in range(len(self.theta)):
            th = linalg.vector_angle(
                self.A[:, ind],
                self.B[:, ind],
                degrees=False,
            )
            nt.assert_almost_equal(th, self.theta[ind])

    def test_vector_angle(self):
        x = np.array([1, 0, 0])
        y = np.array([1, 1, 0])
        theta = linalg.vector_angle(x, y, degrees=True)
        self.assertAlmostEqual(theta, 45.0)

        y = np.array([0, 1, 0])
        theta = linalg.vector_angle(x, y, degrees=True)
        self.assertAlmostEqual(theta, 90.0)

        theta = linalg.vector_angle(x, x, degrees=True)
        self.assertAlmostEqual(theta, 0.0)

        theta = linalg.vector_angle(x, -x, degrees=True)
        self.assertAlmostEqual(theta, 180.0)

        xx = np.array([0.11300039, -0.85537661, 0.50553118])
        theta = linalg.vector_angle(xx, xx, degrees=True)
        self.assertAlmostEqual(theta, 0.0)

    def test_vector_angle_first_vectorized(self):
        th = linalg.vector_angle(self.P, self.p, degrees=False)
        nt.assert_array_almost_equal(th, self.phi)

    def test_vector_angle_second_vectorized(self):
        th = linalg.vector_angle(self.p, self.P, degrees=False)
        nt.assert_array_almost_equal(th, self.phi)

    def test_vector_angle_both_vectorized(self):
        th = linalg.vector_angle(self.A, self.B, degrees=False)
        nt.assert_array_almost_equal(th, self.theta)


class TestRotations(unittest.TestCase):

    def setUp(self):
        self.basis = np.eye(3, dtype=np.float64)
        self.basis_x_90deg = np.array(
            [
                [1, 0, 0],
                [0, 0, -1],
                [0, 1, 0],
            ],
            dtype=np.float64,
        )
        self.basis_y_90deg = np.array(
            [
                [0, 0, 1],
                [0, 1, 0],
                [-1, 0, 0],
            ],
            dtype=np.float64,
        )
        self.basis_z_90deg = np.array(
            [
                [0, -1, 0],
                [1, 0, 0],
                [0, 0, 1],
            ],
            dtype=np.float64,
        )

    def test_rot_mat_x(self):
        R = linalg.rot_mat_x(pi / 2)
        r_basis = R @ self.basis
        nt.assert_array_almost_equal(r_basis, self.basis_x_90deg)
        basis = R.T @ r_basis
        nt.assert_array_almost_equal(basis, self.basis)

    def test_rot_mat_y(self):
        R = linalg.rot_mat_y(pi / 2)
        r_basis = R @ self.basis
        nt.assert_array_almost_equal(r_basis, self.basis_y_90deg)
        basis = R.T @ r_basis
        nt.assert_array_almost_equal(basis, self.basis)

    def test_rot_mat_z(self):
        R = linalg.rot_mat_z(pi / 2)
        r_basis = R @ self.basis
        nt.assert_array_almost_equal(r_basis, self.basis_z_90deg)
        basis = R.T @ r_basis
        nt.assert_array_almost_equal(basis, self.basis)

    def test_rot_mat_x_vector(self):
        th = np.full((3,), np.pi / 2)
        R = linalg.rot_mat_x(th)
        r_basis = np.einsum("ijk,jk->ik", R, self.basis)
        nt.assert_array_almost_equal(r_basis, self.basis_x_90deg)
        basis = np.einsum("ijk,jk->ik", np.einsum("ijk->jik", R), r_basis)
        nt.assert_array_almost_equal(basis, self.basis)

    def test_rot_mat_y_vector(self):
        th = np.full((3,), np.pi / 2)
        R = linalg.rot_mat_y(th)
        r_basis = np.einsum("ijk,jk->ik", R, self.basis)
        nt.assert_array_almost_equal(r_basis, self.basis_y_90deg)
        basis = np.einsum("ijk,jk->ik", np.einsum("ijk->jik", R), r_basis)
        nt.assert_array_almost_equal(basis, self.basis)

    def test_rot_mat_z_vector(self):
        th = np.full((3,), np.pi / 2)
        R = linalg.rot_mat_z(th)
        r_basis = np.einsum("ijk,jk->ik", R, self.basis)
        nt.assert_array_almost_equal(r_basis, self.basis_z_90deg)
        basis = np.einsum("ijk,jk->ik", np.einsum("ijk->jik", R), r_basis)
        nt.assert_array_almost_equal(basis, self.basis)


class TestScale(unittest.TestCase):

    def test_scale_mat_2d_x(self):
        a = np.array([1, 0], dtype=np.float64)
        x_scale = 3
        b = a.copy()
        b[0] *= x_scale
        M = linalg.scale_mat_2d(x_scale, 1)

        bp = M @ a
        nt.assert_array_almost_equal(bp, b)

    def test_scale_mat_2d_y(self):
        a = np.array([0, 1], dtype=np.float64)
        y_scale = 3
        b = a.copy()
        b[1] *= y_scale
        M = linalg.scale_mat_2d(1, y_scale)

        bp = M @ a
        nt.assert_array_almost_equal(bp, b)

    def test_scale_mat_2d_xy(self):
        a = np.array([1, 1], dtype=np.float64)
        x_scale = 3
        y_scale = 2
        b = a.copy()
        b[0] *= x_scale
        b[1] *= y_scale
        M = linalg.scale_mat_2d(x_scale, y_scale)

        bp = M @ a
        nt.assert_array_almost_equal(bp, b)
