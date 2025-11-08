# Minobot

An educational Python package for learning programming through maze solving.

## For Students

Learn programming concepts by writing code to solve mazes. Watch your robot navigate through mazes in real-time or as videos in Jupyter notebooks.

## Quick Start

```python
from minobot import *

# Create a maze
maze = [
    [1, 1, 1, 1, 1], # 1 represents a wall
    [1, 0, 0, 2, 1], # 0 is empty and 2 is the starting position
    [1, 0, 1, 0, 1],
    [1, 0, 0, 3, 1], # 3 is the goal
    [1, 1, 1, 1, 1]
]

# Write your solution
def solve():
    while not has_reached_end():
        if can_move():
            move()
        else:
            turn_left()

# Watch it work
solve_maze(maze, solve)
```

## Installation

```bash
pip install minobot
```

> ⚠️ **Warning:**  
> If you encounter an *encoder error* when trying to display a video in a notebook, you may need to reinstall OpenCV using Conda. Follow these steps:

 1. Create and activate a Conda environment (if you haven’t already).  
 2. Run the following commands:

 ```bash
 pip install minobot
 pip uninstall opencv-python
 conda install -c conda-forge opencv
 ```


## Robot Instructions

The MinoBot provides simple, intuitive instructions for maze navigation:

### Movement Instructions
- `move()` - Move forward one step (returns `True` if successful, `False` if blocked)
- `turn_left()` - Turn 90 degrees to the left
- `turn_right()` - Turn 90 degrees to the right  
- `turn_around()` - Turn 180 degrees

### Sensing Instructions
- `can_move()` - Check if the robot can move forward without hitting a wall
- `has_reached_end()` - Check if the robot has reached the goal
- `get_position()` - Get current (x, y) position
- `get_direction()` - Get current direction (NORTH, EAST, SOUTH, WEST)
- `get_steps()` - Get number of steps taken

### Painting Instructions
- `paint_current(color)` - Paint the tile the robot is standing on
- `paint_forward(color)` - Paint the tile in front of the robot
- `get_current_color()` - Get color of current tile
- `get_forward_color()` - Get color of tile in front

#### Colors

The MinoBot can paint tiles with the following colors:
- `red` - Light red
- `blue` - Light blue  
- `green` - Light green
- `yellow` - Light yellow
- `purple` - Light purple
- `orange` - Light orange
- `pink` - Light pink
- `cyan` - Light cyan



## Educational Features

- **Visual Learning**: See your code execute step-by-step
- **Multiple Environments**: Works in Jupyter notebooks and standalone Python
- **Algorithm Practice**: Perfect for learning loops, conditionals, and problem-solving
