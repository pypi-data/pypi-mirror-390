"""
Sprite asset management using importlib.resources for cross-platform compatibility.

This module preloads all sprite file paths on import, ensuring assets work
correctly across different operating systems and when the package is installed
as a wheel or zip file.
"""

from importlib.resources import files
from typing import Literal


class SpriteConfig:
    """
    Singleton configuration class for sprite themes.
    
    Controls which sprite sets are used for rendering (e.g., robot style).
    Access the global instance via the module-level `config` variable.
    
    Example:
        from minobot import config
        config.robot_theme = "humanlike"  # Use humanlike robot sprites
        config.robot_theme = "robolike"   # Use robolike robot sprites (default)
    """
    
    _instance = None
    _initialized = False
    
    # Valid theme options
    ROBOT_THEMES = ("robolike", "humanlike")
    
    def __new__(cls):
        """Singleton pattern - return the same instance every time."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize configuration with default values."""
        if not SpriteConfig._initialized:
            self._robot_theme: Literal["robolike", "humanlike"] = "robolike"
            SpriteConfig._initialized = True
    
    @property
    def robot_theme(self) -> str:
        """Get the current robot theme."""
        return self._robot_theme
    
    @robot_theme.setter
    def robot_theme(self, theme: str) -> None:
        """
        Set the robot theme.
        
        Args:
            theme: One of "robolike" or "humanlike"
            
        Raises:
            ValueError: If theme is not one of the valid options
        """
        theme = theme.lower().strip()
        if theme not in self.ROBOT_THEMES:
            raise ValueError(
                f"Invalid robot theme '{theme}'. "
                f"Valid options: {', '.join(self.ROBOT_THEMES)}"
            )
        self._robot_theme = theme
    
    def reset(self) -> None:
        """Reset all settings to their default values."""
        self._robot_theme = "robolike"


# Global singleton instance
config = SpriteConfig()


def _get_asset_path(*path_parts: str) -> str:
    """
    Get path to asset file using importlib.resources.
    
    This works across platforms and with packaged installs (wheels are directory-based).
    Uses Python 3.9+ files() API which doesn't require __init__.py files.
    
    Args:
        *path_parts: Path components relative to the assets directory
        
    Returns:
        String path to the asset file
        
    Note:
        Modern Python packages (wheels) are always installed as directories,
        so str() conversion works correctly. For zip-based installs (eggs, rare),
        this may require additional handling.
    """
    # Python 3.9+ approach using files() API
    # Since we require Python >= 3.10, we don't need a fallback
    asset_file = files("minobot").joinpath("assets", *path_parts)
    
    # Convert to string path - works for directory-based installs (wheels)
    # pygame and cv2 accept string paths for file loading
    return str(asset_file)


# Preload all sprite paths on module import
_SPRITE_PATHS: dict[str, str] = {}

def _initialize_sprites():
    """Initialize all sprite paths on module import."""
    global _SPRITE_PATHS
    
    # Maze sprites
    maze_sprites = {
        "path_0": _get_asset_path("maze", "path_0.png"),
        
        "leaf_0": _get_asset_path("maze", "leaf_0.png"),
        "leaf_1": _get_asset_path("maze", "leaf_1.png"),
        "leaf_2": _get_asset_path("maze", "leaf_2.png"),
        "leaf_3": _get_asset_path("maze", "leaf_3.png"),
        "leaf_4": _get_asset_path("maze", "leaf_4.png"),
        "leaf_5": _get_asset_path("maze", "leaf_5.png"),
        "leaf_6": _get_asset_path("maze", "leaf_6.png"),
        "leaf_7": _get_asset_path("maze", "leaf_7.png"),
        
        "wall_0": _get_asset_path("maze", "wall_0.png"),
        
        "wall_leaf_0": _get_asset_path("maze", "wall_leaf_0.png"),
        "wall_leaf_1": _get_asset_path("maze", "wall_leaf_1.png"),
        "wall_leaf_2": _get_asset_path("maze", "wall_leaf_2.png"),
        "wall_leaf_3": _get_asset_path("maze", "wall_leaf_3.png"),
        "wall_leaf_4": _get_asset_path("maze", "wall_leaf_4.png"),
        "wall_leaf_5": _get_asset_path("maze", "wall_leaf_5.png"),
        
        "wall_lock": _get_asset_path("maze", "wall_lock.png"),
        "lock": _get_asset_path("maze", "lock.png"),
        "key": _get_asset_path("maze", "key.png"),
                
        "start": _get_asset_path("maze", "start.png"),
        "end": _get_asset_path("maze", "end.png"),
        
    }
    
    # Robot sprites (robolike)
    robot_robolike_sprites = {
        "robot_north": _get_asset_path("robot_robolike", "north.png"),
        "robot_east": _get_asset_path("robot_robolike", "east.png"),
        "robot_south": _get_asset_path("robot_robolike", "south.png"),
        "robot_west": _get_asset_path("robot_robolike", "west.png"),
    }

    # Robot sprites (humanlike)
    robot_humanlike_sprites = {
        "human_robot_north": _get_asset_path("robot_humanlike", "north.png"),
        "human_robot_east": _get_asset_path("robot_humanlike", "east.png"),
        "human_robot_south": _get_asset_path("robot_humanlike", "south.png"),
        "human_robot_west": _get_asset_path("robot_humanlike", "west.png"),
    }

    _SPRITE_PATHS.update(maze_sprites)
    _SPRITE_PATHS.update(robot_robolike_sprites)
    _SPRITE_PATHS.update(robot_humanlike_sprites)

# Initialize sprites on module import
_initialize_sprites()


def get_sprite_path(sprite_name: str) -> str:
    """
    Get the file path for a sprite by name.
    
    Args:
        sprite_name: Name of the sprite (e.g., "path_0", "wall_3", "robot_north")
        
    Returns:
        String path to the sprite file
        
    Raises:
        KeyError: If sprite_name is not found
    """
    if sprite_name not in _SPRITE_PATHS:
        raise KeyError(f"Sprite '{sprite_name}' not found. Available sprites: {list(_SPRITE_PATHS.keys())}")
    return _SPRITE_PATHS[sprite_name]


def get_maze_path_sprite() -> str:
    """Get path sprite for maze floor."""
    return get_sprite_path(f"path_0")

def get_maze_path_leaf_sprite(index: int) -> str:
    """Get path sprite for maze floor."""
    return get_sprite_path(f"leaf_{index}")

def get_maze_wall_sprite() -> str:
    """Get wall sprite for maze."""
    return get_sprite_path(f"wall_0")

def get_maze_wall_leaf_sprite(index: int) -> str:
    """Get wall leaf sprite for maze (0-6)."""
    return get_sprite_path(f"wall_leaf_{index}")

def get_maze_wall_lock() -> str:
    """Get wall sprite for maze."""
    return get_sprite_path(f"wall_lock")

def get_maze_start_sprite() -> str:
    """Get start sprite for maze."""
    return get_sprite_path("start")

def get_maze_end_sprite() -> str:
    """Get end sprite for maze."""
    return get_sprite_path("end")

def get_maze_lock_sprite() -> str:
    """Get end sprite for maze."""
    return get_sprite_path("lock")

def get_maze_key_sprite() -> str:
    """Get end sprite for maze."""
    return get_sprite_path("key")


def get_robot_sprite(direction: str) -> str:
    """
    Get robot sprite for a given direction based on current theme configuration.
    
    Args:
        direction: One of "north", "east", "south", "west"
        
    Returns:
        String path to the robot sprite
        
    Note:
        The sprite returned depends on the current robot_theme setting in config.
        Use config.robot_theme = "humanlike" or "robolike" to change themes.
    """
    theme = config.robot_theme
    
    if theme == "humanlike":
        sprite_name = f"human_robot_{direction}"
    else:  # robolike (default)
        sprite_name = f"robot_{direction}"
    
    return get_sprite_path(sprite_name)

