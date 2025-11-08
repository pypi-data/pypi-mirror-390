"""
Base visualizer with shared rendering logic.

This module contains the BaseVisualizer class that provides all shared
rendering functionality for maze and robot visualization.
"""

import colorsys
import abc
import random

from typing import Tuple, List, Callable
from .maze import Maze, CellType, Direction
from .robot import Robot
from .rendering_backend import RenderingBackend
from .instructions import Instruction
from .sprite_assets import (
    get_maze_path_sprite,
    get_maze_path_leaf_sprite,
    get_maze_wall_sprite,
    get_maze_wall_leaf_sprite,
    get_maze_wall_lock,
    get_maze_start_sprite,
    get_maze_end_sprite,
    get_robot_sprite,
    get_maze_key_sprite,
    get_maze_lock_sprite
)


class BaseVisualizer(abc.ABC):
    """Base class containing shared rendering logic for all visualizers."""
    
    # Colors in RGB format
    COLORS = {
        'background': (255, 255, 255),  # White
        'wall': (64, 64, 64),           # Dark gray
        'empty': (240, 240, 240),       # Light gray
        'start': (255, 0, 0),           # Red
        'end': (0, 255, 0),             # Green
        'lock': (128, 0, 128),          # Purple
        'key': (255, 165, 0),           # Orange
        'robot': (0, 0, 255),           # Blue
        'path': (255, 255, 0),          # Yellow
        'text': (0, 0, 0),              # Black
        # Paint colors
        'red': (255, 100, 100),         # Light red
        'blue': (100, 100, 255),        # Light blue
        'green': (100, 255, 100),       # Light green
        'yellow': (255, 255, 100),      # Light yellow
        'purple': (255, 100, 255),      # Light purple
        'orange': (255, 165, 100),      # Light orange
        'pink': (255, 150, 200),        # Light pink
        'cyan': (100, 255, 255),        # Light cyan
    }
    
    def __init__(self, maze: Maze, robot: Robot, cell_size: int = 80, 
                 show_info: bool = True, backend: RenderingBackend = None):
        """Initialize the base visualizer."""
        self.maze = maze
        self.robot = robot
        self.cell_size = cell_size
        self.show_info = show_info
        self.backend = backend
        self.seed = random.random()
    
    def _get_cell_color(self, cell_type: CellType) -> Tuple[int, int, int]:
        """Get the color for a cell type."""
        if cell_type == CellType.WALL:
            return self.COLORS['wall']
        elif cell_type == CellType.START:
            return self.COLORS['start']
        elif cell_type == CellType.END:
            return self.COLORS['end']
        elif cell_type == CellType.LOCK:
            return self.COLORS['lock']
        elif cell_type == CellType.KEY:
            return self.COLORS['key']
        else:
            return self.COLORS['empty']
    
    def _get_pair_color(self, lock_pos: Tuple[int, int]) -> Tuple[int, int, int]:
        """Get a unique color for a lock-key pair."""
        # Generate a consistent color based on lock position
        hash_val = hash(lock_pos) % 360
        # Convert HSV to RGB for better color distribution
        rgb = colorsys.hsv_to_rgb(hash_val / 360.0, 0.8, 0.9)
        return (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
    
    def _draw_cell(self, backend: RenderingBackend, x: int, y: int) -> None:
        """Draw a single cell with appropriate styling for locks and keys."""
        cell_type = self.maze.get_cell_type(x, y)
        
        # Calculate rectangle coordinates
        rect_x = x * self.cell_size
        rect_y = y * self.cell_size
        
        sprite_path = get_maze_path_sprite()
        
        backend.draw_sprite(sprite_path, rect_x, rect_y, self.cell_size)
        
        random.seed(int(f"{x}{y}") + self.seed)
        if (random.random() > 0.7):
            leaves = list(range(8))
            chosen = random.choice(leaves)
            backend.draw_sprite(get_maze_path_leaf_sprite(chosen), rect_x, rect_y, self.cell_size)
        
        if cell_type == CellType.WALL:
            
            sprite_path = get_maze_wall_sprite()

            if (x,y) in self.maze.locks_and_keys.values(): 
                sprite_path = get_maze_wall_lock()
                color = self._get_pair_color((x,y))
            else:
                color = (255,255,255)
                
            backend.draw_sprite(sprite_path, rect_x, rect_y, self.cell_size, color=color)
        
            if (random.random() > 0.7):
                leaves = list(range(5))
                chosen = random.choice(leaves)
                backend.draw_sprite(get_maze_wall_leaf_sprite(chosen), rect_x, rect_y, self.cell_size)
            
        if cell_type == CellType.START:
            sprite_path = get_maze_start_sprite()
            backend.draw_sprite(sprite_path, rect_x, rect_y, self.cell_size)

        elif cell_type == CellType.END and not self.robot.has_reached_end(self.maze):
            sprite_path = get_maze_end_sprite()
            backend.draw_sprite(sprite_path, rect_x, rect_y, self.cell_size)
    
    def _draw_locks_and_keys(self, backend: RenderingBackend) -> None:
        """Draw locks and keys separately from the main maze grid."""
        # Draw locks
        for lock_pos in self.maze.locks_and_keys.values():
            x, y = lock_pos
            rect_x = x * self.cell_size
            rect_y = y * self.cell_size
            pair_color = self._get_pair_color(lock_pos)
            backend.draw_sprite(get_maze_lock_sprite(), rect_x, rect_y, self.cell_size, color = pair_color)
        
        # Draw keys
        for key_pos in self.maze.locks_and_keys.keys():
            x, y = key_pos
            rect_x = x * self.cell_size
            rect_y = y * self.cell_size
            lock_pos = self.maze.get_lock_for_key(x, y)
            if lock_pos:
                pair_color = self._get_pair_color(lock_pos)
                backend.draw_sprite(get_maze_key_sprite(), rect_x, rect_y, self.cell_size, color = pair_color)
                
    def _draw_painted_tiles(self, backend: RenderingBackend) -> None:
        """Draw tiles that have been painted with colors."""
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                color_name = self.maze.get_tile_color(x, y)
                if color_name and color_name in self.COLORS:
                    # Draw a colored overlay on the tile
                    overlay_x = x * self.cell_size + 2
                    overlay_y = y * self.cell_size + 2
                    overlay_width = self.cell_size - 4
                    overlay_height = self.cell_size - 4
                    backend.draw_rectangle(overlay_x, overlay_y, overlay_width, overlay_height, 
                                         self.COLORS[color_name], filled=True)
    
    def _draw_robot(self, backend: RenderingBackend) -> None:
        """Draw the robot at its current position."""
        x, y = self.robot.position
        
        center_x = x * self.cell_size + self.cell_size // 2
        center_y = y * self.cell_size + self.cell_size // 2
        
        direction = self.robot.direction

        if direction == Direction.NORTH:
            sprite_path = get_robot_sprite("north")
        elif direction == Direction.EAST:
            sprite_path = get_robot_sprite("east")
        elif direction == Direction.SOUTH:
            sprite_path = get_robot_sprite("south")
        elif direction == Direction.WEST:
            sprite_path = get_robot_sprite("west")
        else:
            sprite_path = get_robot_sprite("south")  # Default fallback
            
        backend.draw_sprite(sprite_path, center_x, center_y, width = self.cell_size, center=True)

    def _draw_info(self, backend: RenderingBackend) -> None:
        """Draw information panel at the bottom."""
        info_y = self.maze.height * self.cell_size + 20
        
        # Position info
        pos_text = f"Position: {self.robot.position}"
        backend.draw_text(pos_text, 50, info_y, self.COLORS['text'])
        
        # Direction info
        dir_text = f"Direction: {self.robot.direction.name}"
        backend.draw_text(dir_text, 200, info_y, self.COLORS['text'])
        
        # Steps info
        steps_text = f"Steps: {self.robot.steps}"
        backend.draw_text(steps_text, 400, info_y, self.COLORS['text'])
        
        # Status info
        if self.robot.has_reached_end(self.maze):
            status_text = "Status: REACHED END!"
            status_color = (0, 128, 0)  # Dark green
        else:
            status_text = "Status: Navigating..."
            status_color = self.COLORS['text']
        
        backend.draw_text(status_text, 10, info_y + 30, status_color)
        
        # Moves info (instruction count)
        moves_text = f"Moves: {self.robot._instruction_call_count}"
        backend.draw_text(moves_text, 200, info_y + 30, self.COLORS['text'])
    
    def _draw_maze(self, backend: RenderingBackend) -> None:
        """Draw the maze grid."""
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                self._draw_cell(backend, x, y)
        
        # Draw locks and keys separately
        self._draw_locks_and_keys(backend)
    
    def render_frame(self, backend: RenderingBackend) -> None:
        """Render a complete frame using the provided backend."""
        backend.clear_screen(self.COLORS['background'])
        self._draw_maze(backend)
        self._draw_painted_tiles(backend)
        self._draw_robot(backend)
        if self.show_info:
            self._draw_info(backend)
    
    # Abstract methods that must be implemented by subclasses
    @abc.abstractmethod
    def run_with_instructions(self, instructions: List[Instruction], *args, **kwargs):
        """Run the visualization with a list of instructions."""
        pass

    @abc.abstractmethod
    def run_with_simple_function(self, func: Callable, *args, **kwargs):
        """Run the visualization with a simple function."""
        pass

    @abc.abstractmethod
    def show_initial_setup(self, *args, **kwargs):
        """Display the initial setup of the maze and robot."""
        pass

    @abc.abstractmethod
    def add_frame(self, *args, **kwargs):
        """Add a frame to the display."""
        pass
