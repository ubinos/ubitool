"""Tail command implementation for ubitool."""

import os
import typer


def tail_command(
    file: str = typer.Argument(..., help="Path to the file to read."),
    lines: int = typer.Option(None, "-n", "--lines", help="Number of lines to display from the end of the file."),
    bytes_count: int = typer.Option(None, "-c", "--bytes", help="Number of bytes to display from the end of the file. (Overrides -n if both specified)")
):
    """Print the last part of a file."""
    
    # Check if file exists
    if not os.path.exists(file):
        print(f"Warning: File '{file}' does not exist.")
        return
    
    # Set default values if neither option is specified
    if lines is None and bytes_count is None:
        lines = 10  # Default to 10 lines
    
    try:
        if bytes_count is not None:
            # Read the file and get the last N bytes
            if bytes_count <= 0:
                print("Warning: Number of bytes must be greater than 0.")
                return
            
            with open(file, 'rb') as f:
                f.seek(0, 2)  # Go to end of file
                file_size = f.tell()
                
                if file_size == 0:
                    return
                
                # Read from the end
                start_pos = max(0, file_size - bytes_count)
                f.seek(start_pos)
                content = f.read(bytes_count)
                
                # Print as text, handling encoding
                try:
                    print(content.decode('utf-8'), end='')
                except UnicodeDecodeError:
                    print(content.decode('utf-8', errors='replace'), end='')
        else:
            # Read the file and get the last N lines
            if lines <= 0:
                print("Warning: Number of lines must be greater than 0.")
                return
            
            # Read as binary first to avoid encoding errors  
            with open(file, 'rb') as f:
                content = f.read()
            
            # Decode with error handling
            try:
                text_content = content.decode('utf-8')
            except UnicodeDecodeError:
                text_content = content.decode('utf-8', errors='replace')
            
            file_lines = text_content.splitlines(keepends=True)
            last_lines = file_lines[-lines:] if len(file_lines) >= lines else file_lines
            
            # Output the lines
            for line in last_lines:
                print(line, end='')  # Don't add extra newline since lines already have them
            
    except Exception as e:
        print(f"Error reading file '{file}': {e}")