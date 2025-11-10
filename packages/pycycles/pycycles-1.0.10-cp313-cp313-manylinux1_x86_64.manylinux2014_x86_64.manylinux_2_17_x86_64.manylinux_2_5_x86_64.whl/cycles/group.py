import bisect
import functools
import math
import operator
import random
from itertools import chain, combinations, product
from typing import Callable, TypeVar, Union

import numpy as np

from .cycles import Cycles, permute
from .schreier_sims import (distribute_gens_by_base, orbit_transversal,
                            schreier_sims_incremental)

T = TypeVar('T')


class _NotContained(Exception):
    pass


class PermutationGroup():

    def __init__(self, generators: list[Cycles]):
        self.generators = generators
        self._elements = []
        self._support = None

        self._order = None
        self._orbits = None
        self._center = []
        self._is_abelian = None
        self._is_trivial = None

        # these attributes are assigned after running schreier_sims
        self._base = []
        self._strong_gens = []
        self._basic_orbits = []
        self._transversals: list[dict[int, Cycles]] = []
        self._shape = ()

    def __repr__(self) -> str:
        return f"PermutationGroup({self.generators})"

    def is_trivial(self):
        """Test if the group is the trivial group.

        This is true if the group contains only the identity permutation.
        """
        if self._is_trivial is None:
            self._is_trivial = len(self.generators) == 0
        return self._is_trivial

    def is_abelian(self):
        """Test if the group is Abelian.
        """
        if self._is_abelian is not None:
            return self._is_abelian

        self._is_abelian = True
        for x, y in combinations(self.generators, 2):
            if not x * y == y * x:
                self._is_abelian = False
                break
        return True

    def is_subgroup(self, G: 'PermutationGroup'):
        """Return ``True`` if all elements of ``self`` belong to ``G``."""
        if not isinstance(G, PermutationGroup):
            return False
        if self == G or self.is_trivial():
            return True
        if G.order() % self.order() != 0:
            return False
        return all(g in G for g in self.generators)

    def generate(self, method: str = "schreier_sims"):
        if method == "schreier_sims":
            yield from self.generate_schreier_sims()
        elif method == "dimino":
            yield from self.generate_dimino(self.generators)

    @staticmethod
    def generate_dimino(generators: list[Cycles]):
        """Yield group elements using Dimino's algorithm."""
        e = Cycles()
        yield e
        gens = {e}
        elements = set(generators) | set(g.inv() for g in generators)
        while True:
            new_elements = set()
            for a, b in chain(product(gens, elements), product(elements, gens),
                              product(elements, elements)):
                c = a * b
                if c not in gens and c not in elements and c not in new_elements:
                    new_elements.add(c)
                    yield c
            gens.update(elements)
            if len(new_elements) == 0:
                break
            elements = new_elements

    def generate_schreier_sims(self):
        """Yield group elements using the Schreier-Sims representation
        in coset_rank order
        """
        if self.is_trivial():
            yield Cycles()
            return

        self.schreier_sims()
        for gens in product(
                *
            [list(coset.values()) for coset in reversed(self._transversals)]):
            yield functools.reduce(operator.mul, gens)

    @property
    def support(self):
        """
        Return the support of the group.

        Explanation
        ===========
        The support of a permutation group is the set of integers
        that appear in the cycles of the generators.
        """
        if self._support is None:
            support = set()
            for g in self.generators:
                support.update(g.support)
            self._support = sorted(support)
        return self._support

    @property
    def elements(self) -> list[Cycles]:
        if self._elements == []:
            for g in self.generate():
                bisect.insort(self._elements, g)
        return self._elements

    def random(self, N=1, rng: random.Random = None) -> Cycles | list[Cycles]:
        """Return a random element of the group.

        If N > 1, return a list of N random elements.

        Parameters
        ==========
        N : int
            Number of random elements to return.
        rng : random.Random
            Random number generator to use. If None, the default RNG is used.
        """
        self.schreier_sims()
        transversals = self._transversals
        orbits = self._basic_orbits

        if rng is None:
            rng = random.Random()
        ret = []
        for _ in range(N):
            g = Cycles()
            for orbit, coset in zip(orbits, transversals):
                g *= coset[rng.choice(orbit)]
            ret.append(g)
        if N == 1:
            return ret[0]
        return ret

    @property
    def base(self):
        """Return a base from the Schreier-Sims algorithm."""
        if self._base == []:
            self.schreier_sims()
        return self._base

    def orbit(self,
              alpha: T,
              action: Callable[[T, Cycles], T] | None = None) -> list[T]:
        """finds the orbit under the group action given by a function `action`
        """
        if isinstance(alpha, int) and action is None:
            for orbit in self.orbits():
                if alpha in orbit:
                    return orbit
            else:
                return [alpha]
        elif isinstance(alpha, Cycles) and action is None:
            action = lambda x, y: y * x
        elif action is None:
            action = permute
        orbit = [alpha]
        for beta in orbit:
            for g in self.generators:
                beta = action(beta, g)
                if beta not in orbit:
                    orbit.append(beta)
        return orbit

    def orbits(self):
        if self._orbits is None:
            orbit_parts = []
            for g in self.generators:
                for cycle in g._cycles:
                    for orbit in orbit_parts:
                        if set(cycle) & set(orbit):
                            orbit.update(cycle)
                            break
                    else:
                        orbit_parts.append(set(cycle))
            orbits = []
            for x in orbit_parts:
                for y in orbits:
                    if x & y:
                        y.update(x)
                        break
                else:
                    orbits.append(x)
            self._orbits = orbits
        return self._orbits

    def schreier_sims(self, base: list[int] | None = None):
        """Schreier-Sims algorithm.

        Explanation
        ===========

        It computes the generators of the chain of stabilizers
        `G > G_{b_1} > .. > G_{b1,..,b_r} > 1`
        in which `G_{b_1,..,b_i}` stabilizes `b_1,..,b_i`,
        and the corresponding ``s`` cosets.
        An element of the group can be written as the product
        `h_1*..*h_s`.

        We use the incremental Schreier-Sims algorithm.
        """
        if self._transversals and (base is None or base == self._base):
            return

        base, strong_gens = schreier_sims_incremental(self.generators,
                                                      base=base)
        self._base = base
        self._strong_gens = strong_gens
        if not base:
            self._transversals = []
            self._basic_orbits = []
            return

        strong_gens_distr = distribute_gens_by_base(base, strong_gens)

        # Compute basic orbits and transversals from a base and strong generating set.
        transversals = []
        basic_orbits = []
        for alpha, gens in zip(base, strong_gens_distr):
            transversal = orbit_transversal(gens, alpha)
            basic_orbits.append(list(transversal.keys()))
            transversals.append(transversal)

        self._transversals = transversals
        self._basic_orbits = [sorted(x) for x in basic_orbits]
        self._shape = tuple(
            [len(coset.values()) for coset in reversed(self._transversals)])

    def order(self):
        if self._order is None:
            if self.is_trivial():
                self._order = 1
            else:
                self.schreier_sims()
                self._order = math.prod(len(x) for x in self._transversals)
        return self._order

    def index(self, H: 'PermutationGroup'):
        """
        Returns the index of a permutation group.

        Examples
        ========

        >>> a = Permutation(1,2,3)
        >>> b =Permutation(3)
        >>> G = PermutationGroup([a])
        >>> H = PermutationGroup([b])
        >>> G.index(H)
        3

        """
        if H.is_subgroup(self):
            return self.order() // H.order()

    def __len__(self):
        return self.order()

    def __getitem__(self, i):
        index = np.unravel_index(i, self._shape)
        gens = [
            list(coset.values())[i]
            for i, coset in zip(index, reversed(self._transversals))
        ]
        return functools.reduce(operator.mul, gens)

    def __contains__(self, perm: Cycles):
        if perm in self.generators or perm.is_identity():
            return True
        if self._elements:
            return perm in self._elements
        try:
            perm = self.coset_factor(perm)
            return True
        except _NotContained:
            return False

    def __eq__(self, other) -> bool:
        """Return ``True`` if PermutationGroup generated by elements in the
        group are same i.e they represent the same PermutationGroup.
        """
        if not isinstance(other, PermutationGroup):
            raise TypeError(
                f"'==' not supported between instances of '{type(self)}' and '{type(other)}'"
            )

        set_self_gens = set(self.generators)
        set_other_gens = set(other.generators)

        # before reaching the general case there are also certain
        # optimisation and obvious cases requiring less or no actual
        # computation.
        if set_self_gens == set_other_gens:
            return True

        # in the most general case it will check that each generator of
        # one group belongs to the other PermutationGroup and vice-versa
        for gen1 in set_self_gens:
            if gen1 not in other:
                return False
        for gen2 in set_other_gens:
            if gen2 not in self:
                return False
        return True

    def __lt__(self, other) -> bool:
        if isinstance(other, PermutationGroup):
            return self.is_subgroup(other) and self.order() < other.order()
        else:
            raise TypeError(
                f"'<' not supported between instances of '{type(self)}' and '{type(other)}'"
            )

    def __le__(self, other) -> bool:
        if isinstance(other, PermutationGroup):
            return self.is_subgroup(other)
        else:
            raise TypeError(
                f"'<=' not supported between instances of '{type(self)}' and '{type(other)}'"
            )

    def __mul__(self, other: Cycles):
        if other in self:
            return self
        return Coset(self, other, left=False)

    def __rmul__(self, other: Cycles):
        if other in self:
            return self
        return Coset(self, other, left=True)

    def coset_factor(self, g: Cycles, index=False):
        """Return ``G``'s (self's) coset factorization of ``g``

        Explanation
        ===========

        If ``g`` is an element of ``G`` then it can be written as the product
        of permutations drawn from the Schreier-Sims coset decomposition,

        The permutations returned in ``f`` are those for which
        the product gives ``g``: ``g = f[n]*...f[1]*f[0]`` where ``n = len(B)``
        and ``B = G.base``. f[i] is one of the permutations in
        ``self._basic_orbits[i]``.
        """
        self.schreier_sims()
        factors = []
        for alpha, coset, orbit in zip(self._base, self._transversals,
                                       self._basic_orbits):
            beta = g._replace(alpha)
            if beta == alpha:
                if index:
                    factors.append(0)
                continue
            if beta not in coset:
                raise _NotContained
            u = coset[beta]
            if index:
                factors.append(orbit.index(beta))
            else:
                factors.append(u)
            g = g * u.inv()
            if g.is_identity():
                break
        if not g.is_identity():
            raise _NotContained
        return factors

    def coset_rank(self, g):
        """rank using Schreier-Sims representation.

        Explanation
        ===========

        The coset rank of ``g`` is the ordering number in which
        it appears in the lexicographic listing according to the
        coset decomposition

        The ordering is the same as in G.generate(method='coset').
        If ``g`` does not belong to the group it returns None.
        """
        try:
            index = self.coset_factor(g, index=True)
            index = index + [0] * (len(self._transversals) - len(index))
        except _NotContained:
            raise IndexError(f"Permutation {g} not contained in group.")
        rank = 0
        b = 1
        for i, coset in zip(index, self._transversals):
            rank += b * i
            b = b * len(coset)
        return rank

    def coset_unrank(self, rank):
        """unrank using Schreier-Sims representation

        coset_unrank is the inverse operation of coset_rank
        if 0 <= rank < order; otherwise it returns None.

        """
        if rank < 0 or rank >= self.order():
            return None
        transversals = self._transversals
        orbits = self._basic_orbits
        ret = Cycles()
        for orbit, coset in zip(orbits, transversals):
            rank, c = divmod(rank, len(coset))
            ret = coset[orbit[c]] * ret
        return ret

    def express(self, perm: Cycles):
        if perm.is_identity():
            return Cycles()
        self.schreier_sims()
        return functools.reduce(operator.mul, self.coset_factor(perm)[::-1])

    def stabilizer_chain(self) -> list[tuple[tuple[int], 'PermutationGroup']]:
        r"""
        Return a chain of stabilizers relative to a base and strong generating
        set.

        Explanation
        ===========

        The ``i``-th basic stabilizer `G^{(i)}` relative to a base
        `(b_1, b_2, \dots, b_k)` is `G_{b_1, b_2, \dots, b_{i-1}}`.
        """
        self.schreier_sims()
        strong_gens = self._strong_gens
        base = self._base
        if not base:  # e.g. if self is trivial
            return []
        strong_gens_distr = distribute_gens_by_base(base, strong_gens)
        basic_stabilizers = []
        for i, gens in enumerate(strong_gens_distr):
            basic_stabilizers.append((tuple(base[:i]), PermutationGroup(gens)))
        basic_stabilizers.append((tuple(base), PermutationGroup([])))
        return basic_stabilizers

    def stabilizer(self, alpha) -> 'PermutationGroup':
        """Return the stabilizer subgroup of ``alpha``."""
        orb = [alpha]
        table = {alpha: Cycles()}
        table_inv = {alpha: Cycles()}
        used = {}
        used[alpha] = True
        stab_gens = []
        for b in orb:
            for gen in self.generators:
                temp = gen[b]
                if temp not in used:
                    gen_temp = table[b] * gen
                    orb.append(temp)
                    table[temp] = gen_temp
                    table_inv[temp] = gen_temp.inv()
                    used[temp] = True
                else:
                    schreier_gen = table[b] * gen * table_inv[temp]
                    if schreier_gen not in stab_gens:
                        stab_gens.append(schreier_gen)
        return PermutationGroup(stab_gens)

    def centralizer(self, H: 'PermutationGroup') -> 'PermutationGroup':
        """Return the centralizer of ``H`` in ``self``."""
        raise NotImplementedError

    def normalizer(self, H: 'PermutationGroup') -> 'PermutationGroup':
        """Return the normalizer of ``H`` in ``self``."""
        raise NotImplementedError

    def center(self) -> 'PermutationGroup':
        """Return the center of group."""
        return self.centralizer(self)


class Coset():

    def __init__(self, H: PermutationGroup, g: Cycles, left: bool = True):
        self._left = left
        self._norm = True
        self.H = H
        self.g = g
        for gen in self.H.generators:
            if gen * self.g not in self.g * self.H:
                self._norm = False
                break

    def is_left_coset(self):
        return self._left

    def is_right_coset(self):
        return not self._left

    def __contains__(self, perm: Cycles):
        if self._left:
            return self.g * perm in self.H
        else:
            return perm * self.g in self.H

    def generate(self):
        if self._left:
            for perm in self.H.generate():
                yield self.g * perm
        else:
            for perm in self.H.generate():
                yield perm * self.g

    def __mul__(self, other: Union[PermutationGroup, 'Coset']) -> 'Coset':
        if isinstance(other, PermutationGroup) and other == self.H:
            return self
        elif isinstance(other, Coset) and other.H == self.H:
            return Coset(self.H, self.g * other.g, self._left)
        else:
            raise TypeError(f"Cannot multiply {self} by {other}")
