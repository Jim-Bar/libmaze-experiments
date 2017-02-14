from algorithms import HuntAndKill, Labyrinth, RecursiveBackTracker, Room
from gui import Renderer
from maze import Maze

output_file_name = 'maze.txt'
width = 239
height = 134
choice = 5

if choice is 1:
    maze = RecursiveBackTracker.run(width, height)
elif choice is 2:
    maze = HuntAndKill.run(width, height)
elif choice is 3:
    maze = Labyrinth.run(width, height)
elif choice is 4:
    maze = Room.run(width, height)
elif choice is 5:
    # 'J'.
    sub_maze_1 = RecursiveBackTracker.run(30, 10), [(0, 0, Maze.Direction.LEFT, True)], (30, 30)
    sub_maze_2 = RecursiveBackTracker.run(10, 30), [(0, 0, Maze.Direction.UP, True)], (40, 40)
    sub_maze_3 = RecursiveBackTracker.run(10, 10), [(9, 9, Maze.Direction.RIGHT, True)], (30, 60)
    # 'i'.
    sub_maze_4 = RecursiveBackTracker.run(10, 10), [(0, 0, Maze.Direction.LEFT, True)], (70, 30)
    sub_maze_5 = RecursiveBackTracker.run(10, 25), [(0, 0, Maze.Direction.LEFT, True)], (70, 45)
    # 'M'.
    sub_maze_6 = RecursiveBackTracker.run(30, 10), [(0, 0, Maze.Direction.LEFT, True)], (90, 30)
    sub_maze_7 = RecursiveBackTracker.run(10, 30), [(0, 0, Maze.Direction.UP, True)], (90, 40)
    sub_maze_8 = RecursiveBackTracker.run(10, 30), [(0, 0, Maze.Direction.UP, True)], (110, 40)
    sub_maze_9 = RecursiveBackTracker.run(4, 10), [(0, 0, Maze.Direction.UP, True)], (103, 40)
    maze = Maze(width, height, True, False, [sub_maze_1, sub_maze_2, sub_maze_3, sub_maze_4, sub_maze_5, sub_maze_6, sub_maze_7, sub_maze_8, sub_maze_9])
    maze = RecursiveBackTracker.run(width, height, (maze, (0, 0)))
else:
    raise RuntimeError('You stupid!')

Renderer(maze, 4, 4, True).run()
