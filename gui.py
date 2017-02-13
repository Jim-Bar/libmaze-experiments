import pyglet

from maze import Maze

try:
    from typing import Any, Callable, Dict, List, Set, Tuple
except ImportError:
    Any, Callable, Dict, List, Set, Tuple = None, None, None, None, None, None


class Renderer(object):
    """
    Render a maze so that one can solve it!
    """

    @staticmethod
    def render(maze, cells_size):
        # type: (Maze, int) -> None

        window = pyglet.window.Window(fullscreen=True)

        width = maze.width() * 2 + 1
        height = maze.height() * 2 + 1
        drawn_width = width * cells_size
        drawn_height = height * cells_size
        origin_x = window.width // 2 - drawn_width // 2
        origin_y = window.height // 2 - drawn_height // 2
        maze = maze.develop()
        batch = pyglet.graphics.Batch()
        for y in range(height):
            for x in range(width):
                if maze[x][y] is 0:
                    Renderer._add_cell(batch, cells_size, x, y, (255, 255, 255), height, origin_x, origin_y)
                else:
                    Renderer._add_cell(batch, cells_size, x, y, (0, 0, 0), height, origin_x, origin_y)

        @window.event
        def on_draw():
            # type: () -> None

            window.clear()
            batch.draw()

        @window.event
        def on_key_press(symbol, _):
            # type: (Any, Any) -> None

            if symbol == pyglet.window.key.ESCAPE or symbol == pyglet.window.key.Q:
                window.close()

        Renderer._flood(maze, width, height, cells_size, batch, origin_x, origin_y)
        pyglet.app.run()

    @staticmethod
    def _add_cell(batch, size, x, y, color, height, origin_x, origin_y):
        # type: (Any, int, int, int, Tuple[int, int, int], int, int, int) -> None

        # Put the origin to the top left (reverse Y-axis).
        y = height - y
        vertices = tuple(n * size for n in (x, y, x + 1, y, x + 1, y - 1, x, y - 1))
        origin = (origin_x, origin_y, origin_x, origin_y, origin_x, origin_y, origin_x, origin_y)
        vertices = tuple(map(sum, zip(vertices, origin)))

        batch.add(4, pyglet.gl.GL_QUADS, None,
                  ('v2i', vertices), ('c3B', color * 4))

    @staticmethod
    def _flood(maze, width, height, cells_size, batch, origin_x, origin_y):
        # type: (List[List[int]], int, int, int, Any, int, int) -> None

        color = (255, 0, 0)
        cells = [(1, 1)]

        while cells:
            next_cells = list()
            for x, y in cells:
                maze[x][y] = color
                Renderer._add_cell(batch, cells_size, x, y, color, height, origin_x, origin_y)
                if x > 0 and maze[x - 1][y] is 0:
                    next_cells.append((x - 1, y))
                if x < width - 1 and maze[x + 1][y] is 0:
                    next_cells.append((x + 1, y))
                if y > 0 and maze[x][y - 1] is 0:
                    next_cells.append((x, y - 1))
                if y < height -1 and maze[x][y + 1] is 0:
                    next_cells.append((x, y + 1))
            cells = next_cells
            color = Renderer._next_color(color)

    @staticmethod
    def _next_color(color):
        # type: (Tuple[int, int, int]) -> Tuple[int, int, int]

        red, green, blue = color
        if red is 255 and green is 0 and blue < 255:
            return red, green, blue + 1
        if red > 0 and green is 0 and blue is 255:
            return red - 1, green, blue
        if red is 0 and green < 255 and blue is 255:
            return red, green + 1, blue
        if red is 0 and green is 255 and blue > 0:
            return red, green, blue - 1
        if red < 255 and green is 255 and blue is 0:
            return red + 1, green, blue
        if red is 255 and green > 0 and blue is 0:
            return red, green - 1, blue

        raise RuntimeError('Flaws in "_next_color()"')
