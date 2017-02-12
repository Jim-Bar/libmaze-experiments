from algorithms import HuntAndKill, Labyrinth, RecursiveBackTracker, Room
from maze import Maze

output_file_name = 'maze.txt'
width = 100
height = width
choice = 5

if choice is 1:
    RecursiveBackTracker.run(width, height).export(output_file_name)
elif choice is 2:
    HuntAndKill.run(width, height).export(output_file_name)
elif choice is 3:
    Labyrinth.run(width, height).export(output_file_name)
elif choice is 4:
    Room.run(width, height).export(output_file_name)
elif choice is 5:
    sub_maze_1 = Labyrinth.run(20, 20), [(0, 0, Maze.Direction.LEFT, True)], (40, 40)
    sub_maze_2 = Room.run(10, 10), [(0, 0, Maze.Direction.LEFT, True)], (10, 10)
    maze = Maze(width, height, True, False, [sub_maze_1, sub_maze_2])
    RecursiveBackTracker.run(width, height, (maze, (0, 0))).export(output_file_name)
else:
    print('You stupid!')
