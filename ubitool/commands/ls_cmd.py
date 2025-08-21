"""Ls command implementation for ubitool."""

import os
import glob
import typer


def ls_command(
    paths: list[str] = typer.Argument(None, help="Paths to list (files or directories). Can include wildcards/patterns. Defaults to current directory if none specified."),
    show_all: bool = typer.Option(False, "-a", "--all", help="Include entries starting with dot (.)")
):
    """List directory contents."""
    
    # If no paths provided, default to current directory
    if not paths:
        paths = ["."]
    
    try:
        # If all paths are files (likely from shell wildcard expansion), list them without separators
        all_files = all(os.path.isfile(path) for path in paths if os.path.exists(path))
        
        # Count directories in paths
        dir_count = sum(1 for path in paths if os.path.exists(path) and os.path.isdir(path))
        
        # Process each path
        for i, path in enumerate(paths):
            # Handle wildcard patterns
            if '*' in path or '?' in path:
                # Use glob for pattern matching
                matches = glob.glob(path)
                if not matches:
                    print(f"ls: cannot access '{path}': No such file or directory")
                    continue
                
                # Sort the matches
                matches.sort()
                
                # If multiple matches, show them as a list
                if len(matches) > 1:
                    for match in matches:
                        if os.path.isfile(match):
                            print(match)
                        elif os.path.isdir(match):
                            print(f"{match}/")
                else:
                    # Single match, handle like regular path
                    match = matches[0]
                    _handle_single_path(match, show_all)
            else:
                # Show directory name only if multiple directories
                show_dir_name = dir_count > 1 and os.path.isdir(path)
                _handle_single_path(path, show_all, show_dir_name)
                
    except Exception as e:
        print(f"Error listing paths: {e}")
        raise typer.Exit(1)


def _handle_single_path(path: str, show_all: bool, show_dir_name: bool = False):
    """Handle a single path (file or directory)"""
    if not os.path.exists(path):
        print(f"ls: cannot access '{path}': No such file or directory")
        return
    
    if os.path.isfile(path):
        # If it's a file, just print the filename
        print(path)
    else:
        # List directory contents
        if show_dir_name:
            print(f"{path}:")
        _list_directory_contents(path, show_all)


def _list_directory_contents(directory: str, show_all: bool):
    """Helper function to list directory contents"""
    try:
        entries = os.listdir(directory)
        
        # Filter hidden files if not showing all
        if not show_all:
            entries = [entry for entry in entries if not entry.startswith('.')]
        
        # Sort entries
        entries.sort()
        
        # Print entries
        for entry in entries:
            print(entry)
            
    except PermissionError:
        print(f"ls: cannot open directory '{directory}': Permission denied")
    except Exception as e:
        print(f"ls: error reading directory '{directory}': {e}")