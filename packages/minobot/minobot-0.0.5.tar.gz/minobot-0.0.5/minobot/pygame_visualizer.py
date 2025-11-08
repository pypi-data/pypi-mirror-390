"""
Pygame-based visualization for maze and robot.
"""

import pygame
import time
from typing import List, Callable
from .maze import Maze
from .robot import Robot, RobotInstructionLimitException
from .instructions import Instruction, set_context
from .base_visualizer import BaseVisualizer
from .rendering_backend import PygameBackend

class PygameVisualizer(BaseVisualizer):
    """Pygame-based visualizer for maze navigation."""
    
    def __init__(self, maze: Maze, robot: Robot, cell_size: int = 40, show_info: bool = True):
        """
        Initialize the visualizer.
        
        Args:
            maze: The maze to visualize
            robot: The robot to visualize
            cell_size: Size of each cell in pixels
            show_info: If True, displays status information panel
        """
        # Calculate window size
        self.width = maze.width * cell_size
        self.height = maze.height * cell_size + (60 if show_info else 0)  # Extra space for info only if show_info is True
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("MinoBot")
        
        # Initialize backend
        backend = PygameBackend(self.width, self.height)
        
        # Initialize base visualizer
        super().__init__(maze, robot, cell_size, show_info, backend)
        
        # Animation state
        self.running = False
        self.paused = False
    
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def update_display(self):
        """Update the display with current state."""
        # Render frame using base visualizer
        self.render_frame(self.backend)
        
        # Copy from backend surface to pygame screen
        self.screen.blit(self.backend.get_surface(), (0, 0))
        pygame.display.flip()
    
    def run_with_instructions(self, instructions: List[Instruction], delay: int = 500):
        """
        Run the visualization with a list of instructions.
        
        Args:
            instructions: List of instructions to execute
            delay: Delay between moves in milliseconds
        """
        self.running = True
        instruction_index = 0
        
        # Show initial state
        self.update_display()
        
        while self.running and instruction_index < len(instructions):
            self.handle_events()
            
            if not self.paused:
                instruction = instructions[instruction_index]
                success = instruction.execute(self.robot, self.maze)
                
                instruction_index += 1
                self.update_display()
                time.sleep(delay / 1000.0)
                
                # Check if robot reached the end
                if self.robot.has_reached_end(self.maze):
                    break
        
        # Keep window open after completion
        while self.running:
            self.handle_events()
            self.update_display()
            time.sleep(0.1)
        
        pygame.quit()
    

    def add_frame(self):
        """Add a frame to the display."""
        self.handle_events()
        self.update_display()
        time.sleep(0.1)
    
    def run_with_simple_function(self, func: Callable):
        """
        Run the visualization with a simple function that uses the new instruction system.
        
        Args:
            func: Function that uses simple instructions like move(), turn_left(), etc.
        """
        # Set the global context for the instruction functions
        set_context(self.robot, self.maze, self)
        
        self.running = True
        
        # Show initial state
        self.update_display()
        
        try:
            success = func()
        except RobotInstructionLimitException as e:
            print(e)
        # Keep window open after completion
        while self.running:
            self.handle_events()
            self.update_display()
            time.sleep(0.1)
        
        pygame.quit()
        return success

    def show_initial_setup(self):
        """Display the initial setup of the maze and robot in a Pygame window until closed by the user."""
        self.update_display()
        self.running = True
        while self.running:
            self.handle_events()
            self.update_display()
            time.sleep(0.1)
        pygame.quit() 