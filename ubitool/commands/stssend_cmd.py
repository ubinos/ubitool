"""Stssend command implementation for ubitool."""

import subprocess
import time
import typer
from .utils import get_htail_content_for_session


def stssend_command(
    keys: list[str] = typer.Argument(..., help="Keys to send."),
    target_session: str = typer.Option(..., "-t", "--target-session", help="Target tmux session name."),
    expect: str = typer.Option(..., "-e", "--expect", help="Expected string in the output."),
    retry: int = typer.Option(10, "-r", "--retry", help="Maximum number of retries."),
    retry_interval: int = typer.Option(1, "--retry-interval", help="Interval between retries in seconds."),
    timeout: int = typer.Option(30, "--timeout", help="Timeout for each command execution in seconds."),
    output_path: str = typer.Option("~/Workspace/log/tmux", "-o", "--output-path", help="Directory containing tmux log files. Finds and reads the latest log file matching the pattern: PATH/session_<target-session>_window_0_pane_0_*.log"),
    cancel_key: list[str] = typer.Option([], "-c", "--cancel-key", help="Key sent before every retry to cancel the previous one.")
):
    """Retry sending keys to tmux session (strict ssend).
    
    This command repeatedly sends keys until the output
    contains the expected string or the retry limit is reached.
    
    Output is get with the shtail command logic
    
    After send cancel key and before resend KEYS, output should be cleared with htail command logic."""

    # Clear output before sending keys
    get_htail_content_for_session(target_session, lines=1, keep=False, output_path=output_path) # Clear output

    for attempt in range(1, retry + 1):
        try:
            print(f"Attempt {attempt}/{retry}: Sending keys to session '{target_session}'...")
            
            # Send keys using ssend logic
            command = ["tmux", "send-keys", "-t", target_session] + keys
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30  # tmux send-keys should be quick
            )
            
            if result.returncode != 0:
                print(f"Error: Failed to send keys to session '{target_session}'")
                if result.stderr:
                    print(f"Error details: {result.stderr.strip()}")
                if attempt < retry:
                    # Send cancel keys if specified (before retry)
                    if cancel_key:
                        print(f"Sending cancel keys: {' '.join(cancel_key)}")
                        for cancel_k in cancel_key:
                            cancel_command = ["tmux", "send-keys", "-t", target_session, cancel_k]
                            subprocess.run(cancel_command, capture_output=True)
                            time.sleep(0.1)  # Short delay between cancel keys
                    
                    print(f"Retrying in {retry_interval} second(s)...")
                    time.sleep(retry_interval)
                continue
            
            # Wait for expected output with timeout
            start_time = time.time()
            found_expected = False
            
            while time.time() - start_time < timeout:
                # Wait a moment before checking output
                time.sleep(1.0)
                
                # Get output using htail logic
                recent_output = get_htail_content_for_session(target_session, lines=50, keep=True, output_path=output_path)
                
                # Check if expected string is in the output
                if recent_output and expect in recent_output:
                    print(f"Success: Expected string '{expect}' found in output after {attempt} attempt(s)")
                    # Show the relevant output
                    if recent_output.strip():
                        print("Recent output:")
                        print(recent_output.strip())
                    found_expected = True
                    break
            
            if found_expected:
                return
            
            # If we reach here, timeout occurred without finding expected string
            print(f"Expected string '{expect}' not found within {timeout} seconds")
            if attempt < retry:
                # Send cancel keys if specified (before retry)
                if cancel_key:
                    print(f"Sending cancel keys: {' '.join(cancel_key)}")
                    for cancel_k in cancel_key:
                        cancel_command = ["tmux", "send-keys", "-t", target_session, cancel_k]
                        subprocess.run(cancel_command, capture_output=True)
                        time.sleep(0.1)  # Short delay between cancel keys
                    
                    # Clear output after sending cancel keys
                    time.sleep(0.5)  # Wait for cancel keys to take effect
                    get_htail_content_for_session(target_session, lines=1, keep=False, output_path=output_path)
                
                print(f"Retrying in {retry_interval} second(s)...")
                time.sleep(retry_interval)
                
        except subprocess.TimeoutExpired:
            print(f"Attempt {attempt}: tmux send-keys command timed out")
            if attempt < retry:
                # Send cancel keys if specified (before retry)
                if cancel_key:
                    print(f"Sending cancel keys: {' '.join(cancel_key)}")
                    for cancel_k in cancel_key:
                        cancel_command = ["tmux", "send-keys", "-t", target_session, cancel_k]
                        subprocess.run(cancel_command, capture_output=True)
                        time.sleep(0.1)  # Short delay between cancel keys
                    
                    # Clear output after sending cancel keys
                    time.sleep(0.5)  # Wait for cancel keys to take effect
                    get_htail_content_for_session(target_session, lines=1, keep=False, output_path=output_path)
                
                print(f"Retrying in {retry_interval} second(s)...")
                time.sleep(retry_interval)
        except FileNotFoundError:
            print("Error: tmux command not found. Please make sure tmux is installed.")
            raise typer.Exit(1)
        except Exception as e:
            print(f"Attempt {attempt}: Error executing command: {e}")
            if attempt < retry:
                # Send cancel keys if specified (before retry)
                if cancel_key:
                    print(f"Sending cancel keys: {' '.join(cancel_key)}")
                    for cancel_k in cancel_key:
                        cancel_command = ["tmux", "send-keys", "-t", target_session, cancel_k]
                        subprocess.run(cancel_command, capture_output=True)
                        time.sleep(0.1)  # Short delay between cancel keys
                    
                    # Clear output after sending cancel keys
                    time.sleep(0.5)  # Wait for cancel keys to take effect
                    get_htail_content_for_session(target_session, lines=1, keep=False, output_path=output_path)
                
                print(f"Retrying in {retry_interval} second(s)...")
                time.sleep(retry_interval)
    
    print(f"Failed: Expected string '{expect}' not found after {retry} attempts")
    raise typer.Exit(1)