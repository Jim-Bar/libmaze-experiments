#include <stdio.h>
#include <stdlib.h>
#include <time.h>

typedef enum Direction Direction;
enum Direction
{
  NONE = 0,
  LEFT = 1,
  TOP = LEFT << 1,
  RIGHT = TOP << 1,
  BOTTOM = RIGHT << 1
};

Direction const DIRECTIONS[4] = { LEFT, TOP, RIGHT, BOTTOM };

/*
 * Return a non null integer if the provided square is connected to its neighbor
 * for this direction.
 */
#define OPENED_LEFT(square) square & LEFT
#define OPENED_TOP(square) square & TOP
#define OPENED_RIGHT(square) square & RIGHT
#define OPENED_BOTTOM(square) square & BOTTOM

/* Connect the provided square to its neighbor for this direction. */
#define OPEN_DIRECTION(square, direction) square | direction

typedef struct Maze Maze;
struct Maze
{
  int width;
  int height;
  int size;

  int *squares;
  int *permutation;
};

int coordinates_to_square_index(Maze const *const maze, int const x,
                                int const y);
Maze* create_maze(int const width, int const height);
void destroy_maze(Maze *maze);
Direction draw_direction(Direction availableDirections[]);
int get_neighbor_index(Maze const *const maze, int const square_index,
                       Direction const direction);
Direction get_reverse_direction(Direction const direction);
char has_neighbor(Maze const *const maze, int const square_index,
                  Direction direction);
char has_neighbor_available(Maze const *const maze, int const square_index,
                            Direction direction);
void print_maze(Maze const *const maze, FILE *const file);
void shuffle(int *const array, size_t const size);
void square_index_to_coordinates(Maze const *const maze, int const square_index,
                                 int *const x, int *const y);
int main(int argc, char *argv[])
{
  int width = 0, height = 0;
  Maze *maze = NULL;
  char const outputFileName[] = "maze.txt";
  FILE *outputFile = NULL;

  if (argc != 3)
  {
    fprintf(stderr, "Usage: %s WIDTH HEIGHT\n", argv[0]);
    return EXIT_FAILURE;
  }

  width = atoi(argv[1]);
  height = atoi(argv[2]);

  if (width <= 0 || height <= 0)
  {
    fprintf(stderr, "Invalid width or height\n");
    return EXIT_FAILURE;
  }

  outputFile = fopen(outputFileName, "w+");
  if (outputFile == NULL)
  {
    fprintf(stderr, "Could not open %s\n", outputFileName);
    return EXIT_FAILURE;
  }

  srand((unsigned int) time(NULL));

  maze = create_maze(width, height);
  print_maze(maze, outputFile);
  destroy_maze(maze);

  return EXIT_SUCCESS;
}

Maze* create_maze(int const width, int const height)
{
  char blocked = 0;
  int i = 0, j = 0, squareIndex = 0, neighborIndex = 0;
  Maze *maze = NULL;
  Direction availableDirections[4] = { NONE, NONE, NONE, NONE };
  Direction drewDirection = NONE, reverseDirection = NONE;

  maze = malloc(sizeof(Maze));
  if (maze == NULL)
  {
    fprintf(stderr, "Could not allocate maze\n");
    return NULL;
  }

  maze->width = width;
  maze->height = height;
  maze->size = width * height;

  maze->squares = malloc(maze->size * sizeof(int));
  if (maze->squares == NULL)
  {
    fprintf(stderr, "Could not allocate maze->squares\n");
    free(maze);
    return NULL;
  }

  maze->permutation = malloc(maze->size * sizeof(int));
  if (maze->permutation == NULL)
  {
    fprintf(stderr, "Could not allocate maze->permutation\n");
    free(maze->squares);
    free(maze);
    return NULL;
  }

  /* Generate the permutation and initialize the maze to zero. */
  for (i = 0; i < maze->size; i++)
  {
    maze->permutation[i] = i;
    maze->squares[i] = 0;
  }
  shuffle(maze->permutation, (size_t) maze->size);

  /* Generate maze. */
  for (i = 0; i < maze->size; i++)
  {
    squareIndex = *(maze->permutation + i);
    if (*(maze->squares + squareIndex) == NONE)
    {
      blocked = 0;
      while (!blocked) {
        /* Find available directions. */
        blocked = 1;
        for (j = 0; j < 4; j++)
          if (has_neighbor_available(maze, squareIndex, DIRECTIONS[j]))
          {
            availableDirections[j] = DIRECTIONS[j];
            blocked = 0;
          }
          else
            availableDirections[j] = NONE;

        /*
         * If there is no available direction, the path is blocked. In this case
         * choose an arbitrary neighbor (still check for world's edges) for
         * connecting to it and ending the path.
         */
        if (blocked)
          for (j = 0; j < 4; j++)
            if (has_neighbor(maze, squareIndex, DIRECTIONS[j]))
              availableDirections[j] = DIRECTIONS[j];
            else
              availableDirections[j] = NONE;

        /* Connect to the chosen neighbor. */
        if (!blocked)
        {
          drewDirection = draw_direction(availableDirections);
          reverseDirection = get_reverse_direction(drewDirection);
          neighborIndex = get_neighbor_index(maze, squareIndex, drewDirection);

          *(maze->squares + squareIndex) = OPEN_DIRECTION(*(maze->squares + squareIndex), drewDirection);
          *(maze->squares + neighborIndex) = OPEN_DIRECTION(*(maze->squares + neighborIndex), reverseDirection);
          squareIndex = neighborIndex;
        }
      }
    }
  }

  return maze;
}

void destroy_maze(Maze *maze)
{
  free(maze->squares);
  maze->squares = NULL;
  free(maze->permutation);
  maze->permutation = NULL;
  free(maze);
}

/* Arrange the N elements of ARRAY in random order.
   Only effective if N is much smaller than RAND_MAX;
   if this may not be the case, use a better random
   number generator. */
void shuffle(int *const array, size_t const size)
{
  size_t i = 0, j = 0;
  int temp = 0;

  for (i = 0; i < size - 1; i++)
  {
    j = i + rand() / (RAND_MAX / (size - i) + 1);
    temp = array[j];
    array[j] = array[i];
    array[i] = temp;
  }
}

Direction draw_direction(Direction availableDirections[])
{
  int i = 0, count = 0, drewDirection = 0;

  for (i = 0; i < 4; i++)
    if (availableDirections[i] != NONE)
      count++;

  drewDirection = rand() % count;

  count = 0;
  for (i = 0; i < 4; i++)
  {
    if (availableDirections[i] != NONE) {
      if (drewDirection == count)
        return availableDirections[i];
      count++;
    }
  }

  return NONE; /* Never happens. */
}

/*
 * Return a non null integer if the provided square has a neighbor in this
 * direction.
 */
char has_neighbor(Maze const *const maze, int const square_index,
                  Direction direction)
{
  int x = 0, y = 0;

  switch (direction)
  {
    case LEFT:
      square_index_to_coordinates(maze, square_index, &x, &y);
      return x > 0;
    case TOP:
      square_index_to_coordinates(maze, square_index, &x, &y);
      return y > 0;
    case RIGHT:
      square_index_to_coordinates(maze, square_index, &x, &y);
      return x < maze->width - 1;
    default:
      square_index_to_coordinates(maze, square_index, &x, &y);
      return y < maze->height - 1;
  }
}

/*
 * Return a non null integer if the provided square has a neighbor in this
 * direction which is not already connected to a path.
 */
char has_neighbor_available(Maze const *const maze, int const square_index,
                            Direction direction)
{
  int neighborIndex = 0;

  if (!has_neighbor(maze, square_index, direction))
    return 0;

  neighborIndex = get_neighbor_index(maze, square_index, direction);
  return *(maze->squares + neighborIndex) == NONE;
}

int get_neighbor_index(Maze const *const maze, int const square_index,
                       Direction const direction)
{
  int x = 0, y = 0;

  switch (direction)
  {
    case LEFT:
      return square_index - 1;
    case TOP:
      square_index_to_coordinates(maze, square_index, &x, &y);
      return coordinates_to_square_index(maze, x, y - 1);
    case RIGHT:
      return square_index + 1;
    default:
      square_index_to_coordinates(maze, square_index, &x, &y);
      return coordinates_to_square_index(maze, x, y + 1);
  }
}

Direction get_reverse_direction(Direction const direction)
{
  switch (direction)
  {
    case LEFT:
      return RIGHT;
    case TOP:
      return BOTTOM;
    case RIGHT:
      return LEFT;
    default:
      return TOP;
  }
}

void square_index_to_coordinates(Maze const *const maze, int const square_index,
                                 int *const out_x, int *const out_y)
{
  *out_x = square_index % maze->width;
  *out_y = square_index / maze->width;
}

int coordinates_to_square_index(Maze const *const maze, int const x,
                                int const y)
{
  return maze->width * y + x;
}

void print_maze(Maze const *const maze, FILE *const file)
{
  int x = 0, y = 0;

  for (y = 0; y < maze->height; y++)
  {
    for (x = 0; x < maze->width; x++)
      fprintf(file, "%02d ", *(maze->squares + coordinates_to_square_index(maze, x, y)));
    fprintf(file, "\n");
  }
}
