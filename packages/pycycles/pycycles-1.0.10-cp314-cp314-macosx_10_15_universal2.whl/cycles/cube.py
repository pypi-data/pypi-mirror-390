from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from .cycles import Cycles, find_permutation
from .group import PermutationGroup

Face = Literal['U', 'D', 'F', 'B', 'L', 'R']


def _rot(x: int, y: int, z: int, face: Face):
    """
    90 degre anticlockwise rotation around the given axis.
    """
    return {
        'R': (x, -z, y),
        'L': (x, z, -y),
        'B': (z, y, -x),
        'F': (-z, y, x),
        'U': (-y, x, z),
        'D': (y, -x, z),
    }[face]


def draw_cube(ax, position, size=2, colors=None):
    if colors is None:
        colors = ["blue", "green", "orange", "red", "white", "yellow"]

    # Define the vertices of a unit cube
    vertices = np.array([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
                         [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]])

    # Scale and translate the vertices to the correct position
    vertices = vertices * size / 2 + position

    # Define the six faces of the unit cube
    faces = [[vertices[j] for j in [0, 1, 5, 4]],
             [vertices[j] for j in [7, 6, 2, 3]],
             [vertices[j] for j in [0, 3, 7, 4]],
             [vertices[j] for j in [1, 2, 6, 5]],
             [vertices[j] for j in [0, 1, 2, 3]],
             [vertices[j] for j in [4, 5, 6, 7]]]

    # Create a Poly3DCollection object from the faces
    cube = Poly3DCollection(faces,
                            facecolors=colors,
                            linewidths=1,
                            edgecolors="k")

    # Add the cube to the axis
    ax.add_collection3d(cube)


class Cube():

    def __init__(self, position: tuple[int, int, int], colors: dict):
        self.position = position
        self.colors = colors

    def draw(self, ax):
        draw_cube(ax, self.position, colors=[self.colors[k] for k in "FBLRDU"])

    def rot(self, face):
        self.position = _rot(*self.position, face)
        s = {
            'U': 'RLFBDU',
            'D': 'LRBFDU',
            'F': 'FBDURL',
            'B': 'FBUDLR',
            'L': 'UDLRFB',
            'R': 'DULRBF'
        }[face]
        self.colors = {k: self.colors[v] for k, v in zip(s, "FBLRDU")}

    def face_position(self, face: Face) -> tuple[int, int, int]:
        pos = {
            'U': (0, 0, 1),
            'D': (0, 0, -1),
            'F': (0, -1, 0),
            'B': (0, 1, 0),
            'L': (-1, 0, 0),
            'R': (1, 0, 0)
        }[face]

        return tuple([a + b for a, b in zip(pos, self.position)])

    def __repr__(self):
        return "Cube(position={}, colors={})".format(self.position,
                                                     self.colors)


class RubikCube():

    def __init__(self, N: int = 3, colors: dict[Face, str] | None = None):
        self.N = N
        if colors is None:
            self.colors = {
                "F": "blue",
                "B": "green",
                "L": "orange",
                "R": "red",
                "D": "white",
                "U": "yellow"
            }
        else:
            self.colors = colors
        self.cubes: list[Cube] = []
        tmp = set()
        for i in range(-N + 1, N + 1, 2):
            for j in range(-N + 1, N + 1, 2):
                for position in [(i, j, -N + 1), (i, j, N - 1), (i, -N + 1, j),
                                 (i, N - 1, j), (-N + 1, i, j), (N - 1, i, j)]:
                    if position not in tmp:
                        c = {k: "black" for k in "FBLRDU"}
                        if position[0] == -N + 1:
                            c['L'] = self.colors['L']
                        if position[0] == N - 1:
                            c['R'] = self.colors['R']
                        if position[1] == -N + 1:
                            c['F'] = self.colors['F']
                        if position[1] == N - 1:
                            c['B'] = self.colors['B']
                        if position[2] == -N + 1:
                            c['D'] = self.colors['D']
                        if position[2] == N - 1:
                            c['U'] = self.colors['U']
                        self.cubes.append(Cube(position, colors=c))
                    tmp.add(position)

    def rot(self, face: Face, level: int = 0):
        axis, sign = {
            'U': (2, 1),
            'D': (2, -1),
            'F': (1, -1),
            'B': (1, 1),
            'L': (0, -1),
            'R': (0, 1)
        }[face]

        def selected(point):
            return sign * point[axis] == self.N - 1 - 2 * level

        for cube in self.cubes:
            if selected(cube.position):
                cube.rot(face)
        return self

    def face_position_list(self) -> list[tuple[int, int, int]]:
        ret = []
        for cube in self.cubes:
            d = {}
            for f, c in cube.colors.items():
                if c != 'black':
                    d[c] = f
            for color in self.colors.values():
                if color in d and not any(
                        cube.position[i] == cube.position[j] == 0
                        for (i, j) in [(0, 1), (1, 2), (0, 2)]):
                    ret.append(cube.face_position(d[color]))
        return ret

    def permutation(self, other: 'RubikCube') -> Cycles:
        if self.N != other.N:
            raise ValueError('Cubes must have the same size')

        return find_permutation(self.face_position_list(),
                                other.face_position_list())

    def draw(self, fig=None):
        if fig is None:
            fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        for cube in self.cubes:
            cube.draw(ax)
        ax.set_xlim([-self.N, self.N])
        ax.set_ylim([-self.N, self.N])
        ax.set_zlim([-self.N, self.N])
        ax.set_title('Rubik\'s Cube')
        ax.set_box_aspect((1, 1, 1))
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        ax.set_axis_off()


class RubikGroup(PermutationGroup):
    """
    The Rubik Group

    The Rubik Group is the group of permutations of the Rubik's Cube.
    It is generated by the following moves:

        U: Up
        F: Front
        L: Left
        B: Back
        R: Right
        D: Down

    where each move is a 90 degree clockwise rotation of the face.
    """

    def __init__(self, N: int = 3):
        cube = RubikCube(N)

        if N <= 3:
            self.ops = {
                face: cube.permutation(RubikCube(N).rot(face))
                for face in 'UDFBLR'
            }
        else:
            self.ops = {}
            for face in 'UDFBLR':
                for level in range(0, N // 2):
                    self.ops[f'{face}{level}'] = cube.permutation(
                        RubikCube(N).rot(face, level))
        super().__init__(list(self.ops.values()))
