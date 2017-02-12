from algorithms import HuntAndKill, RecursiveBackTracker

output_file_name = 'maze.txt'
choice = 3

if choice is 1:
    RecursiveBackTracker.run(100, 100).export(output_file_name)
elif choice is 2:
    HuntAndKill.run(100, 100).export(output_file_name)
else:
    print('You stupid!')
