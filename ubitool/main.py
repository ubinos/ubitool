#!/usr/bin/env python3

import typer
import ipdb

# Import command implementations
from .commands.tail_cmd import tail_command
from .commands.htail_cmd import htail_command
from .commands.shtail_cmd import shtail_command
from .commands.ssend_cmd import ssend_command
from .commands.stssend_cmd import stssend_command
from .commands.shell_cmd import shell_command
from .commands.stshell_cmd import stshell_command
from .commands.ls_cmd import ls_command
from .commands.sort_cmd import sort_command
from .commands.json_cmd import json_command
from .commands.libmgr_cmd import libmgr_command
from .commands.configsel_cmd import configsel_command

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


# Register commands
app.command(name="tail")(tail_command)
app.command(name="htail")(htail_command)
app.command(name="shtail")(shtail_command)  
app.command(name="ssend")(ssend_command)
app.command(name="stssend")(stssend_command)
app.command(name="shell")(shell_command)
app.command(name="stshell")(stshell_command)
app.command(name="ls")(ls_command)
app.command(name="sort")(sort_command)
app.command(name="json")(json_command)
app.command(name="libmgr")(libmgr_command)
app.command(name="configsel")(configsel_command)


if __name__ == "__main__":
    app()