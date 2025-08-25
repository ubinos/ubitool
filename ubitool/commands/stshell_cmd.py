"""Stshell command implementation for ubitool."""

import subprocess
import time
import typer


def stshell_command(
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