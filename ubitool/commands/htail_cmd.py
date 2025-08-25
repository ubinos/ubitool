"""Htail command implementation for ubitool."""

import typer
from .utils import execute_htail_logic


def htail_command(
    file: str = typer.Argument(..., help="Path to the file to read."),
    lines: int = typer.Option(None, "-n", "--lines", help="Maximum number of new lines to display."),
    bytes_count: int = typer.Option(None, "-c", "--bytes", help="Maximum number of new bytes to display. (Overrides -n if both specified)"),
    reset: bool = typer.Option(False, "--reset", help="Reset the saved position and read from the beginning."),
    last: bool = typer.Option(False, "--last", help="Mark current end of file as read (skip to end without displaying)."),
    keep: bool = typer.Option(False, "--keep", help="Do not update last read position.")
):
    """Print the unread portion of a file since last access.
    
    This command tracks the reading position and only displays new content
    added since the last read. The position is saved in a hidden file
    (.FILE.htail) in the same directory as the target file."""
    
    # Use shared htail logic
    execute_htail_logic(file, lines, bytes_count, reset, last, keep)