import enum
import math
import operator
from fractions import Fraction
from functools import reduce, total_ordering
from itertools import chain, product
from typing import NamedTuple

import numpy as np
import qutip as qt


class OpType(enum.Enum):
    scalar = 0
    boson = 1
    fermion = 2


class _BaseOp(NamedTuple):
    tag: str = 'a'
    dag: bool = False
    type: OpType = OpType.boson
    n: int = 1

    def _format(self) -> str:
        dagger = '*' if self.type == OpType.scalar else '\\dagger{}'
        if self.n == 1:
            return f"{self.tag}^{{{dagger}}}" if self.dag else f"{self.tag}"
        else:
            return f"{self.tag}^{{{dagger} {self.n}}}" if self.dag else f"{self.tag}^{self.n}"

    def _repr_latex_(self) -> str:
        return f"${self._format()}$"


def _format_op(op) -> str:
    if op.n == 1:
        s = f"{op.tag}^{{\\dagger}}" if op.dag else f"{op.tag}"
    else:
        s = f"{op.tag}^{{\\dagger {op.n}}}" if op.dag else f"{op.tag}^{op.n}"
    if op.amp == 1 and not op.imag:
        return s
    elif op.amp == -1 and not op.imag:
        return '-' + s
    elif op.amp == 1 and op.imag:
        return f"i" + s
    elif op.amp == -1 and op.imag:
        return f"-i" + s
    elif op.amp.denominator == 1:
        if op.imag:
            num = f"{op.amp.numerator}i"
        else:
            num = f"{op.amp.numerator}"
    else:
        if op.imag:
            num = f"\\frac{{{abs(op.amp.numerator)}i}}{{{op.amp.denominator}}}"
        else:
            num = f"\\frac{{{abs(op.amp.numerator)}}}{{{op.amp.denominator}}}"
        if op.amp.numerator < 0:
            num = '-' + num
    return num + s


class _Op():

    def __init__(self, ops: list[_BaseOp] = []):
        self.ops: dict[str, list[_BaseOp]] = {}
        for op in ops:
            self.ops.setdefault(op.tag, []).append(op)
        self.ops = {k: self.ops[k] for k in sorted(self.ops.keys())}

    def _format(self):
        return ''.join(op._format()
                       for op in chain.from_iterable(self.ops.values()))

    def _repr_latex_(self) -> str:
        return f"${self._format()}$"

    def _as_key(self):
        return tuple(
            [tuple(o) for o in chain.from_iterable(self.ops.values())])

    def __hash__(self):
        return hash(self._as_key())

    @staticmethod
    def _mul_subsys(l1: list[_BaseOp], l2: list[_BaseOp]) -> list[_BaseOp]:
        if not l2:
            return l1
        if not l1:
            return l2
        if l1[-1].tag != l2[0].tag or l1[-1].dag != l2[-1].dag:
            return [*l1, *l2]

        l = [*l1]
        op = l2[0]._replace(n=l[-1].n + l2[0].n)
        l.pop()
        if op.n != 0:
            l.append(op)
        l.extend(l2[1:])

        return l

    def __mul__(self, other):
        if isinstance(other, _Op):
            d = self.ops.copy()
            for k, v in other.ops.items():
                d[k] = self._mul_subsys(d.get(k, []), v)
            ret = _Op()
            ret.ops = {k: d[k] for k in sorted(d.keys())}
            return ret
        else:
            raise TypeError(
                "Unsupported operand type for *: '_Op' and '{}'".format(
                    type(other)))

    @staticmethod
    def _swap(l: list[_BaseOp], i: int):
        d = []
        a, b = l[i], l[i + 1]
        h, t = l[:i], l[i + 2:]

        m, n = a.n, b.n
        x = 0
        for i in range(min(m, n)):
            x = math.perm(n, i)
            d.append(
                (x,
                 reduce(
                     _Op._mul_subsys,
                     [h, [b._replace(n=b.n - i)], [a._replace(n=a.n - i)], t
                      ])))

        d.append(
            (x * (abs(m - n) + 1),
             reduce(_Op._mul_subsys, [
                 h, [b._replace(n=b.n - i - 1)], [a._replace(n=a.n - i - 1)], t
             ])))

        return d

    @staticmethod
    def _sort_subsys(l: list[_BaseOp]) -> list[tuple[list[_BaseOp], int]]:
        d = {}
        n = len(l)
        rest = {}

        for i in range(n):
            for j in range(0, n - i - 1):
                if l[j] > l[j + 1]:
                    l, (o, s) = _Op._swap(l, j)
                    l = list(l)
                    if s != 0:
                        rest[o] = rest.get(o, 0) + s
        return d

    def simplify(self):
        pass


class Operator():

    def __init__(self):
        self.ops = {}


@total_ordering
class _Create():

    def __init__(self, tag='a', dag=True):
        self.tag = tag
        self._dag = dag

    def __eq__(self, other):
        if isinstance(other, int):
            return False
        return self.tag == other.tag and self._dag == other._dag

    def __lt__(self, other):
        if isinstance(other, int):
            return False
        return (self.tag, not self._dag) < (other.tag, not other._dag)

    def dag(self):
        return _Create(self.tag, not self._dag)

    def qobj(self, N):
        if self._dag:
            return qt.create(N)
        else:
            return qt.destroy(N)

    def _repr_latex_(self):
        if self._dag:
            return f"${self.tag}^{{\\dagger}}$"
        else:
            return f"${self.tag}$"

    def commutator(self, other):
        if other.tag != self.tag or other._dag == self._dag:
            return 0
        elif self._dag:
            return -1
        else:
            return 1

    def __hash__(self):
        return hash((self.tag, self._dag))


class _Destroy(_Create):

    def __init__(self, tag='a', dag=False):
        super().__init__(tag, dag)


class Operator():

    def __init__(self):
        self.ops = {}

    def dag(self):
        ops = {
            tuple([x if isinstance(x, int) else x.dag() for x in k[::-1]]):
            np.conj(v)
            for k, v in self.ops.items()
        }
        ret = Operator()
        ret.ops = ops
        return ret

    def qobj(self, N):
        tags = set()
        for k in self.ops:
            if isinstance(k, int):
                continue
            for o in k:
                tags.add(o.tag)
        tags = sorted(tags)
        l = []
        for k, v in self.ops.items():
            l.append(v * self._qobj(N, tags, k))
        return reduce(operator.add, l)

    def _qobj(self, N, tags, op):
        if isinstance(op, int):
            op = ()
        d = {}
        for o in op:
            if o.tag in d:
                d[o.tag] = d[o.tag] * o.qobj(N)
            else:
                d[o.tag] = o.qobj(N)
        l = []
        for t in tags:
            l.append(d.get(t, qt.qeye(N)))
        return qt.tensor(*l)

    def _swap(self, op, i):
        if isinstance(op[i], int) or isinstance(op[i + 1], int):
            s = 0
        else:
            s = op[i].commutator(op[i + 1])
        y = list(op)
        y[i], y[i + 1] = y[i + 1], y[i]
        y2 = list(op[:i] + op[i + 2:])
        if len(y2) == 0:
            o = 1
        else:
            o = tuple(y2)
        return tuple(y), (o, s)

    def _bubble_sort(self, op):
        n = len(op)
        arr = list(op)
        rest = {}

        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr, (o, s) = self._swap(arr, j)
                    arr = list(arr)
                    if s != 0:
                        rest[o] = rest.get(o, 0) + s
        return tuple(arr), rest

    def simplify(self):
        ops = {}
        ops2 = self.ops.copy()
        while True:
            try:
                k, v = ops2.popitem()
            except KeyError:
                break
            if isinstance(k, int):
                ops[k] = v
                continue

            op, rest = self._bubble_sort(k)
            ops[op] = v
            for k, s in rest.items():
                ops2[k] = ops2.get(k, 0) + s * v

        ops = {k: v for k, v in ops.items() if v != 0}

        if not ops:
            return 0

        def f(x):
            if isinstance(x, int):
                x = 0
            else:
                x = len(x)
            return -x

        ops = {k: ops[k] for k in sorted(ops.keys(), key=f)}
        ret = Operator()
        ret.ops = ops
        return ret

    def __neg__(self):
        ret = Operator()
        for key, value in self.ops.items():
            ret.ops[key] = -value
        return ret

    def __add__(self, other):
        if isinstance(other, (int, float, complex)):
            if other == 0:
                return self
            ret = Operator()
            ret.ops = self.ops.copy()
            if 1 not in self.ops:
                ret.ops[1] = other
            else:
                ret.ops[1] += other
            return ret
        elif isinstance(other, Operator):
            ret = Operator()
            ret.ops = self.ops.copy()
            for key, value in other.ops.items():
                if key not in ret.ops:
                    ret.ops[key] = value
                else:
                    ret.ops[key] += value
                    if ret.ops[key] == 0:
                        ret.ops.pop(key)
            return ret
        else:
            raise TypeError(
                "Unsupported operand type for +: 'Operator' and '{}'".format(
                    type(other)))

    def __radd__(self, other):
        if isinstance(other, (int, float, complex)):
            return self + other
        else:
            return other.__add__(self)

    def __mul__(self, other):
        if isinstance(other, (int, float, complex)):
            if other == 0:
                return 0
            else:
                ret = Operator()
                for k, v in self.ops.items():
                    ret.ops[k] = v * other
                return ret
        elif isinstance(other, Operator):
            ret = Operator()
            for (k1, v1), (k2, v2) in product(self.ops.items(),
                                              other.ops.items()):
                if isinstance(k1, int):
                    key = k2
                elif isinstance(k2, int):
                    key = k1
                else:
                    key = k1 + k2
                if key in ret.ops:
                    ret.ops[key] += v1 * v2
                    if ret.ops[key] == 0:
                        ret.ops.pop(key)
                else:
                    ret.ops[key] = v1 * v2
            return ret
        else:
            TypeError(
                "Unsupported operand type for *: 'Operator' and '{}'".format(
                    type(other)))

    def __rmul__(self, other):
        if isinstance(other, (int, float, complex)):
            return self * other
        else:
            return other.__mul__(self)

    def __sub__(self, other):
        return self + (-other)

    def __truediv__(self, other):
        return (1 / other) * self

    def _repr_latex_(self):
        terms = []
        for k, v in self.ops.items():
            if isinstance(k, int) and k == 1 or len(k) == 0:
                terms.append(f"{v}")
                continue

            parts = []
            for op in k:
                if op._dag:
                    s = f"{op.tag}^{{\\dagger}}"
                else:
                    s = f"{op.tag}"
                parts.append(s)
            if v == 1:
                terms.append(''.join(parts))
            elif v == -1:
                terms.append('-' + ''.join(parts))
            else:
                if v.imag == 0:
                    v = v.real
                if v == 1j:
                    num = 'i'
                elif v == -1j:
                    num = '-i'
                elif v.real == 0 and v.imag != 0:
                    num = f'{v.imag}i'
                else:
                    num = f'{v}'
                terms.append(num + ''.join(parts))
        s = ""
        for t in terms:
            if t[0] == '-':
                s = s + t
            else:
                s = s + '+' + t
        if s and s[0] == '+':
            s = s[1:]
        if s == '':
            s = '0'
        s = '$' + s + '$'
        return s


def create(tag='a'):
    op = Operator()
    op.ops[(_Create(tag), )] = 1
    return op


def destroy(tag='a'):
    op = Operator()
    op.ops[(_Destroy(tag), )] = 1
    return op


def commutator(a, b):
    return a * b - b * a


def anticommutator(a, b):
    return a * b + b * a
