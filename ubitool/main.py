#!/usr/bin/env python3

import os
import subprocess
import glob
import sys
import typer
import ipdb

__version__ = "1.0.0"

app = typer.Typer(help="ubitool is a toolbox for ubinos.")

# Global debug flag
debug_mode = False


def version_callback(value: bool):
    if value:
        typer.echo(f"ubitool version {__version__}")
        raise typer.Exit()


def debug_callback(value: bool):
    global debug_mode
    if value:
        debug_mode = True
        print("Debug mode enabled — entering ipdb before main()")
        ipdb.set_trace()


@app.callback()
def main(
    version: bool = typer.Option(False, "-v", "--version", callback=version_callback, help="Show the version and exit."),
    debug: bool = typer.Option(False, "-d", "--debug", callback=debug_callback, help="Enable debug mode (interactive debugging with ipdb).")
):
    """ubitool is a toolbox for ubinos."""
    pass


@app.command()
def tail(
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


@app.command()
def htail(
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
    _execute_htail_logic(file, lines, bytes_count, reset, last, keep)


@app.command()
def shell(
    command: str = typer.Argument(..., help="Shell command to execute (use quotes for complex commands)."),
    timeout: int = typer.Option(30, "--timeout", help="Command execution timeout in seconds."),
    capture_stderr: bool = typer.Option(False, "--capture-stderr", help="Capture and display stderr output as well.")
):
    """Execute a shell command and display the output."""
    
    try:
        if capture_stderr:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Print stdout
            if result.stdout:
                print(result.stdout, end='')
            
            # Print stderr
            if result.stderr:
                print(result.stderr, end='')
            
            # Exit with the same code as the command
            if result.returncode != 0:
                raise typer.Exit(result.returncode)
        else:
            result = subprocess.run(
                command,
                shell=True,
                text=True,
                timeout=timeout
            )
            
            # Exit with the same code as the command
            if result.returncode != 0:
                raise typer.Exit(result.returncode)
                
    except subprocess.TimeoutExpired:
        print(f"Error: Command timed out after {timeout} seconds")
        raise typer.Exit(1)
    except Exception as e:
        print(f"Error executing command '{command}': {e}")
        raise typer.Exit(1)


@app.command()
def ls(
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


def _get_new_content_as_string(file: str, position_file: str, last_position: int, lines: int, bytes_count: int, update_position: bool = True) -> tuple[str, bool]:
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


def _read_new_content(file: str, position_file: str, last_position: int, lines: int, bytes_count: int, update_position: bool = True) -> bool:
    """Helper function to read new content from file since last position.
    Returns True if new content was found and displayed, False otherwise.
    If update_position is False, the position file will not be updated (keep mode)."""
    # Use the shared function to get content as string
    content_str, found_content = _get_new_content_as_string(file, position_file, last_position, lines, bytes_count, update_position)
    
    if found_content:
        print(content_str, end='')
        return True
    
    return False


@app.command()
def shtail(
    path: str = typer.Argument("~/Workspace/log/tmux", help="Directory containing byobu/tmux log files."),
    target_session: str = typer.Option(..., "-t", "--target-session", help="Target byobu/tmux session name."),
    lines: int = typer.Option(None, "-n", "--lines", help="Maximum number of new lines to display."),
    bytes_count: int = typer.Option(None, "-c", "--bytes", help="Maximum number of new bytes to display. (Overrides -n if both specified)"),
    reset: bool = typer.Option(False, "--reset", help="Reset the saved position and read from the beginning."),
    last: bool = typer.Option(False, "--last", help="Mark current end of file as read (skip to end without displaying)."),
    keep: bool = typer.Option(False, "--keep", help="Do not update last read position.")
):
    """Execute htail on the latest byobu/tmux session log file.
    
    Finds and reads the latest log file matching the pattern:
    PATH/session_<target-session>_window_0_pane_0_*.log"""
    
    import glob as glob_module
    
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
        
        # Build the pattern for byobu/tmux log files
        pattern = os.path.join(path, f"session_{target_session}_window_0_pane_0_*.log")
        
        # Find matching log files
        log_files = glob_module.glob(pattern)
        
        if not log_files:
            print(f"Error: No log files found matching pattern: {pattern}")
            raise typer.Exit(1)
        
        # Sort by modification time and get the latest file
        latest_file = max(log_files, key=os.path.getmtime)
        
        # Reuse htail logic by calling the same functions
        _execute_htail_logic(latest_file, lines, bytes_count, reset, last, keep)
        
    except Exception as e:
        print(f"Error in shtail: {e}")
        raise typer.Exit(1)


def _get_htail_content_for_session(target_session: str, lines: int = None, bytes_count: int = None, keep: bool = True, output_path: str = None) -> str:
    """Get new content from byobu/tmux session log using htail logic.
    Returns the new content as a string.
    This function is used by stssend to read session output."""
    import glob as glob_module
    
    # Use provided output_path or default log path for byobu/tmux sessions
    log_path = os.path.expanduser(output_path) if output_path else os.path.expanduser("~/Workspace/log/tmux")
    
    try:
        # Build the pattern for byobu/tmux log files
        pattern = os.path.join(log_path, f"session_{target_session}_window_0_pane_0_*.log")
        
        # Find matching log files
        log_files = glob_module.glob(pattern)
        
        if not log_files:
            return ""
        
        # Sort by modification time and get the latest file
        latest_file = max(log_files, key=os.path.getmtime)
        
        # Check if file exists
        if not os.path.exists(latest_file):
            return ""
        
        # Set default values if neither option is specified
        if lines is None and bytes_count is None:
            lines = 50  # Default to 50 lines for session monitoring
        
        if lines is not None and lines <= 0:
            return ""
        
        if bytes_count is not None and bytes_count <= 0:
            return ""
        
        # Get the position file path (same directory as the target file)
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
        
        # Get new content using htail logic
        content_str, found_content = _get_new_content_as_string(latest_file, position_file, last_position, lines, bytes_count, not keep)
        
        return content_str if found_content else ""
        
    except Exception as e:
        print(f"Error reading session output: {e}")
        return ""


def _execute_htail_logic(file: str, lines: int, bytes_count: int, reset: bool, last: bool, keep: bool):
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
        _read_new_content(file, position_file, last_position, lines, bytes_count, not keep)
            
    except Exception as e:
        print(f"Error reading file '{file}': {e}")


@app.command()
def ssend(
    keys: list[str] = typer.Argument(..., help="Keys to send."),
    target_session: str = typer.Option(..., "-t", "--target-session", help="Target byobu/tmux session name.")
):
    """Retry sending keys through byobu/tmux session"""
    
    try:
        # Build the byobu/tmux send-keys command
        command = ["byobu", "send-keys", "-t", target_session] + keys
        
        # Execute the command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )
        
        # Check if the command was successful
        if result.returncode != 0:
            print(f"Error: Failed to send keys to session '{target_session}'")
            if result.stderr:
                print(f"Error details: {result.stderr.strip()}")
            raise typer.Exit(1)
        
        # If there's any output, print it
        if result.stdout:
            print(result.stdout, end='')
        if result.stderr:
            print(result.stderr, end='')
            
    except FileNotFoundError:
        print("Error: byobu/tmux command not found. Please make sure byobu/tmux is installed.")
        raise typer.Exit(1)
    except Exception as e:
        print(f"Error executing byobu/tmux send-keys: {e}")
        raise typer.Exit(1)


@app.command()
def stssend(
    keys: list[str] = typer.Argument(..., help="Keys to send."),
    target_session: str = typer.Option(..., "-t", "--target-session", help="Target byobu/tmux session name."),
    expect: str = typer.Option(..., "--expect", help="Expected string in the output."),
    retry: int = typer.Option(10, "--retry", help="Maximum number of retries."),
    retry_interval: int = typer.Option(1, "--retry-interval", help="Interval between retries in seconds."),
    timeout: int = typer.Option(30, "--timeout", help="Timeout for each command execution in seconds."),
    output_path: str = typer.Option("~/Workspace/log/tmux", "--output-path", help="Directory containing byobu/tmux log files. Finds and reads the latest log file matching the pattern: PATH/session_<target-session>_window_0_pane_0_*.log")
):
    """Retry sending keys through byobu/tmux session (strict ssend).
    
    This command repeatedly sends keys until the output
    contains the expected string or the retry limit is reached.
    
    Output is get with the shtail command logic"""
    
    import time

    # Clear output before sending keys
    _get_htail_content_for_session(target_session, lines=1, keep=False, output_path=output_path) # Clear output

    for attempt in range(1, retry + 1):
        try:
            print(f"Attempt {attempt}/{retry}: Sending keys to session '{target_session}'...")
            
            # Send keys using ssend logic
            command = ["byobu", "send-keys", "-t", target_session] + keys
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                print(f"Error: Failed to send keys to session '{target_session}'")
                if result.stderr:
                    print(f"Error details: {result.stderr.strip()}")
                if attempt < retry:
                    print(f"Retrying in {retry_interval} second(s)...")
                    time.sleep(retry_interval)
                continue
            
            # Wait a moment for the command to execute and produce output
            time.sleep(0.5)
            
            # Get output using htail logic
            recent_output = _get_htail_content_for_session(target_session, lines=50, keep=True, output_path=output_path)
            
            if not recent_output:
                print(f"Warning: No new output found for session '{target_session}'")
                if attempt < retry:
                    print(f"Retrying in {retry_interval} second(s)...")
                    time.sleep(retry_interval)
                continue
            
            # Check if expected string is in the output
            if expect in recent_output:
                print(f"Success: Expected string '{expect}' found in output after {attempt} attempt(s)")
                # Show the relevant output
                if recent_output.strip():
                    print("Recent output:")
                    print(recent_output.strip())
                return
            else:
                print(f"Expected string '{expect}' not found in recent output")
                if attempt < retry:
                    print(f"Retrying in {retry_interval} second(s)...")
                    time.sleep(retry_interval)
                
        except subprocess.TimeoutExpired:
            print(f"Attempt {attempt}: Command timed out after {timeout} seconds")
            if attempt < retry:
                print(f"Retrying in {retry_interval} second(s)...")
                time.sleep(retry_interval)
        except FileNotFoundError:
            print("Error: byobu/tmux command not found. Please make sure byobu/tmux is installed.")
            raise typer.Exit(1)
        except Exception as e:
            print(f"Attempt {attempt}: Error executing command: {e}")
            if attempt < retry:
                print(f"Retrying in {retry_interval} second(s)...")
                time.sleep(retry_interval)
    
    print(f"Failed: Expected string '{expect}' not found after {retry} attempts")
    raise typer.Exit(1)

@app.command()
def stshell(
    command: str = typer.Argument(..., help="Shell command to execute (use quotes for complex commands)."),
    expect: str = typer.Option(..., "--expect", help="Expected string in the output."),
    retry: int = typer.Option(10, "--retry", help="Maximum number of retries."),
    timeout: int = typer.Option(30, "--timeout", help="Timeout for each command execution in seconds."),
    retry_interval: int = typer.Option(1, "--retry-interval", help="Interval between retries in seconds."),
    capture_stderr: bool = typer.Option(False, "--capture-stderr", help="Capture and display stderr output as well.")
):
    """Retry shell command until expected result appears (strict shell).
    
    This command repeatedly executes a shell command until the output
    contains the expected string or the retry limit is reached."""
    
    import time
    
    for attempt in range(1, retry + 1):
        try:
            print(f"Attempt {attempt}/{retry}: Executing command...")
            
            if capture_stderr:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                output = result.stdout + result.stderr
                
                # Print the output
                if result.stdout:
                    print(result.stdout, end='')
                if result.stderr:
                    print(result.stderr, end='')
                
            else:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                output = result.stdout
                
                # Print stdout only
                if result.stdout:
                    print(result.stdout, end='')
            
            # Check if expected string is in the output
            if expect in output:
                print(f"Success: Expected string '{expect}' found in output after {attempt} attempt(s)")
                return
            else:
                print(f"Expected string '{expect}' not found in output")
                if attempt < retry:
                    print(f"Retrying in {retry_interval} second(s)...")
                    time.sleep(retry_interval)
                
        except subprocess.TimeoutExpired:
            print(f"Attempt {attempt}: Command timed out after {timeout} seconds")
            if attempt < retry:
                print(f"Retrying in {retry_interval} second(s)...")
                time.sleep(retry_interval)
        except Exception as e:
            print(f"Attempt {attempt}: Error executing command '{command}': {e}")
            if attempt < retry:
                print(f"Retrying in {retry_interval} second(s)...")
                time.sleep(retry_interval)
    
    print(f"Failed: Expected string '{expect}' not found after {retry} attempts")
    raise typer.Exit(1)


@app.command()
def sort(
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
    except UnicodeDecodeError:
        print(f"sort: {file}: Invalid encoding (not UTF-8)")
        raise typer.Exit(1)
    except Exception as e:
        if file:
            print(f"sort: error reading file '{file}': {e}")
        else:
            print(f"sort: error reading from stdin: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()