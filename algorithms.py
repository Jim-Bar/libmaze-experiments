import random
import sys

from maze import Cell, Maze

try:
    from typing import Any, Callable, Dict, List, Set, Tuple, Union
except ImportError:
    Any, Callable, Dict, List, Set, Tuple, Union = None, None, None, None, None, None, None


# FIXME: Write a RandomSet class (pop fully random)?

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

    This algorithm can also be used to make partial braid mazes. The percentage of the dead ends that will be removed
    can be provided.
    """

    @staticmethod
    def run(width, height, parameters=None):
        # type: (int, int, Any) -> Maze

        # TODO: Parameters here are special: (maze, (start_x, start_y), maze_algorithm, percentage)
        # TODO: Do not erase sub mazes? Start?
        if parameters:
            maze_algorithm = parameters[2]
            percentage = parameters[3]  # FIXME: Name?
        else:
            maze_algorithm = RecursiveBackTracker
            percentage = 1

        maze = maze_algorithm.run(width, height)

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
            if len(connected_directions) <= 1 and random.random() <= percentage:
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


class Frontier(Algorithm):
    """
    Randomly flood the space.

    Note that this algorithm can add patches of cells to sub-mazes or neighboring mazes. That is due to the cells in the
    tank which are connected to cells which have already been visited (but sometimes by other algorithms/mazes).
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

        initial_cell.set_meta(True)
        frontier = [initial_cell]
        tank = set()

        while tank or frontier:
            # As some directions are ignored, some cells could have been visited but are not. And because some
            # directions are ignored, not all the space is visited. The tank is the list of cells that could have been
            # visited but have been ignored. Some of them have actually been visited by another path, so those are
            # removed.
            while not frontier and tank:
                cell = tank.pop()
                if not cell.get_meta():
                    # Connect to a random direction that have already been visited.
                    directions = [direction for direction in Maze.Direction]
                    random.shuffle(directions)
                    while directions and not cell.get_meta():
                        direction = directions.pop()
                        if cell.has_neighbor(direction) and cell.get_neighbor(direction).get_meta():
                            cell.open(direction)
                            cell.set_meta(True)
                            frontier.append(cell)

            new_frontier = list()
            while frontier:
                # Randomly choose a cell from the frontier.
                cell = random.choice(frontier)
                frontier.remove(cell)

                # Randomly choose directions to explore.
                directions = [direction for direction in Maze.Direction]
                random.shuffle(directions)
                num_directions = random.randint(0, 4)
                directions = directions[:num_directions]

                for direction in directions:
                    if cell.has_neighbor(direction) and not cell.get_neighbor(direction).get_meta():
                        cell.open(direction)
                        cell.get_neighbor(direction).set_meta(True)
                        new_frontier.append(cell.get_neighbor(direction))

                for direction in Maze.Direction:
                    if direction not in directions and cell.has_neighbor(direction) and not cell.get_neighbor(direction).get_meta():
                        tank.add(cell.get_neighbor(direction))
            frontier = new_frontier

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


class Labyrinth2(Algorithm):
    """
    Create a long single path which fills all the space.
    """

    class Expansion(object):
        """
        TODO

        If :meth:`is_possible` returns ``False``, the behaviour of all other methods is undefined. They must not be
        called in that case.
        """

        def __init__(self, origin_cell, direction, perpendicular_direction):
            # type: (Cell, Maze.Direction, Maze.Direction) -> None

            self._direction = direction  # type: Maze.Direction
            self._origin = origin_cell  # type: Cell
            self._origin_expanded = None  # type: Union[Cell, None]
            self._paired = None  # type: Union[Cell, None]
            self._paired_expanded = None  # type: Union[Cell, None]
            self._perpendicular = perpendicular_direction  # type: Maze.Direction
            self._is_possible = self._resolve()  # type: bool

        def do_expansion(self):
            # type: () -> None

            self._origin.close(self._direction)
            self._origin.open(self._perpendicular)
            self._paired.open(self._perpendicular)
            self._origin_expanded.open(self._direction)
            self._origin_expanded.set_meta(True)
            self._paired_expanded.set_meta(True)

        def get_cells(self):
            # type: () -> Set[Cell]

            return {self._origin, self._paired, self._origin_expanded, self._paired_expanded}

        def is_possible(self):
            # type: () -> bool

            return self._is_possible

        def _resolve(self):
            # type: () -> bool

            # Select paired cell.
            if self._origin.has_neighbor(self._direction) and self._origin.get_neighbor(self._direction).get_meta() and self._origin.is_open(self._direction):
                self._paired = self._origin.get_neighbor(self._direction)
            else:
                return False

            # Select first expansion cell.
            if self._origin.has_neighbor(self._perpendicular) and not self._origin.get_neighbor(self._perpendicular).get_meta():
                self._origin_expanded = self._origin.get_neighbor(self._perpendicular)
            else:
                return False

            # Select second expansion cell.
            if self._paired.has_neighbor(self._perpendicular) and not self._paired.get_neighbor(self._perpendicular).get_meta():
                self._paired_expanded = self._paired.get_neighbor(self._perpendicular)
            else:
                return False
            """
            # Check that the expanded cells are at even distance from the edges or cells of the paths.
            is_even = Labyrinth2._is_even(self._origin_expanded, self._direction.opposite()) and Labyrinth2._is_even(self._paired_expanded, self._direction)

            # Check that in the direction of the expansion, the counts are either all evens or all odds.
            evens_or_odds = Labyrinth2._is_even(self._origin_expanded, self._perpendicular) is Labyrinth2._is_even(self._paired_expanded, self._perpendicular)

            # Check if the expansion is stuck again a wall.
            is_stuck_origin = Labyrinth2._is_zero(self._origin_expanded, self._direction.opposite())
            is_stuck_paired = Labyrinth2._is_zero(self._paired_expanded, self._direction)
            is_stuck = is_stuck_origin or is_stuck_paired

            # Check if the expansion is surrounded (stuck from both sides).
            is_surrounded = is_stuck_origin and is_stuck_paired

            return ((is_even or is_stuck) and evens_or_odds) or is_surrounded
            """
            # Check if the expansion is surrounded (stuck from both sides).
            if Labyrinth2._is_zero(self._origin_expanded, self._direction.opposite()) and Labyrinth2._is_zero(self._paired_expanded, self._direction):
                return True

            # In the direction of the expansion, it is fine if the expansion completely shuts off a corridor and goes along a wall.
            if Labyrinth2._is_zero(self._origin_expanded, self._perpendicular) and Labyrinth2._is_zero(self._paired_expanded, self._perpendicular) \
                    and (Labyrinth2._is_zero(self._origin_expanded, self._direction.opposite() or Labyrinth2._is_zero(self._paired_expanded, self._direction))):
                return True

            # Check that the expanded cells are at even distance from the edges or cells of the paths.
            if not Labyrinth2._is_even(self._origin_expanded, self._direction.opposite()):
                return False
            if not Labyrinth2._is_even(self._paired_expanded, self._direction):
                return False

            # Check that in the direction of the expansion, the counts are either all evens or all odds.
            if Labyrinth2._is_even(self._origin_expanded, self._perpendicular) is not Labyrinth2._is_even(self._paired_expanded, self._perpendicular):
                return False

            return True

        @staticmethod
        def _distance_one(cell, direction):
            # type: (Cell, Maze.Direction) -> bool

            if not cell.has_neighbor(direction):
                return False

            neighbor = cell.get_neighbor(direction)
            if neighbor.get_meta():
                return False

            return not neighbor.has_neighbor(direction) or neighbor.get_neighbor(direction).get_meta()

    @staticmethod
    def run(width, height, parameters=None):
        # type: (int, int, Any) -> Maze

        # FIXME: support that. Plus, only even dimensions are supported.
        if parameters:
            raise RuntimeError('parameters not supported')

        maze = Maze(width, height, True, False)
        initial_cell = maze.cell(0, 0)

        try:
            frontier = Labyrinth2._initial_path(initial_cell)
            tank = set()
            while frontier or tank:
                if not frontier:
                    frontier.update(tank)
                    tank.clear()
                random_cell = random.choice(list(frontier))
                expansion = Labyrinth2._find_expansion(random_cell)
                if expansion:
                    expansion.do_expansion()
                    for cell in expansion.get_cells():
                        if Labyrinth2._is_frontier(cell):
                            frontier.add(cell)
                        else:
                            frontier.discard(cell)
                else:
                    frontier.discard(random_cell)
                    if Labyrinth2._is_frontier(random_cell):
                        tank.add(random_cell)
        except KeyboardInterrupt:
            return maze, False

        return maze, True

    @staticmethod
    def _initial_path(cell):
        # type: (Cell) -> Set[Cell]

        directions = set()
        for direction in Maze.Direction:
            if cell.has_neighbor(direction):
                directions.add(direction)

        direction = random.choice(list(directions))
        frontier = {cell}
        cell.set_meta(True)
        while cell.has_neighbor(direction):
            cell.open(direction)
            cell = cell.get_neighbor(direction)
            cell.set_meta(True)
            frontier.add(cell)

        return frontier

    @staticmethod
    def _is_even(cell, direction):
        # type: (Cell, Maze.Direction) -> bool

        count = 0
        while cell.has_neighbor(direction) and not cell.get_neighbor(direction).get_meta():
            count += 1
            cell = cell.get_neighbor(direction)

        return count % 2 is 0

    @staticmethod
    def _is_frontier(cell):
        # type: (Cell) -> bool

        for direction in Maze.Direction:
            if cell.has_neighbor(direction) and not cell.get_neighbor(direction).get_meta():
                return True

        return False

    @staticmethod
    def _is_zero(cell, direction):
        # type: (Cell, Maze.Direction) -> bool

        if not cell.has_neighbor(direction):
            return True

        return cell.get_neighbor(direction).get_meta()

    @staticmethod
    def _find_expansion(cell):
        # type: (Cell) -> Union[Labyrinth2.Expansion, None]

        # Return the first expansion found. Lookup directions in a randomized order.
        for direction in Maze.Direction.shuffle():  # TODO: Add a random() method to Maze.Direction returning an randomly ordered set.
            for perpendicular_direction in direction.perpendiculars():
                expansion = Labyrinth2.Expansion(cell, direction, perpendicular_direction)
                if expansion.is_possible():
                    return expansion

        return None


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


class RecursiveBackTracker2(Algorithm):
    """
    Variation of the Recursive Back Tracker algorithm which occupies half of the grid. It is "even".

    TODO: Achieve the same thing with a regular Recursive Back Tracker algorithm and a smart grid/maze which handles
    TODO: the "even" distribution itself. Algorithms could be combined.

    This algorithm is a basis for the generation of labyrinths.
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

        RecursiveBackTracker2._recursive(initial_cell, None, 0)

        return maze

    @staticmethod
    def _recursive(cell, last_direction, count_since_last_turn):
        # type: (Cell, Union[Maze.Direction, None], int) -> None

        cell.set_meta(True)
        if count_since_last_turn % 2 is 0:
            directions = [direction for direction in Maze.Direction]
            random.shuffle(directions)
        else:
            directions = {last_direction}
        for direction in directions:
            if cell.has_neighbor(direction) and not cell.get_neighbor(direction).get_meta():
                neighbor = cell.get_neighbor(direction)
                for neighbor_direction in direction.opposite().others():
                    if neighbor.has_neighbor(neighbor_direction) and neighbor.get_neighbor(neighbor_direction).get_meta():
                        break
                else:
                    cell.open(direction)
                    RecursiveBackTracker2._recursive(cell.get_neighbor(direction), direction, count_since_last_turn + 1)


class Room(Algorithm):
    """
    An empty maze, no walls excepted the surrounding walls (and maybe the pillars depending on the rendering engine).
    """

    @staticmethod
    def run(width, height, parameters=None):
        # type: (int, int, Any) -> Maze

        return Maze(width, height, False, True)


class Spiral(Algorithm):
    """
    A spiral with one, two, three or four exits. The spiral can be rectangular and the positions of the exits can be
    chosen.
    """
    # TODO: Improve, 13x14 not well supported, 2 or 3 exits not well supported.

    @staticmethod
    def run(width, height, parameters=None):
        # type: (int, int, Any) -> Maze

        if not parameters:
            raise RuntimeError('{} needs positions of the exits'.format(Passage.__name__))

        maze = Maze(width, height, True, False)

        # TODO: Parameters here are special: (maze, [(exit1_x, exit1_y), (exit2_x, exit2_y), ...], is_clockwise)
        exits = parameters[1]
        is_clockwise = parameters[2]

        if is_clockwise:
            directions = [Maze.Direction.LEFT, Maze.Direction.UP, Maze.Direction.RIGHT, Maze.Direction.DOWN]
        else:
            directions = [Maze.Direction.LEFT, Maze.Direction.DOWN, Maze.Direction.RIGHT, Maze.Direction.UP]

        # Heads of the passages, with the directions: (x, y, direction_index).
        front_cells = list()

        # Find the directions of the initial front cells.
        for exit_x, exit_y in exits:
            if exit_x is 0 and exit_y is 0:
                if is_clockwise:
                    front_cells.append((exit_x, exit_y, 2))
                else:
                    front_cells.append((exit_x, exit_y, 1))
            elif exit_x is 0 and exit_y is height - 1:
                if is_clockwise:
                    front_cells.append((exit_x, exit_y, 1))
                else:
                    front_cells.append((exit_x, exit_y, 2))
            elif exit_x is width - 1 and exit_y is height - 1:
                if is_clockwise:
                    front_cells.append((exit_x, exit_y, 0))
                else:
                    front_cells.append((exit_x, exit_y, 3))
            elif exit_x is width - 1 and exit_y is 0:
                if is_clockwise:
                    front_cells.append((exit_x, exit_y, 3))
                else:
                    front_cells.append((exit_x, exit_y, 0))
            else:
                raise RuntimeError('Invalid exit position (must be a corner): ({}, {})'.format(exit_x, exit_y))
            maze.cell(exit_x, exit_y).set_meta(True)

        while front_cells:
            new_front_cells = list()
            for x, y, direction_index in front_cells:
                cell = maze.cell(x, y)
                # If the passage can continue forward, just continue.
                if cell.has_neighbor(directions[direction_index]) and \
                        not cell.get_neighbor(directions[direction_index]).get_meta():
                    cell.open(directions[direction_index])
                    cell.get_neighbor(directions[direction_index]).set_meta(True)
                    new_x = cell.get_neighbor(directions[direction_index]).x()
                    new_y = cell.get_neighbor(directions[direction_index]).y()
                    new_front_cells.append((new_x, new_y, direction_index))
                # Otherwise, turn if there are still available direction.
                # TODO: Don't do it more than once? Could fix some bad behavior (e.g. 13x14, ...).
                elif True in [cell.has_neighbor(direction) and not cell.get_neighbor(direction).get_meta()
                              for direction in directions]:
                    new_front_cells.append((x, y, (direction_index + 1) % len(directions)))
                # Otherwise, join other passages excepted if there is only one passage.
                elif len(exits) > 1:
                    cell.open(directions[direction_index])
            front_cells = new_front_cells

        return maze
