"""
Rendering backend interface for visualizers.

This module provides abstract rendering backends that allow visualizers to draw
without being tied to specific graphics libraries like pygame or OpenCV.
"""

import abc
from typing import Tuple, Union, Optional
import pygame
import cv2
import numpy as np
from .sprite_assets import get_pygame_sprite, get_cv2_sprite


class RenderingBackend(abc.ABC):
    """Abstract base class for rendering backends."""
    
    @abc.abstractmethod
    def draw_rectangle(self, x: int, y: int, width: int, height: int, 
                      color: Tuple[int, int, int], filled: bool = True, 
                      border_width: int = 0) -> None:
        """Draw a rectangle."""
        pass
    
    @abc.abstractmethod
    def draw_circle(self, center_x: int, center_y: int, radius: int, 
                   color: Tuple[int, int, int], filled: bool = True, 
                   border_width: int = 0) -> None:
        """Draw a circle."""
        pass
    
    @abc.abstractmethod
    def draw_sprite(self, sprite_path: str, center_x: int, center_y: int, width: int, center: bool, color) -> None:    
        "Draw an image"
        pass
    
    @abc.abstractmethod
    def draw_line(self, x1: int, y1: int, x2: int, y2: int, 
                 color: Tuple[int, int, int], width: int) -> None:
        """Draw a line."""
        pass
    
    @abc.abstractmethod
    def draw_text(self, text: str, x: int, y: int, color: Tuple[int, int, int]) -> None:
        """Draw text."""
        pass
    
    @abc.abstractmethod
    def clear_screen(self, color: Tuple[int, int, int]) -> None:
        """Clear the screen with a color."""
        pass
    
    @abc.abstractmethod
    def get_surface(self) -> Union[pygame.Surface, np.ndarray]:
        """Get the drawing surface."""
        pass
    
    @abc.abstractmethod
    def draw_cached_background(self) -> None:
        """Draw the cached background if available."""
        pass


class PygameBackend(RenderingBackend):
    """Pygame-based rendering backend."""
    
    def __init__(self, width: int, height: int):
        """Initialize pygame backend."""
        self.width = width
        self.height = height
        self.screen = pygame.Surface((width, height))
        self.font = pygame.font.Font(None, 24)
        
        # Sprite cache: (sprite_path, width, color_tuple, center) -> scaled_sprite
        self._sprite_cache: dict[tuple, pygame.Surface] = {}
        
        # Background cache
        self._background_cache: Optional[pygame.Surface] = None
    
    def draw_rectangle(self, x: int, y: int, width: int, height: int, 
                      color: Tuple[int, int, int], filled: bool = True, 
                      border_width: int = 0) -> None:
        """Draw a rectangle using pygame."""
        rect = pygame.Rect(x, y, width, height)
        if filled:
            pygame.draw.rect(self.screen, color, rect)
        if border_width > 0:
            pygame.draw.rect(self.screen, (128, 128, 128), rect, border_width)
    
    def draw_circle(self, center_x: int, center_y: int, radius: int, 
                   color: Tuple[int, int, int], filled: bool = True, 
                   border_width: int = 0) -> None:
        """Draw a circle using pygame."""
        if filled:
            pygame.draw.circle(self.screen, color, (center_x, center_y), radius)
        if border_width > 0:
            pygame.draw.circle(self.screen, (128, 128, 128), (center_x, center_y), radius, border_width)
    
    def draw_sprite(self, sprite_path: str, x: int, y: int, width: int, center: bool = False, color = (255, 255, 255)) -> None:
        """Draw a PNG image (sprite) at the given position on the screen."""
        # Create cache key
        color_tuple = tuple(color) if hasattr(color, '__iter__') else (255, 255, 255)
        cache_key = (sprite_path, width, color_tuple, center)
        
        # Check cache first
        if cache_key in self._sprite_cache:
            sprite = self._sprite_cache[cache_key]
        else:
            # Try to get preloaded sprite first
            sprite = get_pygame_sprite(sprite_path)
            
            # If not preloaded, load from disk (fallback for backward compatibility)
            if sprite is None:
                sprite = pygame.image.load(sprite_path).convert_alpha()

            sprite_height = int(sprite.get_height() * (width / sprite.get_width()))
            sprite = pygame.transform.scale(sprite, (width, sprite_height))

            if color != (255, 255, 255):
                tinted = sprite.copy()
                tint_surface = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
                tint_surface.fill(color)
                tinted.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                sprite = tinted
            
            # Cache the scaled and tinted sprite
            self._sprite_cache[cache_key] = sprite
        
        # Adjust position if center is True
        if center:
            x = int(x - sprite.get_width() / 2)
            y = int(y - sprite.get_height() / 2)

        self.screen.blit(sprite, (x, y))
        
    def draw_line(self, x1: int, y1: int, x2: int, y2: int, 
                 color: Tuple[int, int, int], width: int) -> None:
        """Draw a line using pygame."""
        pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), width)
    
    def draw_text(self, text: str, x: int, y: int, color: Tuple[int, int, int]) -> None:
        """Draw text using pygame."""
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))
    
    def clear_screen(self, color: Tuple[int, int, int]) -> None:
        """Clear the screen using pygame."""
        self.screen.fill(color)
    
    def set_background_cache(self, background: pygame.Surface) -> None:
        """Set a cached background to blit instead of redrawing."""
        self._background_cache = background.copy()
    
    def clear_background_cache(self) -> None:
        """Clear the background cache."""
        self._background_cache = None
    
    def draw_cached_background(self) -> None:
        """Draw the cached background if available."""
        if self._background_cache is not None:
            self.screen.blit(self._background_cache, (0, 0))
    
    def get_surface(self) -> pygame.Surface:
        """Get the pygame surface."""
        return self.screen


class CV2Backend(RenderingBackend):
    """OpenCV-based rendering backend."""
    
    def __init__(self, width: int, height: int):
        """Initialize OpenCV backend."""
        self.width = width
        self.height = height
        self.frame = np.full((height, width, 3), (255, 255, 255), dtype=np.uint8)
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.6
        self.font_thickness = 2
        
        # Sprite cache: (sprite_path, width, color_tuple, center) -> dict with sprite data
        self._sprite_cache: dict[tuple, dict] = {}
        
        # Background cache
        self._background_cache: Optional[np.ndarray] = None
    
    def _rgb_to_bgr(self, color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Convert RGB color to BGR for OpenCV."""
        return (color[2], color[1], color[0])
    
    def draw_rectangle(self, x: int, y: int, width: int, height: int, 
                      color: Tuple[int, int, int], filled: bool = True, 
                      border_width: int = 0) -> None:
        """Draw a rectangle using OpenCV."""
        bgr_color = self._rgb_to_bgr(color)
        x2, y2 = x + width, y + height
        
        if filled:
            cv2.rectangle(self.frame, (x, y), (x2, y2), bgr_color, -1)
        if border_width > 0:
            cv2.rectangle(self.frame, (x, y), (x2, y2), (128, 128, 128), border_width)
    
    def draw_circle(self, center_x: int, center_y: int, radius: int, 
                   color: Tuple[int, int, int], filled: bool = True, 
                   border_width: int = 0) -> None:
        """Draw a circle using OpenCV."""
        bgr_color = self._rgb_to_bgr(color)
        thickness = -1 if filled else border_width
        
        cv2.circle(self.frame, (center_x, center_y), radius, bgr_color, thickness)
    
    def draw_sprite(
        self,
        sprite_path: str,
        x: int,
        y: int,
        width: int,
        center: bool = False,
        color: tuple = (255, 255, 255)  
    ) -> None:
        """Draw a PNG image (sprite) at the given position on the frame with optional color tint."""
        # Create cache key
        color_tuple = tuple(color) if hasattr(color, '__iter__') else (255, 255, 255)
        cache_key = (sprite_path, width, color_tuple, center)
        
        # Check cache first
        if cache_key in self._sprite_cache:
            sprite_data = self._sprite_cache[cache_key]
            sprite = sprite_data['sprite'].copy()
            h = sprite_data['h']
            w = sprite_data['w']
            has_alpha = sprite_data['has_alpha']
            if has_alpha:
                alpha = sprite_data['alpha'].copy()
            else:
                alpha = 1.0
        else:
            # Try to get preloaded sprite first
            sprite = get_cv2_sprite(sprite_path)
            
            # If not preloaded, load from disk (fallback for backward compatibility)
            if sprite is None:
                sprite = cv2.imread(sprite_path, cv2.IMREAD_UNCHANGED)
                if sprite is None:
                    raise FileNotFoundError(f"Sprite not found at: {sprite_path}")
            else:
                sprite = sprite.copy()  # Copy preloaded sprite
            
            sprite = cv2.resize(sprite, (width, width), interpolation=cv2.INTER_AREA)
            h, w = sprite.shape[:2]

            # Check if sprite has alpha channel
            has_alpha = sprite.shape[2] == 4
            if has_alpha:
                alpha = sprite[:, :, 3] / 255.0
                alpha = alpha[:, :, None]
                bgr = sprite[:, :, :3].astype(float)
            else:
                alpha = 1.0
                bgr = sprite[:, :, :3].astype(float)

            # Apply color tinting
            tint = np.array(color[::-1]) / 255.0
            bgr = np.clip(bgr * tint, 0, 255)
            
            # Cache the processed sprite data
            sprite_uint8 = bgr.astype(np.uint8)
            cache_data = {
                'sprite': sprite_uint8.copy(),
                'h': h,
                'w': w,
                'has_alpha': has_alpha,
                'alpha': alpha.copy() if has_alpha else None
            }
            self._sprite_cache[cache_key] = cache_data
            
            sprite = sprite_uint8

        # Adjust position if center is True
        if center:
            x = int(x - w / 2)
            y = int(y - h / 2)

        # Apply alpha blending
        bgr_float = sprite.astype(float)
        self.frame[y:y+h, x:x+w] = (
            bgr_float * alpha + self.frame[y:y+h, x:x+w] * (1 - alpha)
        ).astype(self.frame.dtype)  
    
    def draw_line(self, x1: int, y1: int, x2: int, y2: int, 
                 color: Tuple[int, int, int], width: int) -> None:
        """Draw a line using OpenCV."""
        bgr_color = self._rgb_to_bgr(color)
        cv2.line(self.frame, (x1, y1), (x2, y2), bgr_color, width)
    
    def draw_text(self, text: str, x: int, y: int, color: Tuple[int, int, int]) -> None:
        """Draw text using OpenCV."""
        bgr_color = self._rgb_to_bgr(color)
        cv2.putText(self.frame, text, (x, y), self.font, self.font_scale, 
                   bgr_color, self.font_thickness)
    
    def clear_screen(self, color: Tuple[int, int, int]) -> None:
        """Clear the screen using OpenCV."""
        bgr_color = self._rgb_to_bgr(color)
        self.frame = np.full((self.height, self.width, 3), bgr_color, dtype=np.uint8)
    
    def set_background_cache(self, background: np.ndarray) -> None:
        """Set a cached background to blit instead of redrawing."""
        self._background_cache = background.copy()
    
    def clear_background_cache(self) -> None:
        """Clear the background cache."""
        self._background_cache = None
    
    def draw_cached_background(self) -> None:
        """Draw the cached background if available."""
        if self._background_cache is not None:
            self.frame = self._background_cache.copy()
    
    def get_surface(self) -> np.ndarray:
        """Get the numpy array frame."""
        return self.frame
