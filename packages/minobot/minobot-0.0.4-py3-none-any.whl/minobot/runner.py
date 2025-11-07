"""
Silent visualizer for maze and robot - runs without any display output.
"""

from typing import Callable
from .maze import Maze
from .robot import Robot, RobotInstructionLimitException
from .instructions import set_context


class Runner():
    """Runner that runs the maze solver without any display output."""
    
    def __init__(self, maze: Maze, robot: Robot):
        self.maze = maze
        self.robot = robot
    
    def run_with_simple_function(self, func: Callable):
        set_context(self.robot, self.maze, self)
        
        try:
            success = func()
        except RobotInstructionLimitException as e:
            print(e)
            success = False

        return success

