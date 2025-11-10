# Copyright 2018 The Cirq Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import cmath

import numpy as np
import pytest

from cycles import (is_cptp, is_diagonal, is_hermitian, is_normal,
                    is_orthogonal, is_special_orthogonal, is_special_unitary,
                    is_unitary, matrix_commutes)


def random_density_matrix(dim: int, ) -> np.ndarray:
    """Returns a random density matrix distributed with Hilbert-Schmidt measure.

    Args:
        dim: The width and height of the matrix.

    Returns:
        The sampled density matrix.

    Reference:
        'Random Bures mixed states and the distribution of their purity'
        https://arxiv.org/abs/0909.5094
    """

    mat = np.random.randn(dim, dim) + 1j * np.random.randn(dim, dim)
    mat = mat @ mat.T.conj()
    return mat / np.trace(mat)


def random_unitary(dim: int) -> np.ndarray:
    """Returns a random unitary matrix distributed with Haar measure.

    Args:
        dim: The width and height of the matrix.

    Returns:
        The sampled unitary matrix.

    References:
        'How to generate random matrices from the classical compact groups'
        http://arxiv.org/abs/math-ph/0609050
    """

    z = np.random.randn(dim, dim) + 1j * np.random.randn(dim, dim)
    q, r = np.linalg.qr(z)
    d = np.diag(r)
    return q * (d / abs(d))


def test_is_diagonal():
    assert is_diagonal(np.empty((0, 0)))
    assert is_diagonal(np.empty((1, 0)))
    assert is_diagonal(np.empty((0, 1)))

    assert is_diagonal(np.array([[1]]))
    assert is_diagonal(np.array([[-1]]))
    assert is_diagonal(np.array([[5]]))
    assert is_diagonal(np.array([[3j]]))

    assert is_diagonal(np.array([[1, 0]]))
    assert is_diagonal(np.array([[1], [0]]))
    assert not is_diagonal(np.array([[1, 1]]))
    assert not is_diagonal(np.array([[1], [1]]))

    assert is_diagonal(np.array([[5j, 0], [0, 2]]))
    assert is_diagonal(np.array([[1, 0], [0, 1]]))
    assert not is_diagonal(np.array([[1, 0], [1, 1]]))
    assert not is_diagonal(np.array([[1, 1], [0, 1]]))
    assert not is_diagonal(np.array([[1, 1], [1, 1]]))
    assert not is_diagonal(np.array([[1, 0.1], [0.1, 1]]))

    assert is_diagonal(np.array([[1, 1e-11], [1e-10, 1]]))


def test_is_diagonal_tolerance():
    atol = 0.5

    # Pays attention to specified tolerance.
    assert is_diagonal(np.array([[1, 0], [-0.5, 1]]), atol=atol)
    assert not is_diagonal(np.array([[1, 0], [-0.6, 1]]), atol=atol)

    # Error isn't accumulated across entries.
    assert is_diagonal(np.array([[1, 0.5], [-0.5, 1]]), atol=atol)
    assert not is_diagonal(np.array([[1, 0.5], [-0.6, 1]]), atol=atol)


def test_is_hermitian():
    assert is_hermitian(np.empty((0, 0)))
    assert not is_hermitian(np.empty((1, 0)))
    assert not is_hermitian(np.empty((0, 1)))

    assert is_hermitian(np.array([[1]]))
    assert is_hermitian(np.array([[-1]]))
    assert is_hermitian(np.array([[5]]))
    assert not is_hermitian(np.array([[3j]]))

    assert not is_hermitian(np.array([[0, 0]]))
    assert not is_hermitian(np.array([[0], [0]]))

    assert not is_hermitian(np.array([[5j, 0], [0, 2]]))
    assert is_hermitian(np.array([[5, 0], [0, 2]]))
    assert is_hermitian(np.array([[1, 0], [0, 1]]))
    assert not is_hermitian(np.array([[1, 0], [1, 1]]))
    assert not is_hermitian(np.array([[1, 1], [0, 1]]))
    assert is_hermitian(np.array([[1, 1], [1, 1]]))
    assert is_hermitian(np.array([[1, 1j], [-1j, 1]]))
    assert is_hermitian(np.array([[1, 1j], [-1j, 1]]) * np.sqrt(0.5))
    assert not is_hermitian(np.array([[1, 1j], [1j, 1]]))
    assert not is_hermitian(np.array([[1, 0.1], [-0.1, 1]]))

    assert is_hermitian(np.array([[1, 1j + 1e-11], [-1j, 1 + 1j * 1e-9]]))


def test_is_hermitian_tolerance():
    atol = 0.5

    # Pays attention to specified tolerance.
    assert is_hermitian(np.array([[1, 0], [-0.5, 1]]), atol=atol)
    assert is_hermitian(np.array([[1, 0.25], [-0.25, 1]]), atol=atol)
    assert not is_hermitian(np.array([[1, 0], [-0.6, 1]]), atol=atol)
    assert not is_hermitian(np.array([[1, 0.25], [-0.35, 1]]), atol=atol)

    # Error isn't accumulated across entries.
    assert is_hermitian(np.array([[1, 0.5, 0.5], [0, 1, 0], [0, 0, 1]]),
                        atol=atol)
    assert not is_hermitian(np.array([[1, 0.5, 0.6], [0, 1, 0], [0, 0, 1]]),
                            atol=atol)
    assert not is_hermitian(np.array([[1, 0, 0.6], [0, 1, 0], [0, 0, 1]]),
                            atol=atol)


def test_is_unitary():
    assert is_unitary(np.empty((0, 0)))
    assert not is_unitary(np.empty((1, 0)))
    assert not is_unitary(np.empty((0, 1)))

    assert is_unitary(np.array([[1]]))
    assert is_unitary(np.array([[-1]]))
    assert is_unitary(np.array([[1j]]))
    assert not is_unitary(np.array([[5]]))
    assert not is_unitary(np.array([[3j]]))

    assert not is_unitary(np.array([[1, 0]]))
    assert not is_unitary(np.array([[1], [0]]))

    assert not is_unitary(np.array([[1, 0], [0, -2]]))
    assert is_unitary(np.array([[1, 0], [0, -1]]))
    assert is_unitary(np.array([[1j, 0], [0, 1]]))
    assert not is_unitary(np.array([[1, 0], [1, 1]]))
    assert not is_unitary(np.array([[1, 1], [0, 1]]))
    assert not is_unitary(np.array([[1, 1], [1, 1]]))
    assert not is_unitary(np.array([[1, -1], [1, 1]]))
    assert is_unitary(np.array([[1, -1], [1, 1]]) * np.sqrt(0.5))
    assert is_unitary(np.array([[1, 1j], [1j, 1]]) * np.sqrt(0.5))
    assert not is_unitary(np.array([[1, -1j], [1j, 1]]) * np.sqrt(0.5))

    assert is_unitary(
        np.array([[1, 1j + 1e-11], [1j, 1 + 1j * 1e-9]]) * np.sqrt(0.5))


def test_is_unitary_tolerance():
    atol = 0.5

    # Pays attention to specified tolerance.
    assert is_unitary(np.array([[1, 0], [-0.5, 1]]), atol=atol)
    assert not is_unitary(np.array([[1, 0], [-0.6, 1]]), atol=atol)

    # Error isn't accumulated across entries.
    assert is_unitary(np.array([[1.2, 0, 0], [0, 1.2, 0], [0, 0, 1.2]]),
                      atol=atol)
    assert not is_unitary(np.array([[1.2, 0, 0], [0, 1.3, 0], [0, 0, 1.2]]),
                          atol=atol)


def test_is_orthogonal():
    assert is_orthogonal(np.empty((0, 0)))
    assert not is_orthogonal(np.empty((1, 0)))
    assert not is_orthogonal(np.empty((0, 1)))

    assert is_orthogonal(np.array([[1]]))
    assert is_orthogonal(np.array([[-1]]))
    assert not is_orthogonal(np.array([[1j]]))
    assert not is_orthogonal(np.array([[5]]))
    assert not is_orthogonal(np.array([[3j]]))

    assert not is_orthogonal(np.array([[1, 0]]))
    assert not is_orthogonal(np.array([[1], [0]]))

    assert not is_orthogonal(np.array([[1, 0], [0, -2]]))
    assert is_orthogonal(np.array([[1, 0], [0, -1]]))
    assert not is_orthogonal(np.array([[1j, 0], [0, 1]]))
    assert not is_orthogonal(np.array([[1, 0], [1, 1]]))
    assert not is_orthogonal(np.array([[1, 1], [0, 1]]))
    assert not is_orthogonal(np.array([[1, 1], [1, 1]]))
    assert not is_orthogonal(np.array([[1, -1], [1, 1]]))
    assert is_orthogonal(np.array([[1, -1], [1, 1]]) * np.sqrt(0.5))
    assert not is_orthogonal(np.array([[1, 1j], [1j, 1]]) * np.sqrt(0.5))
    assert not is_orthogonal(np.array([[1, -1j], [1j, 1]]) * np.sqrt(0.5))

    assert is_orthogonal(np.array([[1, 1e-11], [0, 1 + 1e-11]]))


def test_is_orthogonal_tolerance():
    atol = 0.5

    # Pays attention to specified tolerance.
    assert is_orthogonal(np.array([[1, 0], [-0.5, 1]]), atol=atol)
    assert not is_orthogonal(np.array([[1, 0], [-0.6, 1]]), atol=atol)

    # Error isn't accumulated across entries.
    assert is_orthogonal(np.array([[1.2, 0, 0], [0, 1.2, 0], [0, 0, 1.2]]),
                         atol=atol)
    assert not is_orthogonal(np.array([[1.2, 0, 0], [0, 1.3, 0], [0, 0, 1.2]]),
                             atol=atol)


def test_is_special_orthogonal():
    assert is_special_orthogonal(np.empty((0, 0)))
    assert not is_special_orthogonal(np.empty((1, 0)))
    assert not is_special_orthogonal(np.empty((0, 1)))

    assert is_special_orthogonal(np.array([[1]]))
    assert not is_special_orthogonal(np.array([[-1]]))
    assert not is_special_orthogonal(np.array([[1j]]))
    assert not is_special_orthogonal(np.array([[5]]))
    assert not is_special_orthogonal(np.array([[3j]]))

    assert not is_special_orthogonal(np.array([[1, 0]]))
    assert not is_special_orthogonal(np.array([[1], [0]]))

    assert not is_special_orthogonal(np.array([[1, 0], [0, -2]]))
    assert not is_special_orthogonal(np.array([[1, 0], [0, -1]]))
    assert is_special_orthogonal(np.array([[-1, 0], [0, -1]]))
    assert not is_special_orthogonal(np.array([[1j, 0], [0, 1]]))
    assert not is_special_orthogonal(np.array([[1, 0], [1, 1]]))
    assert not is_special_orthogonal(np.array([[1, 1], [0, 1]]))
    assert not is_special_orthogonal(np.array([[1, 1], [1, 1]]))
    assert not is_special_orthogonal(np.array([[1, -1], [1, 1]]))
    assert is_special_orthogonal(np.array([[1, -1], [1, 1]]) * np.sqrt(0.5))
    assert not is_special_orthogonal(
        np.array([[1, 1], [1, -1]]) * np.sqrt(0.5))
    assert not is_special_orthogonal(
        np.array([[1, 1j], [1j, 1]]) * np.sqrt(0.5))
    assert not is_special_orthogonal(
        np.array([[1, -1j], [1j, 1]]) * np.sqrt(0.5))

    assert is_special_orthogonal(np.array([[1, 1e-11], [0, 1 + 1e-11]]))


def test_is_special_orthogonal_tolerance():
    atol = 0.5

    # Pays attention to specified tolerance.
    assert is_special_orthogonal(np.array([[1, 0], [-0.5, 1]]), atol=atol)
    assert not is_special_orthogonal(np.array([[1, 0], [-0.6, 1]]), atol=atol)

    # Error isn't accumulated across entries, except for determinant factors.
    assert is_special_orthogonal(np.array([[1.2, 0, 0], [0, 1.2, 0],
                                           [0, 0, 1 / 1.2]]),
                                 atol=atol)
    assert not is_special_orthogonal(
        np.array([[1.2, 0, 0], [0, 1.2, 0], [0, 0, 1.2]]), atol=atol)
    assert not is_special_orthogonal(
        np.array([[1.2, 0, 0], [0, 1.3, 0], [0, 0, 1 / 1.2]]), atol=atol)


def test_is_special_unitary():
    assert is_special_unitary(np.empty((0, 0)))
    assert not is_special_unitary(np.empty((1, 0)))
    assert not is_special_unitary(np.empty((0, 1)))

    assert is_special_unitary(np.array([[1]]))
    assert not is_special_unitary(np.array([[-1]]))
    assert not is_special_unitary(np.array([[5]]))
    assert not is_special_unitary(np.array([[3j]]))

    assert not is_special_unitary(np.array([[1, 0], [0, -2]]))
    assert not is_special_unitary(np.array([[1, 0], [0, -1]]))
    assert is_special_unitary(np.array([[-1, 0], [0, -1]]))
    assert not is_special_unitary(np.array([[1j, 0], [0, 1]]))
    assert is_special_unitary(np.array([[1j, 0], [0, -1j]]))
    assert not is_special_unitary(np.array([[1, 0], [1, 1]]))
    assert not is_special_unitary(np.array([[1, 1], [0, 1]]))
    assert not is_special_unitary(np.array([[1, 1], [1, 1]]))
    assert not is_special_unitary(np.array([[1, -1], [1, 1]]))
    assert is_special_unitary(np.array([[1, -1], [1, 1]]) * np.sqrt(0.5))
    assert is_special_unitary(np.array([[1, 1j], [1j, 1]]) * np.sqrt(0.5))
    assert not is_special_unitary(np.array([[1, -1j], [1j, 1]]) * np.sqrt(0.5))

    assert is_special_unitary(
        np.array([[1, 1j + 1e-11], [1j, 1 + 1j * 1e-9]]) * np.sqrt(0.5))


def test_is_special_unitary_tolerance():
    atol = 0.5

    # Pays attention to specified tolerance.
    assert is_special_unitary(np.array([[1, 0], [-0.5, 1]]), atol=atol)
    assert not is_special_unitary(np.array([[1, 0], [-0.6, 1]]), atol=atol)
    assert is_special_unitary(np.array([[1, 0], [0, 1]]) * cmath.exp(1j * 0.1),
                              atol=atol)
    assert not is_special_unitary(
        np.array([[1, 0], [0, 1]]) * cmath.exp(1j * 0.3), atol=atol)

    # Error isn't accumulated across entries, except for determinant factors.
    assert is_special_unitary(np.array([[1.2, 0, 0], [0, 1.2, 0],
                                        [0, 0, 1 / 1.2]]),
                              atol=atol)
    assert not is_special_unitary(
        np.array([[1.2, 0, 0], [0, 1.2, 0], [0, 0, 1.2]]), atol=atol)
    assert not is_special_unitary(
        np.array([[1.2, 0, 0], [0, 1.3, 0], [0, 0, 1 / 1.2]]), atol=atol)


def test_is_normal():
    assert is_normal(np.array([[1]]))
    assert is_normal(np.array([[3j]]))
    assert is_normal(random_density_matrix(4))
    assert is_normal(random_unitary(5))
    assert not is_normal(np.array([[0, 1], [0, 0]]))
    assert not is_normal(np.zeros((1, 0)))


def test_is_normal_tolerance():
    atol = 0.25

    # Pays attention to specified tolerance.
    assert is_normal(np.array([[0, 0.5], [0, 0]]), atol=atol)
    assert not is_normal(np.array([[0, 0.6], [0, 0]]), atol=atol)

    # Error isn't accumulated across entries.
    assert is_normal(np.array([[0, 0.5, 0], [0, 0, 0.5], [0, 0, 0]]),
                     atol=atol)
    assert not is_normal(np.array([[0, 0.5, 0], [0, 0, 0.6], [0, 0, 0]]),
                         atol=atol)


def test_is_cptp():
    rt2 = np.sqrt(0.5)
    # Amplitude damping with gamma=0.5.
    assert is_cptp(
        kraus_ops=[np.array([[1, 0], [0, rt2]]),
                   np.array([[0, rt2], [0, 0]])])
    # Depolarizing channel with p=0.75.
    assert is_cptp(kraus_ops=[
        np.array([[1, 0], [0, 1]]) * 0.5,
        np.array([[0, 1], [1, 0]]) * 0.5,
        np.array([[0, -1j], [1j, 0]]) * 0.5,
        np.array([[1, 0], [0, -1]]) * 0.5,
    ])

    assert not is_cptp(
        kraus_ops=[np.array([[1, 0], [0, 1]]),
                   np.array([[0, 1], [0, 0]])])
    assert not is_cptp(kraus_ops=[
        np.array([[1, 0], [0, 1]]),
        np.array([[0, 1], [1, 0]]),
        np.array([[0, -1j], [1j, 0]]),
        np.array([[1, 0], [0, -1]]),
    ])

    # Makes 4 2x2 kraus ops.
    one_qubit_u = random_unitary(8)
    one_qubit_kraus = np.reshape(one_qubit_u[:, :2], (-1, 2, 2))
    assert is_cptp(kraus_ops=one_qubit_kraus)

    # Makes 16 4x4 kraus ops.
    two_qubit_u = random_unitary(64)
    two_qubit_kraus = np.reshape(two_qubit_u[:, :4], (-1, 4, 4))
    assert is_cptp(kraus_ops=two_qubit_kraus)


def test_is_cptp_tolerance():
    rt2_ish = np.sqrt(0.5) - 0.01
    atol = 0.25
    # Moderately-incorrect amplitude damping with gamma=0.5.
    assert is_cptp(kraus_ops=[
        np.array([[1, 0], [0, rt2_ish]]),
        np.array([[0, rt2_ish], [0, 0]])
    ],
                   atol=atol)
    assert not is_cptp(kraus_ops=[
        np.array([[1, 0], [0, rt2_ish]]),
        np.array([[0, rt2_ish], [0, 0]])
    ],
                       atol=1e-8)


def test_commutes():
    assert matrix_commutes(np.empty((0, 0)), np.empty((0, 0)))
    assert not matrix_commutes(np.empty((1, 0)), np.empty((0, 1)))
    assert not matrix_commutes(np.empty((0, 1)), np.empty((1, 0)))
    assert not matrix_commutes(np.empty((1, 0)), np.empty((1, 0)))
    assert not matrix_commutes(np.empty((0, 1)), np.empty((0, 1)))

    assert matrix_commutes(np.array([[1]]), np.array([[2]]))
    assert matrix_commutes(np.array([[1]]), np.array([[0]]))

    x = np.array([[0, 1], [1, 0]])
    y = np.array([[0, -1j], [1j, 0]])
    z = np.array([[1, 0], [0, -1]])
    xx = np.kron(x, x)
    zz = np.kron(z, z)

    assert matrix_commutes(x, x)
    assert matrix_commutes(y, y)
    assert matrix_commutes(z, z)
    assert not matrix_commutes(x, y)
    assert not matrix_commutes(x, z)
    assert not matrix_commutes(y, z)

    assert matrix_commutes(xx, zz)
    assert matrix_commutes(xx, np.diag([1, -1, -1, 1 + 1e-9]))


def test_commutes_tolerance():
    atol = 0.5

    x = np.array([[0, 1], [1, 0]])
    z = np.array([[1, 0], [0, -1]])

    # Pays attention to specified tolerance.
    assert matrix_commutes(x, x + z * 0.1, atol=atol)
    assert not matrix_commutes(x, x + z * 0.5, atol=atol)
