"""Shtail command implementation for ubitool."""

import os
import glob as glob_module
import typer
from .utils import execute_htail_logic


def shtail_command(
    path: str = typer.Argument("~/Workspace/log/tmux", help="Directory containing tmux log files."),
    target_session: str = typer.Option(..., "-t", "--target-session", help="Target tmux session name."),
    lines: int = typer.Option(None, "-n", "--lines", help="Maximum number of new lines to display."),
    bytes_count: int = typer.Option(None, "-c", "--bytes", help="Maximum number of new bytes to display. (Overrides -n if both specified)"),
    reset: bool = typer.Option(False, "--reset", help="Reset the saved position and read from the beginning."),
    last: bool = typer.Option(False, "--last", help="Mark current end of file as read (skip to end without displaying)."),
    keep: bool = typer.Option(False, "--keep", help="Do not update last read position.")
):
    """Execute htail on the latest tmux session log file.
    
    Finds and reads the latest log file matching the pattern:
    PATH/session_<target-session>_window_0_pane_0_*.log"""
    
    try:
        # Expand tilde to home directory
        path = os.path.expanduser(path)
        
        # Check if path exists
        if not os.path.exists(path):
            print(f"Error: Directory '{path}' does not exist.")
            raise typer.Exit(1)
        
        if not os.path.isdir(path):
            print(f"Error: '{path}' is not a directory.")
            raise typer.Exit(1)
        
        # Build the pattern for tmux log files
        pattern = os.path.join(path, f"session_{target_session}_window_0_pane_0_*.log")
        
        # Find matching log files
        log_files = glob_module.glob(pattern)
        
        if not log_files:
            print(f"Error: No log files found matching pattern: {pattern}")
            raise typer.Exit(1)
        
        # Sort by modification time and get the latest file
        latest_file = max(log_files, key=os.path.getmtime)
        
        # Reuse htail logic by calling the same functions
        execute_htail_logic(latest_file, lines, bytes_count, reset, last, keep)
        
    except Exception as e:
        print(f"Error in shtail: {e}")
        raise typer.Exit(1)