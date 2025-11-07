"""
Example mazes and algorithms for the VU Robot package.
"""

import random
from typing import List

def get_maze_data(maze_data) -> List[List[int]]:
    try:
        return globals()[f"create_{maze_data}_maze"]()
    except KeyError:
        raise ValueError(f"Unknown maze type: {maze_data}")

def create_simple_maze() -> List[List[int]]:
    """Create a simple 5x5 maze."""
    return [
        [2, 0, 0, 0, 0],  # Start at top-left
        [1, 1, 0, 1, 0],  # Wall in middle
        [0, 0, 0, 1, 0],  # Clear path
        [0, 1, 1, 1, 0],  # Wall at bottom
        [0, 0, 0, 0, 3],  # End at bottom-right
    ]

def create_simple2_maze() -> List[List[int]]:
    """Create a simple 5x5 maze."""
    return [
        [2, 0, 0, 0, 0],  # Start at top-left
        [1, 1, 0, 1, 1],  # Wall in middle
        [0, 0, 0, 1, 0],  # Clear path
        [0, 1, 1, 1, 0],  # Wall at bottom
        [0, 0, 0, 0, 3],  # End at bottom-right
    ]

def create_branching_maze() -> List[List[int]]:
    """Create a branching maze."""
    return [
        [2, 0, 0, 0, 0, 0, 0, 0],  # Start
        [1, 1, 1, 0, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],
        [1, 1, 0, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 3],  # End
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]

def create_complex_maze() -> List[List[int]]:
    """More complex variation of the branching maze."""
    return [
        [2, 0, 0, 0, 0, 0, 0, 0],  # Start
        [1, 1, 1, 0, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],
        [1, 1, 0, 1, 0, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 3],  # End
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]

def create_looping_maze() -> List[List[int]]:
    """Create a looping maze."""
    return [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Start
        [1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0],
        [0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 3]  # End
    ]

def create_spiral_maze() -> List[List[int]]:
    """Create a spiral-shaped maze."""
    return [
        [2, 0, 0, 0, 0, 0, 0, 0],  # Start at top-left
        [1, 1, 1, 1, 1, 1, 1, 0],  # Right wall
        [0, 0, 0, 0, 0, 0, 1, 0],  # Path spirals inward
        [0, 1, 1, 1, 1, 0, 1, 0],  # Inner walls
        [0, 1, 0, 3, 1, 0, 1, 0],  # End (3) in middle
        [0, 1, 0, 1, 1, 0, 1, 0],  # Inner walls
        [0, 1, 0, 0, 0, 0, 1, 0],  # Path continues
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]
    

def create_simple_random_maze() -> List[List[int]]:
    """Create a simple random maze."""
    maze = [
        [2, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 3],
    ]

    # One random opening in row two and four
    maze[1][random.randint(0, 5)] = 0
    maze[3][random.randint(0, 5)] = 0

    return maze

def create_empty_maze():
    """
    Create an empty maze.
    """
    return [
        [2, 0, 0, 0, 0, 0, 0, 0],  # Start
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 3, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],  # End
    ]

def create_random_empty_maze():
    """
    Create an empty maze.
    """
    maze = [
        [2, 0, 0, 0, 0, 0, 0, 0],  # Start
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],  # End
    ]
    x = random.randint(0, 7)
    y = random.randint(1, 6)
    maze[x][y] = 3
    return maze

def create_actually_empty_maze():
    """
    Create an empty maze.
    """
    return [
        [2, 0, 0, 0, 0, 0, 0, 0],  # Start
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],  # End
    ]

def create_not_actually_empty_maze():
    """
    Create an not actually empty maze.
    """
    maze = [
        [2, 0, 0, 0, 0, 0, 0, 0],  # Start
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 3],  # End
    ]

    x = random.randint(1, 6)
    maze[8][x] = 0
    return maze
