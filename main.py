from algorithms import RecursiveBackTracker, HuntAndKill

choice = 1

if choice is 1:
    RecursiveBackTracker.run(100, 100).export('maze.txt')
elif choice is 2:
    HuntAndKill.run(100, 100).export('maze.txt')
else:
    print('You stupid!')
