"""
Utility functions for displaying videos in Jupyter notebooks.
"""

import base64
from pathlib import Path
from typing import List, Optional
from IPython import display as ipythondisplay


def insert_newlines(s: str, interval: int) -> str:
    """Insert newlines in a string at regular intervals."""
    return '\n'.join(s[i:i+interval] for i in range(0, len(s), interval))


def show_videos(video_path: str = "", prefix: str = "", height: int = 400):
    """
    Display multiple videos in a Jupyter notebook.
    
    Args:
        video_path: Path to the folder containing videos
        prefix: Filter videos, showing only those starting with this prefix
        height: Height of the videos in pixels
    """
    html = []
    for mp4 in Path(video_path).glob(f"{prefix}*.mp4"):
        video_b64 = base64.b64encode(mp4.read_bytes())
        html.append(
            f"""<video alt="{mp4}" autoplay loop controls style="height: {height}px;">
                <source src="data:video/mp4;base64,{insert_newlines(video_b64.decode("ascii"), 1000)}" type="video/mp4" />
            </video>"""
        )
    ipythondisplay.display(ipythondisplay.HTML(data="<br>".join(html)))


def show_single_video(video_path: str, height: int = 400, autoplay: bool = True, loop: bool = True):
    """
    Display a single video in a Jupyter notebook.
    
    Args:
        video_path: Path to the video file
        height: Height of the video in pixels
        autoplay: Whether to autoplay the video
        loop: Whether to loop the video
    """
    video_b64 = base64.b64encode(Path(video_path).read_bytes())
    
    autoplay_attr = "autoplay" if autoplay else ""
    loop_attr = "loop" if loop else ""
    
    html = f"""<video alt="Video" {autoplay_attr} {loop_attr} controls style="height: {height}px;">
        <source src="data:video/mp4;base64,{insert_newlines(video_b64.decode("ascii"), 1000)}" type="video/mp4" />
    </video>"""
    
    ipythondisplay.display(ipythondisplay.HTML(data=html))


def create_video_comparison(video_paths: List[str], titles: Optional[List[str]] = None, 
                           height: int = 300, width: int = 400):
    """
    Create a side-by-side comparison of multiple videos.
    
    Args:
        video_paths: List of paths to video files
        titles: List of titles for each video (optional)
        height: Height of the videos in pixels
        width: Width of each video in pixels
    """
    if titles is None:
        titles = [f"Video {i+1}" for i in range(len(video_paths))]
    
    html_parts = []
    for video_path, title in zip(video_paths, titles):
        video_b64 = base64.b64encode(Path(video_path).read_bytes())
        html_parts.append(
            f"""<div style="display: inline-block; margin: 10px; text-align: center;">
                <h4>{title}</h4>
                <video alt="{title}" autoplay loop controls 
                       style="height: {height}px; width: {width}px;">
                    <source src="data:video/mp4;base64,{insert_newlines(video_b64.decode("ascii"), 1000)}" type="video/mp4" />
                </video>
            </div>"""
        )
    
    html = f"""<div style="text-align: center;">
        {"".join(html_parts)}
    </div>"""
    
    ipythondisplay.display(ipythondisplay.HTML(data=html)) 