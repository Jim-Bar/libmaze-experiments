from algorithms import Braid, HuntAndKill, Labyrinth, Passage, RecursiveBackTracker, Room
from gui import Renderer
from maze import Maze

cells_size = 4
width = ((1920 // cells_size) - 1) // 2
height = ((1080 // cells_size) - 1) // 2
choice = 6

if choice is 1:
    maze = RecursiveBackTracker.run(width, height)
elif choice is 2:
    maze = HuntAndKill.run(width, height)
elif choice is 3:
    maze = Labyrinth.run(width, height)
elif choice is 4:
    maze = Room.run(width, height)
elif choice is 5:
    maze = Passage.run(width, height, [None, (0, 0), (width - 1, height - 1)])
elif choice is 6:
    maze = Braid.run(width, height)
elif choice is 7:
    # 'J'.
    sub_maze_1 = RecursiveBackTracker.run(30, 10), [(0, 0, Maze.Direction.LEFT, True)], (30, 30)
    sub_maze_2 = RecursiveBackTracker.run(10, 30), [(0, 0, Maze.Direction.UP, True)], (40, 40)
    sub_maze_3 = RecursiveBackTracker.run(10, 10), [(9, 9, Maze.Direction.RIGHT, True)], (30, 60)
    # 'i'.
    sub_maze_4 = RecursiveBackTracker.run(10, 10), list(), (70, 30)
    sub_maze_5 = RecursiveBackTracker.run(10, 25), list(), (70, 45)
    # 'M'.
    sub_maze_6 = RecursiveBackTracker.run(30, 10), [(0, 0, Maze.Direction.LEFT, True)], (90, 30)
    sub_maze_7 = RecursiveBackTracker.run(10, 30), [(0, 0, Maze.Direction.UP, True)], (90, 40)
    sub_maze_8 = RecursiveBackTracker.run(10, 30), [(0, 0, Maze.Direction.UP, True)], (110, 40)
    sub_maze_9 = RecursiveBackTracker.run(4, 10), [(0, 0, Maze.Direction.UP, True)], (103, 40)
    # Link 'J' and 'i'.
    sub_maze_10 = Passage.run(10, 10, (None, (0, 0), (9, 0))), [(0, 0, Maze.Direction.LEFT, True), (9, 0, Maze.Direction.RIGHT, True)], (60, 30)
    # Link the dot of the 'i' and the base of the 'i'.
    sub_maze_11 = Passage.run(10, 5, (None, (9, 0), (9, 4))), [(9, 0, Maze.Direction.UP, True), (9, 4, Maze.Direction.DOWN, True)], (70, 40)
    # Link 'i' and 'M'.
    sub_maze_12 = Passage.run(10, 10, (None, (0, 0), (9, 0))), [(0, 0, Maze.Direction.LEFT, True), (9, 0, Maze.Direction.RIGHT, True)], (80, 30)
    maze = Maze(width, height, True, False, [sub_maze_1, sub_maze_2, sub_maze_3, sub_maze_4, sub_maze_5, sub_maze_6, sub_maze_7, sub_maze_8, sub_maze_9, sub_maze_10, sub_maze_11, sub_maze_12])
    maze = RecursiveBackTracker.run(width, height, (maze, (0, 0)))
else:
    raise RuntimeError('You stupid!')

Renderer(maze, cells_size, 1, False, Renderer.ColorTransition.HUE).run()
