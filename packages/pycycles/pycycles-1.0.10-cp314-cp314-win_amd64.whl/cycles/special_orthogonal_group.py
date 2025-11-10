import math
from functools import cached_property
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.linalg import expm, logm


def _triu_indices(n, i):
    """
    Return the indices of the i-th upper triangular element of an n x n matrix.
    Different order from np.triu_indices.
    """
    l = (math.isqrt(1 + 8 * i) - 1) // 2 + 1
    k = i - l * (l - 1) // 2

    return k, l


class SO():
    """
    Special orthogonal group
    """

    def __init__(self, n: int):
        if n <= 0:
            raise ValueError("n must be positive")
        self.n = n

    @cached_property
    def generators(self):
        return [self[i] for i in range(self.n * (self.n - 1) // 2)]

    @property
    def dim(self):
        return self.n

    @property
    def order(self):
        return self.n * (self.n - 1) // 2

    def __repr__(self):
        return f"SO({self.n})"

    def __getitem__(self, i: int):
        if not 0 <= i < self.n * (self.n - 1) // 2:
            raise IndexError(
                f"i must be in [0, {self.n * (self.n - 1) // 2 - 1}]")
        mat = np.zeros((self.n, self.n), dtype=np.int8)
        k, l = _triu_indices(self.n, i)

        if (k + l) % 2:
            mat[k, l] = -1
            mat[l, k] = 1
        else:
            mat[k, l] = 1
            mat[l, k] = -1

        return mat

    def __contains__(self, mat: NDArray) -> bool:
        if mat.shape != (self.n, self.n):
            return False
        if not np.allclose(mat @ mat.T, np.eye(self.n)):
            return False
        if not np.allclose(np.linalg.det(mat), 1):
            return False
        return True

    def __call__(self, *angles) -> NDArray:
        if len(angles) != self.order:
            raise ValueError(
                f"SO({self.n}) takes {self.order} angles, but {len(angles)} given"
            )
        return expm(sum(a * g for a, g in zip(angles, self.generators)))

    def angles(self, mat: NDArray) -> NDArray:
        """
        mat = expm(sum(angles[i]*self[i]))
        """
        assert mat in self

        A = logm(mat)
        angles = []

        for i in range(self.order):
            k, l = _triu_indices(self.n, i)
            if (k + l) % 2:
                angles.append(A[l, k])
            else:
                angles.append(A[k, l])

        return np.array(angles)
    
    def random(self):
        vec = np.random.randn(self.order)
        vec = vec / np.linalg.norm(vec)
        radius = np.random.rand()**(1.0 / self.order)
        angles = 2 * np.pi * radius * vec
        return self(angles)
