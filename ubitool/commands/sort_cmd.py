"""Sort command implementation for ubitool."""

import os
import sys
import typer


def sort_command(
    file: str = typer.Argument(None, help="File to sort. If not specified, reads from stdin."),
    reverse: bool = typer.Option(False, "-r", "--reverse", help="Reverse the result of comparisons.")
):
    """Sort lines of text file."""
    
    try:
        if file is None:
            # Read from stdin
            lines = sys.stdin.readlines()
        else:
            # Check if file exists
            if not os.path.exists(file):
                print(f"sort: cannot read: {file}: No such file or directory")
                raise typer.Exit(1)
            
            # Read all lines from the file
            with open(file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        
        # Sort the lines
        # Keep newlines intact by sorting with them, but strip for comparison
        sorted_lines = sorted(lines, key=lambda x: x.rstrip('\n'), reverse=reverse)
        
        # Output the sorted lines
        for line in sorted_lines:
            print(line, end='')  # Don't add extra newline since lines already have them
            
    except PermissionError:
        print(f"sort: {file}: Permission denied")
        raise typer.Exit(1)
    except Exception as e:
        print(f"sort: error reading '{file}': {e}")
        raise typer.Exit(1)