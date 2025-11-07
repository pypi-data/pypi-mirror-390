"""
Robot class for maze navigation.
"""

from typing import Tuple, List
from .maze import Direction, Maze
from functools import wraps

class RobotInstructionLimitException(Exception):
    """Exception raised when robot instruction call limit is exceeded."""
    pass

def robot_instruction(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        self._instruction_call_count += 1
        calls = self.specific_instruction_count.get(func.__name__, 0)
        self.specific_instruction_count[func.__name__] = calls + 1

        if self._instruction_call_count > self._MAX_CALLS:
            raise RobotInstructionLimitException(f"Robot instructions called more than {self._MAX_CALLS} times in total")
        return func(self, *args, **kwargs)
    return wrapper

class Robot:
    """Represents a robot that can navigate through a maze."""
    
    def __init__(self, start_position: Tuple[int, int], start_direction: Direction, move_callback=None):
        """
        Initialize the robot.
        
        Args:
            start_position: Starting (x, y) position
            start_direction: Initial direction the robot faces
        """
        self.position = start_position
        self.direction = start_direction
        self.path = [start_position]  # Track the robot's path
        self.steps = 0
        self._instruction_call_count = 0
        self.specific_instruction_count = {}
        self._MAX_CALLS = 10000
        self.move_callback = move_callback
    
    @robot_instruction
    def move_forward(self, maze: Maze) -> bool:
        """
        Move the robot forward in its current direction.
        
        Args:
            maze: The maze to navigate
            
        Returns:
            True if movement was successful, False if blocked by wall
        """
        if maze.is_path_clear(self.position[0], self.position[1], self.direction):
            new_x, new_y = maze.get_neighbor_position(self.position[0], self.position[1], self.direction)
            self.position = (new_x, new_y)
            self.path.append(self.position)
            self.steps += 1
            if self.move_callback:
                arguments = self.create_move_callback_arguments(maze)
                self.move_callback(**arguments)
            return True
        return False

    def create_move_callback_arguments(self, maze: Maze):
        """Create the arguments for the move callback."""
        possibilities = {
            "position": self.position,
            "position_x": self.position[0],
            "position_y": self.position[1],
            "direction": self.direction.name,
            "steps": self.steps,
            "maze": maze,
            "maze_grid": maze.grid,
            "maze_colors": maze.colors,
            "maze_locks_and_keys": maze.locks_and_keys,
            "robot": self,
            "robot_steps": self.steps,
            "robot_path": self.path,
            "robot_has_reached_end": self.has_reached_end(maze),
            "robot_can_move_forward": self.can_move_forward(maze),
        }
        possibilities["data"] = possibilities
        # Return only the keywords that are expected by the callback function
        if self.move_callback:
            callback_params = self.move_callback.__code__.co_varnames[:self.move_callback.__code__.co_argcount]
            return {key: possibilities[key] for key in callback_params if key in possibilities}
        return {}
    
    @robot_instruction
    def turn_left(self):
        """Turn the robot 90 degrees to the left."""
        if self.direction == Direction.NORTH:
            self.direction = Direction.WEST
        elif self.direction == Direction.WEST:
            self.direction = Direction.SOUTH
        elif self.direction == Direction.SOUTH:
            self.direction = Direction.EAST
        elif self.direction == Direction.EAST:
            self.direction = Direction.NORTH
    
    @robot_instruction
    def turn_right(self):
        """Turn the robot 90 degrees to the right."""
        if self.direction == Direction.NORTH:
            self.direction = Direction.EAST
        elif self.direction == Direction.EAST:
            self.direction = Direction.SOUTH
        elif self.direction == Direction.SOUTH:
            self.direction = Direction.WEST
        elif self.direction == Direction.WEST:
            self.direction = Direction.NORTH
    
    @robot_instruction
    def turn_around(self):
        """Turn the robot 180 degrees."""
        self.turn_left()
        self.turn_left()
    
    @robot_instruction
    def get_position(self) -> Tuple[int, int]:
        """Get the current position of the robot."""
        return self.position
    
    @robot_instruction
    def get_direction(self) -> Direction:
        """Get the current direction the robot is facing."""
        return self.direction
    
    @robot_instruction
    def get_path(self) -> List[Tuple[int, int]]:
        """Get the complete path the robot has taken."""
        return self.path.copy()
    
    @robot_instruction
    def get_steps(self) -> int:
        """Get the number of steps the robot has taken."""
        return self.steps
    
    @robot_instruction
    def has_reached_end(self, maze: Maze) -> bool:
        """Check if the robot has reached the end position."""
        return maze.is_end(self.position[0], self.position[1])
    
    @robot_instruction
    def can_move_forward(self, maze: Maze) -> bool:
        """Check if the robot can move forward without hitting a wall."""
        return maze.is_path_clear(self.position[0], self.position[1], self.direction)
    
    @robot_instruction
    def paint_current_tile(self, maze: Maze, color: str) -> bool:
        """
        Paint the tile the robot is currently standing on.
        
        Args:
            maze: The maze to paint on
            color: Color name (string)
            
        Returns:
            True if painting was successful, False otherwise
        """
        return maze.paint_tile(self.position[0], self.position[1], color)
    
    @robot_instruction
    def paint_forward_tile(self, maze: Maze, color: str) -> bool:
        """
        Paint the tile in front of the robot.
        
        Args:
            maze: The maze to paint on
            color: Color name (string)
            
        Returns:
            True if painting was successful, False otherwise
        """
        if maze.is_path_clear(self.position[0], self.position[1], self.direction):
            nx, ny = maze.get_neighbor_position(self.position[0], self.position[1], self.direction)
            return maze.paint_tile(nx, ny, color)
        return False
    
    @robot_instruction
    def get_current_tile_color(self, maze: Maze) -> str:
        """
        Get the color of the tile the robot is currently standing on.
        
        Args:
            maze: The maze to check
            
        Returns:
            Color name if tile is painted, "none" if no color
        """
        color = maze.get_tile_color(self.position[0], self.position[1])
        return color if color else "none"
    
    @robot_instruction
    def get_forward_tile_color(self, maze: Maze) -> str:
        """
        Get the color of the tile in front of the robot.
        
        Args:
            maze: The maze to check
            
        Returns:
            Color name if tile is painted, "none" if no color, "wall" if blocked
        """
        if not maze.is_path_clear(self.position[0], self.position[1], self.direction):
            return "wall"
        
        nx, ny = maze.get_neighbor_position(self.position[0], self.position[1], self.direction)
        color = maze.get_tile_color(nx, ny)
        return color if color else "none"
    
    def reset(self, start_position: Tuple[int, int], start_direction: Direction):
        """Reset the robot to its starting position and direction."""
        self.position = start_position
        self.direction = start_direction
        self.path = [start_position]
        self.steps = 0
        self._instruction_call_count = 0