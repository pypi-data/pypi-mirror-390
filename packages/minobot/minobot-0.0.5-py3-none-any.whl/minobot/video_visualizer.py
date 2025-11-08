"""
Video-based visualization for maze and robot.
"""

import base64
import cv2
import numpy as np
from pathlib import Path
from typing import List, Callable, Optional
from .maze import Maze
from .robot import Robot, RobotInstructionLimitException
from .instructions import Instruction, set_context
from .base_visualizer import BaseVisualizer
from .rendering_backend import CV2Backend

class NotebookVisualizer(BaseVisualizer):
    """Video-based visualizer for maze navigation."""
    
    def __init__(self, maze: Maze, robot: Robot, cell_size: int = 80, fps: int = 2, show_info: bool = True):
        """
        Initialize the video visualizer.
        
        Args:
            maze: The maze to visualize
            robot: The robot to visualize
            cell_size: Size of each cell in pixels
            fps: Frames per second for the video
            show_info: If True, displays status information panel
        """
        # Calculate video dimensions
        self.width = maze.width * cell_size
        self.height = maze.height * cell_size + (80 if show_info else 0)  # Extra space for info only if show_info is True
        
        # Initialize backend
        backend = CV2Backend(self.width, self.height)
        
        # Initialize base visualizer
        super().__init__(maze, robot, cell_size, show_info, backend)
        
        self.fps = fps
        
        # Video writer
        self.video_writer = None
        self.frames = []
    
    def create_frame(self) -> np.ndarray:
        """Create a single frame of the visualization."""
        # Render frame using base visualizer
        self.render_frame(self.backend)
        
        # Get the frame from backend
        return self.backend.get_surface()
    
    
    def add_frame(self):
        """Add current state as a frame."""
        frame = self.create_frame()
        self.frames.append(frame)
    
    def run_with_instructions(self, instructions: List[Instruction], delay_frames: int = 1) -> List[np.ndarray]:
        """
        Run the visualization with a list of instructions.
        
        Args:
            instructions: List of instructions to execute
            delay_frames: Number of frames to hold each state
            
        Returns:
            List of frames as numpy arrays
        """
        self.frames = []
        
        # Add initial state
        for _ in range(delay_frames):
            self.add_frame()
        
        instruction_index = 0
        
        while instruction_index < len(instructions):
            instruction = instructions[instruction_index]
            success = instruction.execute(self.robot, self.maze)
            
            instruction_index += 1
            # Add frame for this state
            for _ in range(delay_frames):
                self.add_frame()
            
            # Check if robot reached the end
            if self.robot.has_reached_end(self.maze):
                break
        
        self.display_in_notebook(self.frames)
    
    
    def save_video(self, filename: str, frames: Optional[List[np.ndarray]] = None):
        """
        Save frames as a video file.
        
        Args:
            filename: Output video filename
            frames: List of frames to save (uses self.frames if None)
        """
        if frames is None:
            frames = self.frames
        
        if not frames:
            raise ValueError("No frames to save")
        
        # Get frame dimensions
        height, width = frames[0].shape[:2]
        
        # Try different codecs in order of preference
        codecs = ['avc1', 'mp4v', 'XVID', 'MJPG']
        out = None
        
        for codec in codecs:
            try:
                fourcc = cv2.VideoWriter_fourcc(*codec)
                out = cv2.VideoWriter(filename, fourcc, self.fps, (width, height))
                
                if out.isOpened():
                    break
                else:
                    out.release()
                    out = None
            except Exception as e:
                if out:
                    out.release()
                    out = None
        
        if out is None:
            raise RuntimeError("No compatible video codec found")
        
        # Write frames
        for frame in frames:
            out.write(frame)
        
        out.release()
        
        # Verify file was created
        if Path(filename).exists():
            file_size = Path(filename).stat().st_size
        else:
            raise RuntimeError(f"Video file was not created: {filename}")
    
    def display_in_notebook(self, frames: Optional[List[np.ndarray]] = None, 
                           video_path: str = "temp_video.mp4", height: int = 400, use_html: bool = True):
        """
        Display frames in a Jupyter notebook as a video.
        
        Args:
            frames: List of frames to display (uses self.frames if None)
            video_path: Temporary path to save the video
            height: Height of the video in pixels
            use_html: If True, use HTML video element; if False, use IPython Video
        """
        try:
            from IPython import display as ipythondisplay
        except ImportError:
            print("IPython is required for notebook display")
            return
        
        if frames is None:
            frames = self.frames
        
        if not frames:
            print("No frames to display")
            return
        
        # Save video to temporary file
        self.save_video(video_path, frames)
        
        if use_html:
            try:
                # Read video file and encode to base64
                video_b64 = base64.b64encode(Path(video_path).read_bytes())
                
                # Insert newlines for better HTML formatting
                def insert_newlines(s, interval):
                    return '\n'.join(s[i:i+interval] for i in range(0, len(s), interval))
                
                # Create HTML video element
                html = f"""<video alt="Robot Maze Solver" autoplay controls style="height: {height}px;">
                    <source src="data:video/mp4;base64,{insert_newlines(video_b64.decode("ascii"), 1000)}" type="video/mp4" />
                </video>"""
                
                # Display in notebook
                ipythondisplay.display(ipythondisplay.HTML(data=html))
                
            except Exception as e:
                print(f"HTML display failed: {e}")
                print("Falling back to IPython Video display...")
                use_html = False
        
        if not use_html:
            # Use IPython's built-in Video display
            try:
                ipythondisplay.display(ipythondisplay.Video(video_path, embed=True, html_attributes=f'height="{height}"'))
            except Exception as e:
                print(f"IPython Video display failed: {e}")
                print("Video saved to file, but could not display in notebook")
        
        # Clean up temporary file
        try:
            Path(video_path).unlink()
        except:
            pass
    
    def run_with_simple_function(self, func: Callable, delay_frames: int = 2) -> List[np.ndarray]:
        """
        Run the visualization with a simple function that uses the new instruction system.
        
        Args:
            func: Function that uses simple instructions like move(), turn_left(), etc.
            delay_frames: Number of frames to hold each state
            
        Returns:
            List of frames as numpy arrays
        """
        # Set the global context for the instruction functions
        set_context(self.robot, self.maze, self)
        
        self.frames = []
        
        # Add initial state
        for _ in range(delay_frames):
            self.add_frame()
        
        # Call the function - it should use the simple instruction functions
        try:
            success = func()
        except RobotInstructionLimitException as e:
            print(e)

        # Add final state
        for _ in range(delay_frames):
            self.add_frame()
        
        self.display_in_notebook(self.frames)
        return success
    
    def create_image(self) -> np.ndarray:
        """Create a static image of the current state."""
        # Render frame using base visualizer
        self.render_frame(self.backend)
        
        # Get the frame from backend
        return self.backend.get_surface()
    
    def show_initial_setup(self):
        """Display the initial setup of the maze and robot as a static image in a Jupyter notebook."""
        from IPython.display import Image, display
        frame = self.create_image()
        # Encode frame as PNG image
        success, buffer = cv2.imencode('.png', frame, [cv2.IMWRITE_PNG_COMPRESSION, 4])
        if success:
            # Convert to bytes and display
            image_bytes = buffer.tobytes()
            display(Image(data=image_bytes, height=self.height, width=self.width, format='png'))

 