import operator
from functools import reduce
from itertools import islice, product
from typing import Literal, Sequence

from ..cycles import Cycles, find_permutation
from ..group import PermutationGroup
from .chp import run_circuit
from .paulis import encode_paulis

OneQubitCliffordGateType = Literal['H', 'S', '-S', 'X', 'X/2', '-X/2', 'Y',
                                   'Y/2', '-Y/2', 'Z/2', '-Z/2', 'Z']
TwoQubitCliffordGateType = Literal['CZ', 'iSWAP', '-iSWAP', 'Cnot', 'CX',
                                   'SWAP', 'CR']


def cliffordOrder(n: int) -> int:
    """
    Order of complex Clifford group of degree 2^n arising in quantum coding theory.
    
    Sloane, N. J. A. (ed.). "Sequence A003956 (Order of Clifford group)".
    The On-Line Encyclopedia of Integer Sequences. OEIS Foundation.
    https://oeis.org/A003956
    """
    return reduce(operator.mul, (((1 << (2 * j)) - 1) << 2 * j + 1
                                 for j in range(1, n + 1)), 1)


def make_stablizers(N: int) -> list[int]:
    stablizers = []
    for s in islice(product('IXYZ', repeat=N), 1, None):
        n = encode_paulis(''.join(s))
        stablizers.append(n)
        stablizers.append(n | 2)

    return stablizers


def verify_one_qubit_clifford_generators(
        gates: Sequence[OneQubitCliffordGateType]) -> bool:
    stablizers = make_stablizers(1)
    generators = []
    for gate in gates:
        generators.append(
            find_permutation(stablizers,
                             run_circuit([(gate, 0)], stablizers)[0]))
    g = PermutationGroup(generators)
    elms = [Cycles((0, 4), (1, 5), (2, 3)), Cycles((0, 2, 1, 3), )]

    for el in elms:
        if el not in g:
            return False
    return True


def make_clifford_generators(
    N: int,
    one_qubit_gates: Sequence[OneQubitCliffordGateType] = ('H', 'S'),
    graph: list[tuple[TwoQubitCliffordGateType, int, int]] = []
) -> dict[tuple, Cycles]:

    if not verify_one_qubit_clifford_generators(one_qubit_gates):
        raise ValueError("Imperfection in one_qubit_gates generators.")

    if not graph:
        graph = [('CZ', i, i + 1) for i in range(N - 1)]

    stablizers = make_stablizers(N)

    generators = {}

    for i in range(N):
        for gate in one_qubit_gates:
            generators[(gate, i)] = find_permutation(
                stablizers,
                run_circuit([(gate, i)], stablizers)[0])

    for two_qubit_gate, i, j in graph:
        generators[(two_qubit_gate, i, j)] = find_permutation(
            stablizers,
            run_circuit([(two_qubit_gate, i, j)], stablizers)[0])

    return generators


class CliffordGroup(PermutationGroup):

    def __init__(self,
                 N: int,
                 one_qubit_gates: Sequence[OneQubitCliffordGateType] = ('H',
                                                                        'S'),
                 two_qubit_gate: TwoQubitCliffordGateType = 'CZ',
                 graph: list[tuple[int, int]] = [],
                 generators: dict[tuple, Cycles] | None = None):
        self.N = N
        self.stabilizers = make_stablizers(N)
        if generators is None:
            if graph:
                generators = make_clifford_generators(N, one_qubit_gates,
                                                      [(two_qubit_gate, i, j)
                                                       for i, j in graph])
            else:
                generators = make_clifford_generators(
                    N, one_qubit_gates,
                    [(two_qubit_gate, i, i + 1) for i in range(N - 1)])
        super().__init__(list(generators.values()))
        self.reversed_map = {v: k for k, v in generators.items()}
        self.gate_map = generators
        self.gate_map_inv = {v: k for k, v in generators.items()}

    def __len__(self):
        return cliffordOrder(self.N)

    def permutation_to_circuit(self, perm: Cycles) -> list:
        perm = self.express(perm)
        return [self.reversed_map[c] for c in perm.expand()]

    def circuit_to_permutation(self, circuit: list) -> Cycles:
        perm = Cycles()
        for gate in circuit:
            if gate not in self.gate_map:
                p = find_permutation(self.stabilizers,
                                     run_circuit([gate], self.stabilizers)[0])
                self.gate_map[gate] = p
                self.gate_map_inv[p] = gate
            perm = perm * self.gate_map[gate]
        return self.express(perm)

    def circuit_inv(self, circuit: list) -> list:
        perm = self.circuit_to_permutation(circuit).inv()
        return self.permutation_to_circuit(perm)
