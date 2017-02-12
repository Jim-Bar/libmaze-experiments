import random
import sys

from maze import Maze


class Algorithm(object):
    """
    Abstract class. All algorithm must override the methods of this class.
    """

    @staticmethod
    def run(width, height):
        # type: (int, int) -> Maze

        raise TypeError('Class {} is abstract'.format(Algorithm.__name__))


class HuntAndKill(Algorithm):
    """
    Variation of the Hunt and Kill algorithm. When a path is complete, instead of looking for starting a new one from
    the top left, start from a random location on the part of the maze already built.
    """

    @staticmethod
    def run(width, height):
        # type: (int, int) -> Maze

        maze = Maze(width, height, True, False)
        sys.setrecursionlimit(width * height + 10)
        starting_cells = set()
        HuntAndKill._recursive(maze.cell(width // 2, height // 2), starting_cells)
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


class RecursiveBackTracker(Algorithm):
    """
    The original Recursive Back Tracker algorithm.
    """

    @staticmethod
    def run(width, height):
        # type: (int, int) -> Maze

        maze = Maze(width, height, True, False)
        sys.setrecursionlimit(width * height + 10)
        RecursiveBackTracker._recursive(maze.cell(width // 2, height // 2))

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
