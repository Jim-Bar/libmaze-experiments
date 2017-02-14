import enum

try:
    from typing import Any, Callable, Dict, List, Set, Tuple
except ImportError:
    Any, Callable, Dict, List, Set, Tuple = None, None, None, None, None, None


class Link(object):
    """
    Link between two adjacent cells. A link is either a wall or a passage.
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
    Each cell is a square in the maze. Cells are separated by walls or passages (i.e. links). Cells have a field 'meta'
    which can be used by algorithms for stored arbitrary data about this cell.
    """

    def __init__(self, x, y, meta):
        # type: (int, int, Any) -> None

        self._x = x  # type: int
        self._y = y  # type: int
        self._meta = meta  # type: Any
        self._neighbors = dict()  # type: Dict[Maze.Direction, Tuple[Cell, Link]]

    def __str__(self):
        # type: () -> str

        return '({}, {})'.format(self._x, self._y)

    def add_neighbor(self, direction, neighbor, is_open):
        # type: (Maze.Direction, Cell, bool) -> None

        if direction not in self._neighbors:
            self.replace_neighbor(direction, neighbor, is_open)

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

    def replace_neighbor(self, direction, neighbor, is_open):
        # type: (Maze.Direction, Cell, bool) -> None

        link = Link(is_open)
        self._neighbors[direction] = (neighbor, link)
        neighbor._neighbors[direction.opposite()] = (self, link)

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
    A maze composed of cells.
    """

    @enum.unique
    class Direction(enum.Enum):
        """

        """

        LEFT = 1
        UP = 2
        RIGHT = 3
        DOWN = 4

        def opposite(self):
            # type: (Maze.Direction) -> Maze.Direction

            if self is Maze.Direction.LEFT:
                return Maze.Direction.RIGHT
            elif self is Maze.Direction.UP:
                return Maze.Direction.DOWN
            elif self is Maze.Direction.RIGHT:
                return Maze.Direction.LEFT
            elif self is Maze.Direction.DOWN:
                return Maze.Direction.UP

    # TODO: Make a class out of 'sub_mazes'.
    def __init__(self, width, height, carving, meta=None, sub_mazes=None):
        # type: (int, int, bool, Any, List[Tuple[Maze, List[Tuple[int, int, Maze.Direction, bool]], Tuple[int, int]]]) -> None

        self._grid = [[Cell(x, y, meta) for y in range(height)] for x in range(width)]  # type: List[List[Cell]]
        self._width = width  # type: int
        self._height = height  # type: int

        # Set links between cells.
        for y in range(height):
            for x in range(width):
                if x > 0:
                    self.cell(x, y).add_neighbor(Maze.Direction.LEFT, self.cell(x - 1, y), not carving)
                if y > 0:
                    self.cell(x, y).add_neighbor(Maze.Direction.UP, self.cell(x, y - 1), not carving)
                if x < self.width() - 1:
                    self.cell(x, y).add_neighbor(Maze.Direction.RIGHT, self.cell(x + 1, y), not carving)
                if y < self.height() - 1:
                    self.cell(x, y).add_neighbor(Maze.Direction.DOWN, self.cell(x, y + 1), not carving)

        # Insert sub mazes if there are some.
        if sub_mazes is None:
            sub_mazes = list()
        for sub_maze, special_cases, (sub_x, sub_y) in sub_mazes:
            for y in range(sub_maze.height()):
                for x in range(sub_maze.width()):
                    abs_x = sub_x + x
                    abs_y = sub_y + y
                    self._grid[abs_x][abs_y] = sub_maze.cell(x, y)

                    # Reconnect adjacent cells.
                    if abs_x > 0 and x is 0:
                        self.cell(abs_x, abs_y).replace_neighbor(Maze.Direction.LEFT,
                                                                 self.cell(abs_x - 1, abs_y), not carving)
                    if abs_y > 0 and y is 0:
                        self.cell(abs_x, abs_y).replace_neighbor(Maze.Direction.UP,
                                                                 self.cell(abs_x, abs_y - 1), not carving)
                    if abs_x < self.width() - 1 and x is sub_maze.width() - 1:
                        self.cell(abs_x, abs_y).replace_neighbor(Maze.Direction.RIGHT,
                                                                 self.cell(abs_x + 1, abs_y), not carving)
                    if abs_y < self.height() - 1 and y is sub_maze.height() - 1:
                        self.cell(abs_x, abs_y).replace_neighbor(Maze.Direction.DOWN,
                                                                 self.cell(abs_x, abs_y + 1), not carving)

            # Open or close some cells in some directions.
            for x, y, direction, is_open in special_cases:
                if is_open:
                    sub_maze.cell(x, y).open(direction)
                else:
                    sub_maze.cell(x, y).close(direction)

    def cell(self, x, y):
        # type: (int, int) -> Cell

        return self._grid[x][y]

    def export_to_full_grid(self, spaces, walls):
        # type: (Any, Any) -> List[List[int]]

        exported_maze = [[walls for _ in range(self.height() * 2 + 1)] for _ in range(self.width() * 2 + 1)]

        for x in range(self.width()):
            for y in range(self.height()):
                exported_maze[x * 2 + 1][y * 2 + 1] = spaces
                if self.cell(x, y).has_neighbor(Maze.Direction.RIGHT) and self.cell(x, y).is_open(Maze.Direction.RIGHT):
                    exported_maze[x * 2 + 2][y * 2 + 1] = spaces
                if self.cell(x, y).has_neighbor(Maze.Direction.DOWN) and self.cell(x, y).is_open(Maze.Direction.DOWN):
                    exported_maze[x * 2 + 1][y * 2 + 2] = spaces

        return exported_maze

    def export_to_bits(self):
        # type: () -> List[List[int]]

        exported_maze = [[0 for _ in range(self.height())] for _ in range(self.width())]

        for y in range(self.height()):
            for x in range(self.width()):
                if self.cell(x, y).has_neighbor(Maze.Direction.LEFT) and self.cell(x, y).is_open(Maze.Direction.LEFT):
                    exported_maze[x][y] |= 1
                if self.cell(x, y).has_neighbor(Maze.Direction.UP) and self.cell(x, y).is_open(Maze.Direction.UP):
                    exported_maze[x][y] |= 2
                if self.cell(x, y).has_neighbor(Maze.Direction.RIGHT) and self.cell(x, y).is_open(Maze.Direction.RIGHT):
                    exported_maze[x][y] |= 4
                if self.cell(x, y).has_neighbor(Maze.Direction.DOWN) and self.cell(x, y).is_open(Maze.Direction.DOWN):
                    exported_maze[x][y] |= 8

        return exported_maze

    def height(self):
        # type: () -> int

        return self._height

    def width(self):
        # type: () -> int

        return self._width
