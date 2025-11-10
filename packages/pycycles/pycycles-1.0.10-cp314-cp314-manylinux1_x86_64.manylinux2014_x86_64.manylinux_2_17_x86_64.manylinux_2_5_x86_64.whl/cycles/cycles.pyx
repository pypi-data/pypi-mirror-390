import functools
import math
from itertools import repeat
from typing import Dict, Literal, TypeVar

import numpy as np


@functools.total_ordering
class Cycles():

    __slots__ = ('_cycles', '_support', '_mapping', '_expr', '_order')

    def __init__(self, *cycles):
        self._mapping = {}
        self._expr: tuple[Cycles | Literal['-'], Cycles] | list[Cycles] = []
        self._order = None
        if len(cycles) == 0:
            self._cycles = ()
            self._support = ()
            return

        if not isinstance(cycles[0], (list, tuple)):
            cycles = (cycles, )

        support = set()
        ret = []
        for cycle in cycles:
            if len(cycle) <= 1:
                continue
            support.update(cycle)
            i = cycle.index(min(cycle))
            cycle = cycle[i:] + cycle[:i]
            ret.append(tuple(cycle))
            for i in range(len(cycle) - 1):
                self._mapping[cycle[i]] = cycle[i + 1]
            self._mapping[cycle[-1]] = cycle[0]
        self._cycles = tuple(sorted(ret))
        self._support = tuple(sorted(support))

    def __hash__(self):
        return hash(self._cycles)

    def is_identity(self):
        return len(self._cycles) == 0

    def __eq__(self, value: 'Cycles') -> bool:
        return self._cycles == value._cycles

    def __lt__(self, value: 'Cycles') -> bool:
        return self._cycles < value._cycles

    def __mul__(self, other: 'Cycles') -> 'Cycles':
        """Returns the product of two cycles.

        The product of permutations a, b is understood to be the permutation
        resulting from applying a, then b.
        """
        support = sorted(set(self.support + other.support), reverse=True)
        mapping = {
            a: b
            for a, b in zip(support, other.replace(self.replace(support)))
            if a != b
        }
        c = Cycles._from_sorted_mapping(mapping)
        c._expr = (self, other)
        return c

    def __rmul__(self, other: 'Cycles') -> 'Cycles':
        return other.__mul__(self)

    @staticmethod
    def _from_sorted_mapping(mapping: Dict[int, int]) -> 'Cycles':
        c = Cycles()
        if not mapping:
            return c

        c._support = tuple(reversed(mapping.keys()))
        c._mapping = mapping.copy()
        c._order = 1

        cycles = []
        while mapping:
            k, el = mapping.popitem()
            cycle = [k]
            while k != el:
                cycle.append(el)
                el = mapping.pop(el)
            cycles.append(tuple(cycle))
            c._order = math.lcm(c._order, len(cycle))
        c._cycles = tuple(cycles)

        return c

    def __pow__(self, n: int) -> 'Cycles':
        if n == 0:
            return Cycles()
        elif n > 0:
            n = n % self.order
            ret = Cycles()
            while n > 0:
                if n % 2 == 1:
                    ret *= self
                self *= self
                n //= 2
            return ret
        else:
            return self.inv()**(-n)

    def __invert__(self):
        return self.inv()

    def inv(self):
        c = Cycles()
        if len(self._cycles) == 0:
            return c
        c._cycles = tuple([(cycle[0], ) + tuple(reversed(cycle[1:]))
                           for cycle in self._cycles])
        c._support = self._support
        c._mapping = {v: k for k, v in self._mapping.items()}
        c._order = self._order
        c._expr = (self, )
        return c

    @property
    def order(self):
        """Returns the order of the permutation.

        The order of a permutation is the least integer n such that
        p**n = e, where e is the identity permutation.
        """
        if self._order is None:
            self._order = math.lcm(*[len(cycle) for cycle in self._cycles])
        return self._order

    @property
    def support(self):
        """Returns the support of the permutation.

        The support of a permutation is the set of elements that are moved by
        the permutation.
        """
        return self._support

    @property
    def signature(self):
        """Returns the signature of the permutation.

        The signature of the permutation is (-1)^n, where n is the number of
        transpositions of pairs of elements that must be composed to build up
        the permutation. 
        """
        return 1 - 2 * ((len(self._support) - len(self._cycles)) % 2)

    def __len__(self):
        return len(self._support)

    def __repr__(self):
        return f'Cycles{tuple(self._cycles)!r}'

    def to_matrix(self) -> np.ndarray:
        """Returns the matrix representation of the permutation."""
        if self._support:
            return permute(np.eye(max(self._support) + 1, dtype=np.int8), self)
        else:
            return np.eye(0, dtype=np.int8)

    def replace(self, expr):
        """replaces each part in expr by its image under the permutation."""
        if isinstance(expr, (tuple, list)):
            return type(expr)(self.replace(e) for e in expr)
        elif isinstance(expr, Cycles):
            return Cycles(*[self.replace(cycle) for cycle in expr._cycles])
        else:
            return self._replace(expr)

    def _replace(self, x: int) -> int:
        return self._mapping.get(x, x)

    def __call__(self, *cycle):
        return self * Cycles(*cycle)

    def commutator(self, x: 'Cycles') -> 'Cycles':
        """Return the commutator of ``self`` and ``x``: ``self*x*self.inv()*x.inv()``

        References
        ==========

        .. [1] https://en.wikipedia.org/wiki/Commutator
        """
        return self * x * self.inv() * x.inv()

    def simplify(self) -> 'Cycles':
        if isinstance(self._expr, list):
            if self.is_identity():
                pass
            elif not self._expr:
                self._expr = [[self, 1]]
            return self

        if len(self._expr) == 1:
            # inv
            self._expr[0].simplify()
            ret = []
            for g, n in reversed(self._expr[0]._expr):
                if n and not g.is_identity():
                    ret.append([g, g.order - n])
            self._expr = ret
        else:
            # mul
            self._expr[0].simplify()
            self._expr[1].simplify()
            ret = [[g, n] for g, n in self._expr[0]._expr
                   if n and not g.is_identity()]
            for g, n in self._expr[1]._expr:
                if ret and ret[-1][0] == g:
                    ret[-1][1] = (ret[-1][1] + n) % g.order
                    if ret[-1][1] == 0:
                        ret.pop()
                elif n and not g.is_identity():
                    ret.append([g, n])
            self._expr = ret

        return self

    def expand(self):
        self.simplify()
        for c, n in self._expr:
            yield from repeat(c, n)


def permute(expr: list | tuple | str | bytes | np.ndarray, perm: Cycles):
    """replaces each part in expr by its image under the permutation."""
    ret = list(expr)
    for cycle in perm._cycles:
        i = cycle[0]
        for j in cycle[1:]:
            ret[i], ret[j] = ret[j], ret[i]
    if isinstance(expr, list):
        return ret
    elif isinstance(expr, tuple):
        return tuple(ret)
    elif isinstance(expr, str):
        return ''.join(ret)
    elif isinstance(expr, bytes):
        return b''.join(ret)
    elif isinstance(expr, np.ndarray):
        return np.array(ret)
    else:
        return ret


def _ne(a, b):
    if isinstance(a, np.ndarray):
        if isinstance(b, np.ndarray):
            return not np.allclose(a, b)
        return True
    else:
        return a != b


def _encode(perm: list, codes: dict) -> list:
    """encode the permutation"""
    ret = []
    for x in perm:
        for k, v in codes.items():
            if _ne(x, v):
                continue
            ret.append(k)
            break
        codes.pop(k)
    return ret


def find_permutation(expr1: list, expr2: list) -> Cycles:
    """find the permutation that transform expr1 to expr2"""
    if len(expr1) != len(expr2):
        raise ValueError("expr1 and expr2 must have the same length")
    codes = {}
    support = []
    perm = []
    for i, (a, b) in enumerate(zip(expr1, expr2)):
        if type(a) != type(b) or _ne(a, b):
            perm.append(b)
            support.append(i)
            codes[i] = a
    if not support:
        return Cycles()
    mapping = {
        k: v
        for k, v in reversed(list(zip(support, _encode(perm, codes))))
        if k != v
    }
    return Cycles._from_sorted_mapping(mapping)


def random_permutation(n: int) -> Cycles:
    """return a random permutation of n elements"""
    cycles = []
    perm = np.random.permutation(n)
    rest = list(perm)
    while len(rest) > 0:
        cycle = [rest.pop(0)]
        el = perm[cycle[-1]]
        while cycle[0] != el:
            cycle.append(el)
            rest.remove(el)
            el = perm[cycle[-1]]
        if len(cycle) > 1:
            cycles.append(tuple(cycle))
    return Cycles(*cycles)
