"""
Simplified instruction system for robot movement.
Designed for students learning programming.
"""

from typing import List
from enum import Enum
from .robot import Robot
from .maze import Maze

# Global context for robot and maze
_current_robot = None
_current_maze = None
_current_visualizer = None

def set_context(robot: Robot, maze: Maze, visualizer):
    """Set the global robot and maze context for instructions."""
    global _current_robot, _current_maze, _current_visualizer
    _current_robot = robot
    _current_maze = maze
    _current_visualizer = visualizer

def get_context() -> tuple[Robot, Maze]:
    """Get the current robot and maze context."""
    if _current_robot is None or _current_maze is None:
        raise RuntimeError("Context not set. Call set_context(robot, maze) first.")
    return _current_robot, _current_maze, _current_visualizer

def move() -> bool:
    """
    Move the robot forward in its current direction.
    
    Returns:
        True if movement was successful, False if blocked by wall
    """
    robot, maze, visualizer = get_context()
    visualizer.add_frame()
    return robot.move_forward(maze)

def turn_left():
    """Turn the robot 90 degrees to the left."""
    robot, _, visualizer = get_context()
    visualizer.add_frame()
    robot.turn_left()

def turn_right():
    """Turn the robot 90 degrees to the right."""
    robot, _, visualizer = get_context()
    visualizer.add_frame()
    robot.turn_right()

def turn_around():
    """Turn the robot 180 degrees."""
    robot, _, visualizer = get_context()
    visualizer.add_frame()
    robot.turn_around()

def can_move() -> bool:
    """
    Check if the robot can move forward without hitting a wall.
    
    Returns:
        True if the robot can move forward, False otherwise
    """
    robot, maze, visualizer = get_context()
    return robot.can_move_forward(maze)

def has_reached_end() -> bool:
    """
    Check if the robot has reached the end position.
    
    Returns:
        True if the robot has reached the end, False otherwise
    """
    robot, maze, visualizer = get_context()
    return robot.has_reached_end(maze)

def get_position() -> tuple[int, int]:
    """
    Get the current position of the robot.
    
    Returns:
        Current (x, y) position
    """
    robot, _, _ = get_context()
    return robot.get_position()

def get_direction() -> str:
    """
    Get the current direction the robot is facing.
    
    Returns:
        Direction name (NORTH, EAST, SOUTH, WEST)
    """
    robot, _, _ = get_context()
    return robot.get_direction().name

def get_steps() -> int:
    """
    Get the number of steps the robot has taken.
    
    Returns:
        Number of steps taken
    """
    robot, _, _ = get_context()
    return robot.get_steps()

def paint_current(color: str) -> bool:
    """
    Paint the tile the robot is currently standing on.
    
    Args:
        color: Color name (string)
        
    Returns:
        True if painting was successful, False otherwise
    """
    robot, maze, visualizer = get_context()
    visualizer.add_frame()
    return robot.paint_current_tile(maze, color)

def paint_forward(color: str) -> bool:
    """
    Paint the tile in front of the robot.
    
    Args:
        color: Color name (string)
        
    Returns:
        True if painting was successful, False otherwise
    """
    robot, maze, visualizer = get_context()
    visualizer.add_frame()
    return robot.paint_forward_tile(maze, color)

def get_current_color() -> str:
    """
    Get the color of the tile the robot is currently standing on.
    
    Returns:
        Color name if tile is painted, "none" if no color
    """
    robot, maze, _ = get_context()
    return robot.get_current_tile_color(maze)

def get_forward_color() -> str:
    """
    Get the color of the tile in front of the robot.
    
    Returns:
        Color name if tile is painted, "none" if no color, "wall" if blocked
    """
    robot, maze, _ = get_context()
    return robot.get_forward_tile_color(maze)

# Legacy support for the old instruction system
class InstructionType(Enum):
    """Types of instructions the robot can execute."""
    MOVE = "MOVE"
    TURN_LEFT = "TURN_LEFT"
    TURN_RIGHT = "TURN_RIGHT"
    TURN_AROUND = "TURN_AROUND"

class Instruction:
    """Legacy instruction class for backward compatibility."""
    
    def __init__(self, instruction_type: InstructionType):
        self.type = instruction_type
    
    def execute(self, robot: Robot, maze: Maze) -> bool:
        """Execute this instruction on the robot."""
        if self.type == InstructionType.MOVE:
            return robot.move_forward(maze)
        elif self.type == InstructionType.TURN_LEFT:
            robot.turn_left()
            return True
        elif self.type == InstructionType.TURN_RIGHT:
            robot.turn_right()
            return True
        elif self.type == InstructionType.TURN_AROUND:
            robot.turn_around()
            return True
        else:
            raise ValueError(f"Unknown instruction type: {self.type}")

class InstructionParser:
    """Legacy parser for backward compatibility."""
    
    def __init__(self):
        self.instruction_map = {
            "MOVE": InstructionType.MOVE,
            "TURN_LEFT": InstructionType.TURN_LEFT,
            "TURN_RIGHT": InstructionType.TURN_RIGHT,
            "TURN_AROUND": InstructionType.TURN_AROUND,
            "FORWARD": InstructionType.MOVE,
            "LEFT": InstructionType.TURN_LEFT,
            "RIGHT": InstructionType.TURN_RIGHT,
            "AROUND": InstructionType.TURN_AROUND,
        }
    
    def parse(self, instructions: List[str]) -> List[Instruction]:
        """Parse a list of instruction strings into Instruction objects."""
        parsed_instructions = []
        
        for instruction_str in instructions:
            instruction_str = instruction_str.strip().upper()
            
            if instruction_str in self.instruction_map:
                instruction_type = self.instruction_map[instruction_str]
                parsed_instructions.append(Instruction(instruction_type))
            else:
                raise ValueError(f"Unknown instruction: {instruction_str}")
        
        return parsed_instructions
    
    def parse_string(self, instruction_text: str) -> List[Instruction]:
        """Parse a string of instructions separated by newlines or spaces."""
        lines = instruction_text.strip().split('\n')
        instructions = []
        
        for line in lines:
            line_instructions = line.strip().split()
            instructions.extend(line_instructions)
        
        return self.parse(instructions)
