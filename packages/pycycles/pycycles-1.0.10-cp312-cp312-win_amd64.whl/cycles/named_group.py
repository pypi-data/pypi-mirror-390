import numpy as np

from .cycles import Cycles
from .group import PermutationGroup


class SymmetricGroup(PermutationGroup):

    def __init__(self, N: int):
        if N < 2:
            super().__init__([])
        elif N == 2:
            super().__init__([Cycles((0, 1))])
        else:
            super().__init__([Cycles((0, 1)), Cycles(tuple(range(N)))])
        self.N = N

    def __repr__(self) -> str:
        return f"SymmetricGroup({self.N})"

    def __len__(self):
        return np.math.factorial(self.N)

    def __contains__(self, perm: Cycles):
        return set(perm.support) <= set(range(self.N))


class CyclicGroup(PermutationGroup):

    def __init__(self, N: int):
        if N < 2:
            super().__init__([])
        else:
            super().__init__([Cycles(tuple(range(N)))])
        self.N = N

    def __repr__(self) -> str:
        return f"CyclicGroup({self.N})"

    def __len__(self):
        return max(self.N, 1)


class DihedralGroup(PermutationGroup):

    def __init__(self, N: int):
        if N < 2:
            generators = []
        elif N == 2:
            generators = [Cycles((0, 1))]
        else:
            generators = [
                Cycles(tuple(range(N))),
                Cycles(*[(i + N % 2, N - 1 - i) for i in range(N // 2)])
            ]
        super().__init__(generators)
        self.N = N

    def __repr__(self) -> str:
        return f"DihedralGroup({self.N})"

    def __len__(self):
        if self.N == 1:
            return 1
        elif self.N == 2:
            return 2
        return max(2 * self.N, 1)


class AbelianGroup(PermutationGroup):

    def __init__(self, *n: int):
        self.n = tuple(sorted(n))
        generators = []
        start = 0
        for ni in self.n:
            if ni >= 2:
                generators.append(Cycles(tuple(range(start, start + ni))))
                start += ni
        super().__init__(generators)

    def __repr__(self) -> str:
        return f"AbelianGroup{self.n}"

    def __len__(self):
        return max(np.multiply.reduce(self.n), 1)


class AlternatingGroup(PermutationGroup):

    def __init__(self, N: int):
        if N <= 2:
            generators = []
        elif N == 3:
            generators = [Cycles((0, 1, 2))]
        else:
            generators = [
                Cycles((0, 1, 2)),
                Cycles(tuple(range(N))) if N %
                2 else Cycles(tuple(range(1, N)))
            ]
        super().__init__(generators)
        self.N = N

    def __repr__(self) -> str:
        return f"AlternatingGroup({self.N})"

    def __len__(self):
        return max(np.math.factorial(self.N) // 2, 1)

    def __contains__(self, perm: Cycles):
        return perm in SymmetricGroup(self.N) and perm.signature == 1
