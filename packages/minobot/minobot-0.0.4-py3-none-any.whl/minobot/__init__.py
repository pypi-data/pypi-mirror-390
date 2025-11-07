"""
VU Robot - A package for visualizing robot maze solving.

This package provides tools to create mazes, define robot instructions,
and visualize the robot's path through the maze.
"""

# pygame prints a message to the console when it is imported, this hides it
from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from .maze import Maze
from .robot import Robot
from .pygame_visualizer import PygameVisualizer
from .video_visualizer import NotebookVisualizer
from .runner import Runner
from .instructions import InstructionParser, Instruction, move, turn_left, turn_right, can_move, has_reached_end, paint_current, paint_forward, get_current_color, get_forward_color, get_direction, get_position, get_steps
from .notebook_utils import show_videos, show_single_video, create_video_comparison
from .examples import get_maze_data
from . import sprite_assets
from .sprite_assets import config
import time

def is_notebook():
    """Detect if code is running in a Jupyter notebook."""
    try:
        from IPython import get_ipython
        shell = get_ipython().__class__.__name__
        return shell == 'ZMQInteractiveShell'
    except (ImportError, AttributeError):
        return False

__version__ = "0.0.4"
__all__ = ["Maze", "Robot", "PygameVisualizer", "NotebookVisualizer", "Runner", "InstructionParser", "Instruction", 
           "show_videos", "show_single_video", "create_video_comparison", "move", "turn_left", "turn_right", "can_move", "has_reached_end",
           "paint_current", "paint_forward", "get_current_color", "get_forward_color", "solve_maze", "show_maze", "get_direction", "test_maze",
           "config", "get_position", "get_steps"]

def solve_maze(maze_data, instructions, locks_and_keys=None, move_callback=None, cell_size=80, notebook=None, fps=2, show_info=False):
    """
    Main function to visualize a robot solving a maze.
    
    Args:
        maze_data: 2D list representing the maze (0=empty, 1=wall, 2=start, 3=end)
        instructions: List of instructions or Python function
        cell_size: Size of each cell in pixels
        notebook: If None, auto-detect notebook environment. If True/False, use that setting.
        fps: Frames per second for video (notebook only)
        show_info: If True, displays status information panel (affects screen size)
    """
    # Auto-detect notebook environment if not specified
    if notebook is None:
        notebook = is_notebook()

    maze, robot = create_maze_and_robot(maze_data, locks_and_keys, move_callback)

    if notebook:
        visualizer = NotebookVisualizer(maze, robot, cell_size, fps, show_info)
    else:
        visualizer = PygameVisualizer(maze, robot, cell_size, show_info)

    if callable(instructions):
        return visualizer.run_with_simple_function(instructions)
    else:
        parser = InstructionParser()
        if isinstance(instructions, str):
            parsed_instructions = parser.parse_string(instructions)
        else:
            parsed_instructions = parser.parse(instructions)
        visualizer.run_with_instructions(parsed_instructions)

def test_maze(maze_data, instructions, locks_and_keys=None, move_callback=None):
    """
    Test a maze with a given instructions and return performance data.
    
    Returns:
        dict: Dictionary containing:
            - solvable (bool): Whether the maze is solvable
            - steps (int): Number of steps taken
            - instruction_count (int): Number of instructions executed
            - time (float): Time taken in seconds
            - path (list): The path taken by the robot
            - maze_data (list): The maze data
            - maze_size (tuple): The size of the maze
            - maze_colors (list): The colors of the maze
            - locks_and_keys (dict): The locks and keys
    """
    
    maze, robot = create_maze_and_robot(maze_data, locks_and_keys, move_callback)
    runner = Runner(maze, robot)
    
    start_time = time.time()
    success = runner.run_with_simple_function(instructions)
    end_time = time.time()
    
    return {
        'solvable': success,
        'steps': robot.steps,
        'instruction_count': robot._instruction_call_count,
        'time': end_time - start_time,
        'path': robot.path,
        'maze_data': maze.grid,
        'maze_size': (maze.width, maze.height),
        'maze_colors': maze.colors,
        'locks_and_keys': locks_and_keys,
        'specific_instruction_count': robot.specific_instruction_count,
    }

def create_maze_and_robot(maze_data, locks_and_keys=None, move_callback=None):

    if isinstance(maze_data, str):
        maze_data = get_maze_data(maze_data)
        
    maze = Maze(maze_data, locks_and_keys)
    robot = Robot(maze.start_position, maze.start_direction, move_callback)
    return maze, robot

def show_maze(maze_data, locks_and_keys=None, notebook=None, cell_size=80):
    """
    Show a maze as a image.
    
    Args:
        maze_data: 2D list representing the maze (0=empty, 1=wall, 2=start, 3=end)
        locks_and_keys: Optional dictionary of locks and keys
        notebook: If None, auto-detect notebook environment. If True/False, use that setting.
        cell_size: Size of each cell in pixels
    """
    # Auto-detect notebook environment if not specified
    if notebook is None:
        notebook = is_notebook()
    maze, robot = create_maze_and_robot(maze_data, locks_and_keys)

    if notebook:
        visualizer = NotebookVisualizer(maze, robot, cell_size, show_info=False)
    else:
        visualizer = PygameVisualizer(maze, robot, cell_size, show_info=False)
    visualizer.show_initial_setup()