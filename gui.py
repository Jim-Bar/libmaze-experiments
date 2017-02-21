import enum
import pyglet
import random

from maze import Maze

try:
    from typing import Any, Callable, Dict, List, Set, Tuple
except ImportError:
    Any, Callable, Dict, List, Set, Tuple = None, None, None, None, None, None


class Renderer(object):
    """
    Render a maze so that one can solve it!
    """

    class ColorTransition(enum.Enum):
        """
        How the colors variate.
        """

        HUE = 1,
        HUE_0_5 = 2,
        HUE_2 = 3,
        HUE_10 = 4,
        RANDOM = 5

    def __init__(self, maze, cells_size, num_initial_cells, color_walls, color_transition):
        # type: (Maze, int, int, bool, Renderer.ColorTransition) -> None

        self._window = pyglet.window.Window(fullscreen=True)  # type: pyglet.window.Window
        self._cells_size = cells_size  # type: int
        self._num_initial_cells = num_initial_cells  # type: int
        self._color_transition = color_transition  # type: Renderer.ColorTransition
        self._width = maze.width() * 2 + 1  # type: int
        self._height = maze.height() * 2 + 1  # type: int
        drawn_width = self._width * cells_size  # type: int
        drawn_height = self._height * cells_size  # type: int
        self._origin = (self._window.width // 2 - drawn_width // 2,
                        self._window.height // 2 - drawn_height // 2)  # type: Tuple[int, int]
        self._batch = pyglet.graphics.Batch()  # type: pyglet.graphics.Batch

        # Color walls or spaces.
        if color_walls:
            walls = 0
            spaces = 1
        else:
            walls = 1
            spaces = 0
        self._maze = maze.export_to_full_grid(spaces, walls)  # type: List[List[int]]

        # Get the list of all the walls.
        self._walls = set()  # type: Set[Tuple[int, int]]
        for y in range(self._height):
            for x in range(self._width):
                if self._maze[x][y] is 0:
                    self._walls.add((x, y))

        # Pick random cells.
        self._frontier = set()  # type: Set[Tuple[int, int]]
        for _ in range(num_initial_cells):
            self._frontier.add((random.randrange(walls, self._width, 2), random.randrange(walls, self._height, 2)))

        # Pick a random color.
        color = [random.randint(0, 255), 0, 255]
        random.shuffle(color)
        self._color = tuple(color)  # type: Tuple[int, int, int]

    def run(self):
        # type: () -> None

        @self._window.event
        def on_draw():
            # type: () -> None

            # TODO: Clear to white or black.
            self._window.clear()
            self._batch.draw()

        @self._window.event
        def on_key_press(symbol, _):
            # type: (Any, Any) -> None

            if symbol == pyglet.window.key.ESCAPE or symbol == pyglet.window.key.Q:
                self._window.close()

        pyglet.clock.schedule_interval(self._flood, 1 / 60)
        pyglet.app.run()

    def _add_cell(self, x, y):
        # type: (int, int) -> None

        # TODO: Use Pyglet's origin instead of changing it.
        # Put the origin to the top left (reverse Y-axis).
        y = self._height - y
        vertices = tuple(n * self._cells_size for n in (x, y, x + 1, y, x + 1, y - 1, x, y - 1))
        origin = (self._origin[0], self._origin[1], self._origin[0], self._origin[1], self._origin[0], self._origin[1],
                  self._origin[0], self._origin[1])
        vertices = tuple(map(sum, zip(vertices, origin)))

        self._batch.add(4, pyglet.gl.GL_QUADS, None, ('v2i', vertices), ('c3B', self._color * 4))

    def _flood(self, _):
        # type: (float) -> None

        if self._frontier:
            next_cells = set()
            for x, y in self._frontier:
                self._maze[x][y] = 1
                self._walls.remove((x, y))
                self._add_cell(x, y)
                if x > 0 and self._maze[x - 1][y] is 0:
                    next_cells.add((x - 1, y))
                if x < self._width - 1 and self._maze[x + 1][y] is 0:
                    next_cells.add((x + 1, y))
                if y > 0 and self._maze[x][y - 1] is 0:
                    next_cells.add((x, y - 1))
                if y < self._height - 1 and self._maze[x][y + 1] is 0:
                    next_cells.add((x, y + 1))
            self._frontier = next_cells - self._frontier  # Do not add the cells that have been already dealt with.
            self._next_color()
        else:
            if self._walls:  # If there are still cells left (isolated areas), start a new frontier.
                while len(self._frontier) < min(self._num_initial_cells, len(self._walls)):
                    self._frontier.add(random.choice(tuple(self._walls)))
            else:
                pyglet.clock.unschedule(self._flood)

    def _next_color(self):
        # type: () -> None

        if self._color_transition in {Renderer.ColorTransition.HUE, Renderer.ColorTransition.HUE_0_5,
                                      Renderer.ColorTransition.HUE_2, Renderer.ColorTransition.HUE_10}:
            if self._color_transition is Renderer.ColorTransition.HUE_0_5 and random.randint(0, 1) is 0:
                return  # Average is one of two.

            if self._color_transition is Renderer.ColorTransition.HUE_10:
                num_iterations = 10
            elif self._color_transition is Renderer.ColorTransition.HUE_2:
                num_iterations = 2
            else:
                num_iterations = 1

            for _ in range(0, num_iterations):
                red, green, blue = self._color
                if red is 255 and green is 0 and blue < 255:
                    self._color = red, green, blue + 1
                elif red > 0 and green is 0 and blue is 255:
                    self._color = red - 1, green, blue
                elif red is 0 and green < 255 and blue is 255:
                    self._color = red, green + 1, blue
                elif red is 0 and green is 255 and blue > 0:
                    self._color = red, green, blue - 1
                elif red < 255 and green is 255 and blue is 0:
                    self._color = red + 1, green, blue
                elif red is 255 and green > 0 and blue is 0:
                    self._color = red, green - 1, blue
                else:
                    raise RuntimeError('Invalid color ({}, {}, {}). RGB == {{0, 255, n}}'.format(red, green, blue))
        elif self._color_transition is Renderer.ColorTransition.RANDOM:
            self._color = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        else:
            raise RuntimeError('Invalid color transition {}'.format(self._color_transition))
