from cycles import CliffordGroup, PermutationGroup
from cycles.clifford import cliffordOrder
from cycles.clifford.group import make_clifford_generators


def test_cliffordOrder():
    assert cliffordOrder(0) == 1
    assert cliffordOrder(1) == 24
    assert cliffordOrder(2) == 11520
    assert cliffordOrder(3) == 92897280

    for N in [1, 2, 3]:
        clifford = PermutationGroup(list(make_clifford_generators(N).values()))
        assert clifford.order() == cliffordOrder(N)

        clifford = CliffordGroup(N)
        assert clifford.order() == cliffordOrder(N)
