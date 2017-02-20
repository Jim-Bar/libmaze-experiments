import random
import sys

from maze import Maze

try:
    from typing import Any, Callable, Dict, List, Set, Tuple
except ImportError:
    Any, Callable, Dict, List, Set, Tuple = None, None, None, None, None, None


class Algorithm(object):
    """
    Abstract class. All algorithm must override the methods of this class.
    """

    # TODO: Make a class out of 'parameters'. Note: parameter = (maze, (start_x, start_y))
    @staticmethod
    def run(width, height, parameters=None):
        # type: (int, int, Any) -> Maze

        raise NotImplementedError('Class {} is abstract'.format(Algorithm.__name__))


class Braid(object):
    """
    A maze with no dead ends. An algorithm is provided to generate an first maze whose dead ends will be removed. If no
    algorithm is provided, it defaults to RecursiveBackTracker.
    """

    @staticmethod
    def run(width, height, parameters=None):
        # type: (int, int, Any) -> Maze

        # TODO: Parameters here are special: (maze, (start_x, start_y), maze_algorithm)
        # TODO: Do not erase sub mazes?
        if parameters:
            maze_algorithm = parameters[2]
        else:
            maze_algorithm = RecursiveBackTracker

        maze = maze_algorithm.run(width, height, parameters)

        # Reset all the cells as unvisited.
        for y in range(height):
            for x in range(width):
                maze.cell(x, y).set_meta(False)

        frontier = {maze.cell(0, 0)}
        while frontier:
            current_cell = frontier.pop()
            current_cell.set_meta(True)

            connected_directions = set()
            for direction in Maze.Direction:
                if current_cell.has_neighbor(direction) and current_cell.is_open(direction):
                    connected_directions.add(direction)

            # If the current cell is a dead end or is completely closed, make a new passage.
            if len(connected_directions) <= 1:
                other_directions = set(Maze.Direction)
                if len(connected_directions) == 1:  # Prefer the facing direction.
                    opened_direction = connected_directions.pop()
                    carve_direction = opened_direction.opposite()
                    other_directions.remove(opened_direction)
                    other_directions.remove(carve_direction)
                else:
                    carve_direction = random.choice(other_directions)
                    other_directions.remove(carve_direction)
                while not current_cell.has_neighbor(carve_direction):
                    carve_direction = random.choice(list(other_directions))
                    other_directions.remove(carve_direction)

                current_cell.open(carve_direction)

            for direction in Maze.Direction:
                if current_cell.has_neighbor(direction) and not current_cell.get_neighbor(direction).get_meta():
                    frontier.add(current_cell.get_neighbor(direction))

        return maze


class HuntAndKill(Algorithm):
    """
    Variation of the Hunt and Kill algorithm. When a path is complete, instead of looking from the top left for starting
    a new one, start from a random location on the part of the maze already built.
    """

    @staticmethod
    def run(width, height, parameters=None):
        # type: (int, int, Any) -> Maze

        sys.setrecursionlimit(max(sys.getrecursionlimit(), width * height + 10))

        if parameters:
            maze = parameters[0]
            initial_cell = maze.cell(parameters[1][0], parameters[1][1])
        else:
            maze = Maze(width, height, True, False)
            initial_cell = maze.cell(random.randrange(width), random.randrange(height))

        starting_cells = set()
        HuntAndKill._recursive(initial_cell, starting_cells)
        while starting_cells:
            next_cell = starting_cells.pop()
            HuntAndKill._recursive(next_cell, starting_cells)

        return maze

    @staticmethod
    def _recursive(cell, starting_cells):
        # type: (Cell, Set[Cell]) -> None

        cell.set_meta(True)
        starting_cells.add(cell)
        directions = [direction for direction in Maze.Direction]
        random.shuffle(directions)
        for direction in directions:
            if cell.has_neighbor(direction) and not cell.get_neighbor(direction).get_meta():
                cell.open(direction)
                HuntAndKill._recursive(cell.get_neighbor(direction), starting_cells)
                return
        starting_cells.remove(cell)


class Labyrinth(Algorithm):
    """
    Create a long single path which fills all the space.
    """

    @staticmethod
    def run(width, height, parameters=None):
        # type: (int, int, Any) -> Maze

        if parameters:
            maze = parameters[0]
            initial_cell = maze.cell(parameters[1][0], parameters[1][1])
        else:
            maze = Maze(width, height, True, False)
            initial_cell = maze.cell(random.randrange(width), random.randrange(height))

        cell = initial_cell
        cell.set_meta(True)
        done = False
        while not done:
            done = True
            for direction in Maze.Direction:
                if cell.has_neighbor(direction) and not cell.get_neighbor(direction).get_meta():
                    cell.open(direction)
                    cell = cell.get_neighbor(direction)
                    cell.set_meta(True)
                    done = False
                    break

        return maze


class Passage(Algorithm):
    """
    Make a passage between two points.
    """

    @staticmethod
    def run(width, height, parameters=None):
        # type: (int, int, Any) -> Maze

        if not parameters:
            raise RuntimeError('{} needs two points'.format(Passage.__name__))

        maze = Maze(width, height, True, False)

        # TODO: Parameters here are special: (maze, (start_x, start_y), (end_x, end_y))
        start_cell = maze.cell(parameters[1][0], parameters[1][1])
        end_cell = maze.cell(parameters[2][0], parameters[2][1])

        directions = set()
        if start_cell.x() < end_cell.x():
            directions.add(Maze.Direction.RIGHT)
        elif start_cell.x() > end_cell.x():
            directions.add(Maze.Direction.LEFT)
        if start_cell.y() < end_cell.y():
            directions.add(Maze.Direction.DOWN)
        elif start_cell.y() > end_cell.y():
            directions.add(Maze.Direction.UP)
        current_cell = start_cell
        current_cell.set_meta(True)

        while current_cell is not end_cell:
            # TODO: Respect the ratio when drawing random direction.
            direction = random.choice(tuple(directions))
            if current_cell.has_neighbor(direction):
                current_cell.open(direction)
                current_cell = current_cell.get_neighbor(direction)
                current_cell.set_meta(True)
            else:
                directions.remove(direction)

        return maze


class RecursiveBackTracker(Algorithm):
    """
    The original Recursive Back Tracker algorithm.
    """

    @staticmethod
    def run(width, height, parameters=None):
        # type: (int, int, Any) -> Maze

        sys.setrecursionlimit(max(sys.getrecursionlimit(), width * height + 10))

        if parameters:
            maze = parameters[0]
            initial_cell = maze.cell(parameters[1][0], parameters[1][1])
        else:
            maze = Maze(width, height, True, False)
            initial_cell = maze.cell(random.randrange(width), random.randrange(height))

        RecursiveBackTracker._recursive(initial_cell)

        return maze

    @staticmethod
    def _recursive(cell):
        # type: (Cell) -> None

        cell.set_meta(True)
        directions = [direction for direction in Maze.Direction]
        random.shuffle(directions)
        for direction in directions:
            if cell.has_neighbor(direction) and not cell.get_neighbor(direction).get_meta():
                cell.open(direction)
                RecursiveBackTracker._recursive(cell.get_neighbor(direction))


class Room(Algorithm):
    """
    An empty maze, no walls excepted the surrounding walls (and maybe the pillars depending on the rendering engine).
    """

    @staticmethod
    def run(width, height, parameters=None):
        # type: (int, int, Any) -> Maze

        return Maze(width, height, False, True)
