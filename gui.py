import Image # Python Imaging Library (PIL)

input_file_name = 'maze.txt'

with open(input_file_name) as input_file:
    maze_raw = input_file.readlines()

maze_raw = [[int(cell) for cell in row.split()] for row in maze_raw]

width = len(maze_raw[0])
height = len(maze_raw)

maze = [[1 for x in range(width * 2 + 1)] for y in range(height * 2 + 1)]

for x in range(width):
    for y in range(height):
        maze[x * 2 + 1][y * 2 + 1] = 0
        if maze_raw[x][y] & 8 is not 0:
            maze[x * 2 + 2][y * 2 + 1] = 0
        if maze_raw[x][y] & 4 is not 0:
            maze[x * 2 + 1][y * 2 + 2] = 0


def print_maze():
    for x in range(width * 2 + 1):
        for y in range(height * 2 + 1):
            #print('{} '.format(' ' if maze[x][y] is 0 else 'O'), end='')
            pass
        print('')


def fill_with_color(pixels, average_color, i, j, w, h):
    for x in range(i, i + w):
        for y in range(j, j + h):
            pixels[x, y] = average_color

width = width * 2 + 1
height = height * 2 + 1

square_size = 5
img_dst = Image.new('RGB', (width * square_size, height * square_size))
pixels_dst = img_dst.load()

for i in range(width):
    for j in range(height):
        if maze[i][j] is 0:
            fill_with_color(pixels_dst, (255, 255, 255), i * square_size, j * square_size, square_size, square_size)
        else:
            fill_with_color(pixels_dst, (128, 128, 128), i * square_size, j * square_size, square_size, square_size)

img_dst.show()
