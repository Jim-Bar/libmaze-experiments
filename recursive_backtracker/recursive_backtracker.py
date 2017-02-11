import enum
import random
import sys

try:
    from typing import Any, Callable, Dict, List, Tuple
except ImportError:
    Any, Callable, Dict, List, Tuple = None, None, None, None, None


class Link(object):
    """

    """

    def __init__(self, is_open):
        # type: (bool) -> None

        self._is_open = is_open

    def open(self):
        # type: () -> None

        self._is_open = True

    def close(self):
        # type: () -> None

        self._is_open = False

    def is_open(self):
        # type: () -> bool

        return self._is_open


class Cell(object):
    """

    """

    def __init__(self, x, y, meta):
        # type: (int, int, Any) -> None

        self._x = x  # type: int
        self._y = y  # type: int
        self._meta = meta  # type: Any
        self._neighbors = dict()  # type: Dict[Maze.Direction, Tuple[Cell, Link]]

    def add_neighbor(self, direction, neighbor, is_open):
        # type: (Maze.Direction, Cell, bool) -> None

        if direction not in self._neighbors:
            link = Link(is_open)
            self._neighbors[direction] = (neighbor, link)
            neighbor._neighbors[direction.opposite()] = (self, link)

    def close(self, direction):
        # type: (Maze.Direction) -> None

        self._neighbors[direction][1].close()

    def is_open(self, direction):
        # type: (Maze.Direction) -> bool

        return self._neighbors[direction][1].is_open()

    def get_meta(self):
        # type: () -> Any

        return self._meta

    def get_neighbor(self, direction):
        # type: (Maze.Direction) -> Cell

        return self._neighbors[direction][0]

    def has_neighbor(self, direction):
        # type: (Maze.Direction) -> bool

        return direction in self._neighbors

    def open(self, direction):
        # type: (Maze.Direction) -> None

        self._neighbors[direction][1].open()

    def set_meta(self, meta):
        # type: (Any) -> None

        self._meta = meta

    def x(self):
        # type: () -> int

        return self._x

    def y(self):
        # type: () -> int

        return self._y


class Maze(object):
    """

    """

    @enum.unique
    class Direction(enum.Enum):
        """

        """

        LEFT = 1
        TOP = 2
        RIGHT = 3
        BOTTOM = 4

        def opposite(self):
            # type: (Maze.Direction) -> Maze.Direction

            if self is Maze.Direction.LEFT:
                return Maze.Direction.RIGHT
            elif self is Maze.Direction.TOP:
                return Maze.Direction.BOTTOM
            elif self is Maze.Direction.RIGHT:
                return Maze.Direction.LEFT
            elif self is Maze.Direction.BOTTOM:
                return Maze.Direction.TOP

    def __init__(self, width, height, carving, meta=None):
        # type: (int, int, bool, Any) -> None

        self._grid = [[Cell(x, y, meta) for y in range(height)] for x in range(width)]  # type: List[List[Cell]]
        self._width = width  # type: int
        self._height = height  # type: int

        # Set links between cells.
        for y in range(height):
            for x in range(width):
                if x > 0:
                    self._grid[x][y].add_neighbor(Maze.Direction.LEFT, self._grid[x - 1][y], not carving)
                if y > 0:
                    self._grid[x][y].add_neighbor(Maze.Direction.TOP, self._grid[x][y - 1], not carving)
                if x < self._width - 1:
                    self._grid[x][y].add_neighbor(Maze.Direction.RIGHT, self._grid[x + 1][y], not carving)
                if y < self._height - 1:
                    self._grid[x][y].add_neighbor(Maze.Direction.BOTTOM, self._grid[x][y + 1], not carving)

    def cell(self, x, y):
        # type: (int, int) -> Cell

        return self._grid[x][y]

    def height(self):
        # type: () -> int

        return self._height

    def width(self):
        # type: () -> int

        return self._width


class RecursiveBackTracker(object):
    """

    """

    @staticmethod
    def run(width, height):
        # type: (int, int) -> Maze

        maze = Maze(width, height, True, False)
        sys.setrecursionlimit(width * height + 10)
        RecursiveBackTracker.recursive(maze.cell(width // 2, height //2))

        return maze

    @staticmethod
    def recursive(cell):
        # type: (Cell) -> None

        cell.set_meta(True)
        directions = [direction for direction in Maze.Direction]
        random.shuffle(directions)
        for direction in directions:
            if cell.has_neighbor(direction) and not cell.get_neighbor(direction).get_meta():
                cell.open(direction)
                RecursiveBackTracker.recursive(cell.get_neighbor(direction))


class MazeExporter(object):
    """

    """

    @staticmethod
    def export(maze):
        # type: (Maze) -> None

        maze_representation = ''
        for y in range(maze.height()):
            for x in range(maze.width()):
                value = 0
                if maze.cell(x, y).has_neighbor(Maze.Direction.LEFT) and maze.cell(x, y).is_open(Maze.Direction.LEFT):
                    value |= 1
                if maze.cell(x, y).has_neighbor(Maze.Direction.TOP) and maze.cell(x, y).is_open(Maze.Direction.TOP):
                    value |= 2
                if maze.cell(x, y).has_neighbor(Maze.Direction.RIGHT) and maze.cell(x, y).is_open(Maze.Direction.RIGHT):
                    value |= 4
                if maze.cell(x, y).has_neighbor(Maze.Direction.BOTTOM) and maze.cell(x, y).is_open(Maze.Direction.BOTTOM):
                    value |= 8
                maze_representation += '{} '.format(value)
            maze_representation += '\n'

        with open('maze.txt', 'w') as maze_file:
            maze_file.write(maze_representation)

MazeExporter.export(RecursiveBackTracker.run(50, 25))
