"""
Maze representation for the robot visualization.
"""

from typing import Tuple, List, Optional
from enum import Enum
from copy import deepcopy

class CellType(Enum):
    """Types of cells in the maze."""
    EMPTY = 0
    WALL = 1
    START = 2
    END = 3
    LOCK = 4
    KEY = 5

class Direction(Enum):
    """Cardinal directions the robot can face."""
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

class Maze:
    """Represents a 2D maze grid with walls, start, end positions, locks, and keys."""
    
    def __init__(self, maze_data: List[List[int]], locks_and_keys: Optional[dict] = None):
        """
        Initialize maze from 2D grid data.
        
        Args:
            maze_data: 2D list where:
                0 = empty cell
                1 = wall
                2 = start position
                3 = end position
                4 = lock
                5 = key
            locks_and_keys: Dictionary mapping key positions to lock positions.
                           Format: {(key_x, key_y): (lock_x, lock_y)}
                           If None, no lock-key relationships are defined.
        """
        self.grid = deepcopy(maze_data)
        self.height = len(maze_data)
        self.width = len(maze_data[0]) if maze_data else 0
        
        # Initialize colors grid (None means no color)
        self.colors = [[None for _ in range(self.width)] for _ in range(self.height)]
        
        # Initialize locks and keys dictionary
        self.locks_and_keys = deepcopy(locks_and_keys) or {}
        # Place walls at lock positions
        for lock_pos in self.locks_and_keys.values():
            self.grid[lock_pos[1]][lock_pos[0]] = CellType.WALL.value
        
        # Find start and end positions
        self.start_position = self._find_cell(CellType.START)
        self.end_position = self._find_cell(CellType.END)
        
        # Default start direction is North
        self.start_direction = Direction.SOUTH
        
        if not self.start_position:
            raise ValueError("Maze must have a start position (value 2)")

        # Make sure that the maze is rectangular
        for row in self.grid:
            if len(row) != self.width:
                raise ValueError("Maze must be rectangular")
    
    def _find_cell(self, cell_type: CellType) -> Optional[Tuple[int, int]]:
        """Find the position of a specific cell type."""
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == cell_type.value:
                    return (x, y)
        return None
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if a position is within the maze bounds."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def is_wall(self, x: int, y: int) -> bool:
        """Check if a position contains a wall."""
        if not self.is_valid_position(x, y):
            return True  # Out of bounds is considered a wall
        return self.grid[y][x] == CellType.WALL.value
    
    def is_end(self, x: int, y: int) -> bool:
        """Check if a position is the end goal."""
        if not self.is_valid_position(x, y):
            return False
        return self.grid[y][x] == CellType.END.value
    
    def is_lock(self, x: int, y: int) -> bool:
        """Check if a position contains a lock."""
        if not self.is_valid_position(x, y):
            return False
        return self.grid[y][x] == CellType.LOCK.value
    
    def is_key(self, x: int, y: int) -> bool:
        """Check if a position contains a key."""
        if not self.is_valid_position(x, y):
            return False
        return self.grid[y][x] == CellType.KEY.value
    
    def get_key_for_lock(self, lock_x: int, lock_y: int) -> Optional[Tuple[int, int]]:
        """
        Get the position of the key that opens a specific lock.
        
        Args:
            lock_x, lock_y: Position of the lock
            
        Returns:
            Position of the corresponding key, or None if no key is defined for this lock
        """
        for key_pos, lock_pos in self.locks_and_keys.items():
            if lock_pos == (lock_x, lock_y):
                return key_pos
        return None
    
    def get_lock_for_key(self, key_x: int, key_y: int) -> Optional[Tuple[int, int]]:
        """
        Get the position of the lock that a specific key opens.
        
        Args:
            key_x, key_y: Position of the key
            
        Returns:
            Position of the corresponding lock, or None if this key doesn't open any lock
        """
        return self.locks_and_keys.get((key_x, key_y))
    
    def get_cell_type(self, x: int, y: int) -> CellType:
        """Get the type of cell at a given position."""
        if not self.is_valid_position(x, y):
            return CellType.WALL
        return CellType(self.grid[y][x])
    
    def get_neighbor_position(self, x: int, y: int, direction: Direction) -> Tuple[int, int]:
        """Get the position of the neighbor in the given direction."""
        if direction == Direction.NORTH:
            return (x, y - 1)
        elif direction == Direction.EAST:
            return (x + 1, y)
        elif direction == Direction.SOUTH:
            return (x, y + 1)
        elif direction == Direction.WEST:
            return (x - 1, y)
        else:
            raise ValueError(f"Invalid direction: {direction}")
    
    def is_path_clear(self, x: int, y: int, direction: Direction) -> bool:
        """Check if the path in the given direction is clear (no wall)."""
        nx, ny = self.get_neighbor_position(x, y, direction)
        return not self.is_wall(nx, ny) 
    
    def paint_tile(self, x: int, y: int, color: str) -> bool:
        """
        Paint a tile with a specific color.
        
        Args:
            x, y: Position to paint
            color: Color name (string)
            
        Returns:
            True if painting was successful, False if position is invalid or is a wall
        """
        if not self.is_valid_position(x, y) or self.is_wall(x, y):
            return False
        
        self.colors[y][x] = color
        return True
    
    def get_tile_color(self, x: int, y: int) -> Optional[str]:
        """
        Get the color of a tile.
        
        Args:
            x, y: Position to check
            
        Returns:
            Color name if tile is painted, None if no color or invalid position
        """
        if not self.is_valid_position(x, y):
            return None
        
        return self.colors[y][x]

    def clear_tile_color(self, x: int, y: int) -> bool:
        """
        Clear the color from a tile.
        
        Args:
            x, y: Position to clear
            
        Returns:
            True if clearing was successful, False if position is invalid
        """
        if not self.is_valid_position(x, y):
            return False
        
        self.colors[y][x] = None
        return True 
