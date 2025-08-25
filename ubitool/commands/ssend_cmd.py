"""Ssend command implementation for ubitool."""

import subprocess
import typer


def ssend_command(
    keys: list[str] = typer.Argument(..., help="Keys to send."),
    target_session: str = typer.Option(..., "-t", "--target-session", help="Target tmux session name.")
):
    """Send keys to tmux session"""
    
    try:
        # Build the tmux send-keys command
        command = ["tmux", "send-keys", "-t", target_session] + keys
        
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
                print(f"Error details: {result.stderr}")
            raise typer.Exit(1)
    
    except FileNotFoundError:
        print("Error: tmux command not found. Please make sure tmux is installed.")
        raise typer.Exit(1)
    except Exception as e:
        print(f"Error executing ssend: {e}")
        raise typer.Exit(1)