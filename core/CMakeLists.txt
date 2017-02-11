cmake_minimum_required(VERSION 3.6)
project(Maze_Generator)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

set(SOURCE_FILES
    maze.c)

add_executable(Maze_Generator ${SOURCE_FILES})