import logging

from .cycles import Cycles

logger = logging.getLogger(__name__)


def _strip(h: Cycles, base: list[int], orbits: dict[int, list[int]],
           transversals: dict[int, dict[int, Cycles]],
           j: int) -> tuple[Cycles, int]:
    """
    """
    base_len = len(base)
    for i in range(j + 1, base_len):
        beta = h._replace(base[i])
        if beta == base[i]:
            continue
        if beta not in orbits[i]:
            return h, i + 1
        u = transversals[i][beta]
        if h == u:
            return None, base_len + 1
        h = h * u.inv()
    return h, base_len + 1


def orbit_transversal(
        generators: list[Cycles],
        alpha: int,
        Identity: Cycles = Cycles(),
) -> dict[int, Cycles]:
    r"""Computes a transversal for the orbit of ``alpha`` as a set.

    Explanation
    ===========

    generators   generators of the group ``G``

    For a permutation group ``G``, a transversal for the orbit
    `Orb = \{g(\alpha) | g \in G\}` is a set
    `\{g_\beta | g_\beta(\alpha) = \beta\}` for `\beta \in Orb`.
    Note that there may be more than one possible transversal.
    """
    tr = [(alpha, Identity)]
    db = {alpha}
    for x, px in tr:
        for i, gen in enumerate(generators):
            temp = gen._replace(x)
            if temp not in db:
                db.add(temp)
                tr.append((temp, px * gen))

    return dict(tr)


def distribute_gens_by_base(base: list[int],
                            gens: list[Cycles]) -> list[list[Cycles]]:
    r"""
    Distribute the group elements ``gens`` by membership in basic stabilizers.

    Explanation
    ===========

    Notice that for a base `(b_1, b_2, \dots, b_k)`, the basic stabilizers
    are defined as `G^{(i)} = G_{b_1, \dots, b_{i-1}}` for
    `i \in\{1, 2, \dots, k\}`.

    Parameters
    ==========

    base : a sequence of points in `\{0, 1, \dots, n-1\}`
    gens : a list of elements of a permutation group of degree `n`.

    Returns
    =======
    list
        List of length `k`, where `k` is the length of *base*. The `i`-th entry
        contains those elements in *gens* which fix the first `i` elements of
        *base* (so that the `0`-th entry is equal to *gens* itself). If no
        element fixes the first `i` elements of *base*, the `i`-th element is
        set to a list containing the identity element.
    """
    base_len = len(base)
    stabs = [[] for _ in range(base_len)]
    max_stab_index = 0
    for gen in gens:
        j = 0
        while j < base_len - 1 and gen._replace(base[j]) == base[j]:
            j += 1
        if j > max_stab_index:
            max_stab_index = j
        for k in range(j + 1):
            stabs[k].append(gen)
    for i in range(max_stab_index + 1, base_len):
        stabs[i].append(Cycles())
    return stabs


def schreier_sims_incremental(
        gens: list[Cycles],
        base: list[int] | None = None) -> tuple[list[int], list[Cycles]]:
    """Extend a sequence of points and generating set to a base and strong
    generating set.

    Parameters
    ==========
    gens
        The generating set to be extended to a strong generating set
        relative to the base obtained.

    base
        The sequence of points to be extended to a base. Optional
        parameter with default value ``[]``.

    Returns
    =======

    (base, strong_gens)
        ``base`` is the base obtained, and ``strong_gens`` is the strong
        generating set relative to it. The original parameters ``base``,
        ``gens`` remain unchanged.
    """
    if base is None:
        base = []
    else:
        base = base.copy()
    support = set()
    for g in gens:
        support.update(g.support)
    # handle the trivial group
    if len(gens) == 1 and gens[0].is_identity():
        return base, gens, {gens[0]: [gens[0]]}
    # remove the identity as a generator
    gens = [x for x in gens if not x.is_identity()]
    # make sure no generator fixes all base points
    for gen in gens:
        if all(x == gen._replace(x) for x in base):
            for new in support:
                if gen._replace(new) != new:
                    break
            else:
                assert None  # can this ever happen?
            base.append(new)
    #logger.debug("Schreier-Sims: base = %s, gens = %s", _base, _gens)
    # distribute generators according to basic stabilizers
    strong_gens_distr = distribute_gens_by_base(base, gens)
    new_strong_gens = []
    # initialize the basic stabilizers, basic orbits and basic transversals
    orbs = {}
    transversals = {}
    for i, alpha in enumerate(base):
        transversals[i] = orbit_transversal(strong_gens_distr[i], alpha)
        orbs[i] = list(transversals[i].keys())
    # main loop: amend the stabilizer chain until we have generators
    # for all stabilizers
    base_len = len(base)
    i = base_len - 1
    while i >= 0:
        # this flag is used to continue with the main loop from inside
        # a nested loop
        continue_i = False
        # test the generators for being a strong generating set
        db = {}
        for beta, u_beta in list(transversals[i].items()):
            for j, gen in enumerate(strong_gens_distr[i]):
                gb = gen._replace(beta)
                u1 = transversals[i][gb]
                g1 = u_beta * gen
                if g1 != u1:
                    # test if the schreier generator is in the i+1-th
                    # would-be basic stabilizer
                    new_strong_generator_found = False
                    try:
                        u1_inv = db[gb]
                    except KeyError:
                        u1_inv = db[gb] = u1.inv()
                    schreier_gen = g1 * u1_inv
                    h, j = _strip(schreier_gen, base, orbs, transversals, i)
                    if j <= base_len:
                        # new strong generator h at level j
                        new_strong_generator_found = True
                    elif h is not None:
                        # h fixes all base points
                        new_strong_generator_found = True
                        for moved in support:
                            if h._replace(moved) != moved:
                                break
                        base.append(moved)
                        base_len += 1
                        strong_gens_distr.append([])
                    if new_strong_generator_found:
                        # if a new strong generator is found, update the
                        # data structures and start over
                        new_strong_gens.append(h)
                        for l in range(i + 1, j):
                            strong_gens_distr[l].append(h)
                            transversals[l] =\
                            orbit_transversal(strong_gens_distr[l],
                                base[l])
                            orbs[l] = list(transversals[l].keys())
                        i = j - 1
                        # continue main loop using the flag
                        continue_i = True
                if continue_i is True:
                    break
            if continue_i is True:
                break
        logger.debug(
            "Schreier-Sims: i = %s, continue_i = %s, len(transversals[i]) = %s",
            i, continue_i, len(transversals[i]))
        if continue_i is True:
            continue
        i -= 1

    return (base, gens + new_strong_gens)
