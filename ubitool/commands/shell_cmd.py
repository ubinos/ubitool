"""Shell command implementation for ubitool."""

import subprocess
import typer


def shell_command(
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