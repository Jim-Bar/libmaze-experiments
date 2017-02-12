import random
import sys

from maze import Maze


class Algorithm(object):
    """
    Abstract class. All algorithm must override the methods of this class.
    """

    # TODO: Make a class out of 'parameters'.
    @staticmethod
    def run(width, height, parameters=None):
        # type: (int, int, Any) -> Maze

        raise NotImplementedError('Class {} is abstract'.format(Algorithm.__name__))


class HuntAndKill(Algorithm):
    """
    Variation of the Hunt and Kill algorithm. When a path is complete, instead of looking from the top left for starting
    a new one, start from a random location on the part of the maze already built.
    """

    @staticmethod
    def run(width, height, parameters=None):
        # type: (int, int, Any) -> Maze

        maze = Maze(width, height, True, False)
        sys.setrecursionlimit(max(sys.getrecursionlimit(), width * height + 10))
        starting_cells = set()
        HuntAndKill._recursive(maze.cell(random.randrange(width), random.randrange(height)), starting_cells)
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

        maze = Maze(width, height, True, False)
        cell = maze.cell(0, 0)
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
