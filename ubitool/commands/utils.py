"""Common utility functions for ubitool commands."""

import os


def get_new_content_as_string(file: str, position_file: str, last_position: int, lines: int, bytes_count: int, update_position: bool = True) -> tuple[str, bool]:
    """Helper function to read new content from file since last position and return as string.
    Returns tuple of (content_string, found_new_content).
    If update_position is False, the position file will not be updated (keep mode)."""
    try:
        if bytes_count is not None:
            # Handle bytes mode
            with open(file, 'rb') as f:
                f.seek(last_position)
                new_content = f.read()
                current_position = f.tell()
            
            if new_content:
                # Get the last N bytes of new content
                if len(new_content) > bytes_count:
                    output_content = new_content[-bytes_count:]
                else:
                    output_content = new_content
                
                # Convert to text, handling encoding
                try:
                    content_str = output_content.decode('utf-8')
                except UnicodeDecodeError:
                    content_str = output_content.decode('utf-8', errors='replace')
                
                # Save the new position (only if update_position is True)
                if update_position:
                    with open(position_file, 'w') as f:
                        f.write(str(current_position))
                return content_str, True
        else:
            # Handle lines mode - read as binary first to avoid encoding errors
            with open(file, 'rb') as f:
                f.seek(last_position)
                new_content_bytes = f.read()
                current_position = f.tell()
            
            if new_content_bytes:
                # Decode with error handling
                try:
                    new_content = new_content_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    # If UTF-8 fails, try with replacement characters
                    new_content = new_content_bytes.decode('utf-8', errors='replace')
                
                # Split into lines and get the last N lines of new content
                new_lines = new_content.splitlines(keepends=True)
                
                # If we have more lines than requested, show only the last N lines
                if lines and len(new_lines) > lines:
                    output_lines = new_lines[-lines:]
                else:
                    output_lines = new_lines
                
                # Join lines into string
                content_str = ''.join(output_lines)
                
                # Save the new position (only if update_position is True)
                if update_position:
                    with open(position_file, 'w') as f:
                        f.write(str(current_position))
                return content_str, True
        
        return "", False
        
    except Exception as e:
        print(f"Error reading file '{file}': {e}")
        return "", False


def read_new_content(file: str, position_file: str, last_position: int, lines: int, bytes_count: int, update_position: bool = True) -> bool:
    """Helper function to read new content from file since last position.
    Returns True if new content was found and displayed, False otherwise.
    If update_position is False, the position file will not be updated (keep mode)."""
    # Use the shared function to get content as string
    content_str, found_content = get_new_content_as_string(file, position_file, last_position, lines, bytes_count, update_position)
    
    if found_content:
        print(content_str, end='')
        return True
    
    return False


def execute_htail_logic(file: str, lines: int, bytes_count: int, reset: bool, last: bool, keep: bool):
    """Execute htail logic on a specific file - shared between htail and shtail commands"""
    import time
    
    # Check if file exists
    if not os.path.exists(file):
        print(f"Warning: File '{file}' does not exist.")
        return
    
    # Set default values if neither option is specified
    if lines is None and bytes_count is None:
        lines = 10  # Default to 10 lines
    
    if lines is not None and lines <= 0:
        print("Warning: Number of lines must be greater than 0.")
        return
    
    if bytes_count is not None and bytes_count <= 0:
        print("Warning: Number of bytes must be greater than 0.")
        return
    
    try:
        # Get the position file path (same directory as the target file)
        file_dir = os.path.dirname(os.path.abspath(file))
        file_name = os.path.basename(file)
        position_file = os.path.join(file_dir, f".{file_name}.htail")
        
        # Handle reset option
        if reset:
            if os.path.exists(position_file):
                os.remove(position_file)
            last_position = 0
        else:
            # Read the last saved position
            last_position = 0
            if os.path.exists(position_file):
                try:
                    with open(position_file, 'r') as f:
                        last_position = int(f.read().strip())
                except (ValueError, IOError):
                    last_position = 0
        
        # Handle last option (mark current end as read)
        if last:
            with open(file, 'rb') as f:
                f.seek(0, 2)  # Go to end of file
                current_position = f.tell()
            with open(position_file, 'w') as f:
                f.write(str(current_position))
            return
        
        # Read new content (keep mode affects whether position is updated)
        read_new_content(file, position_file, last_position, lines, bytes_count, not keep)
            
    except Exception as e:
        print(f"Error reading file '{file}': {e}")


def get_htail_content_for_session(target_session: str, lines: int = None, bytes_count: int = None, keep: bool = True, output_path: str = None) -> str:
    """Get new content from tmux session log using htail logic.
    Returns the new content as a string.
    This function is used by stssend to read session output."""
    import glob as glob_module
    
    # Use provided output_path or default log path for tmux sessions
    log_path = os.path.expanduser(output_path) if output_path else os.path.expanduser("~/Workspace/log/tmux")
    
    try:
        # Build the pattern for tmux log files
        pattern = os.path.join(log_path, f"session_{target_session}_window_0_pane_0_*.log")
        
        # Find matching log files
        log_files = glob_module.glob(pattern)
        
        if not log_files:
            return ""  # No log files found
        
        # Sort by modification time and get the latest file
        latest_file = max(log_files, key=os.path.getmtime)
        
        # Get the position file path
        file_dir = os.path.dirname(os.path.abspath(latest_file))
        file_name = os.path.basename(latest_file)
        position_file = os.path.join(file_dir, f".{file_name}.htail")
        
        # Read the last saved position
        last_position = 0
        if os.path.exists(position_file):
            try:
                with open(position_file, 'r') as f:
                    last_position = int(f.read().strip())
            except (ValueError, IOError):
                last_position = 0
        
        # Get new content as string
        content_str, _ = get_new_content_as_string(latest_file, position_file, last_position, lines, bytes_count, not keep)
        return content_str
        
    except Exception as e:
        print(f"Error getting content for session '{target_session}': {e}")
        return ""