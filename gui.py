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

        @window.event
        def on_draw():
            # type: () -> None

            window.clear()
            batch = pyglet.graphics.Batch()
            for y in range(height):
                for x in range(width):
                    if maze[x][y] is 0:
                        Renderer._add_cell(batch, cells_size, x, y, (255, 255, 255), height, origin_x, origin_y)
                    else:
                        Renderer._add_cell(batch, cells_size, x, y, (0, 0, 0), height, origin_x, origin_y)
            batch.draw()

        @window.event
        def on_key_press(symbol, _):
            # type: (Any, Any) -> None

            if symbol == pyglet.window.key.ESCAPE or symbol == pyglet.window.key.Q:
                window.close()

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
