# ubitool

A toolbox for ubinos development.

## Installation

### Development Installation

To install ubitool in development mode:

```bash
pip install -e .
```

### Regular Installation

To install ubitool:

```bash
pip install .
```

## Usage

After installation, you can use ubitool from the command line:

```bash
ubitool --help
```

### Available Commands

- `tail` - Print the last part of a file
- `htail` - Print unread content of a file with position tracking
- `shtail` - Run `htail` against the latest tmux session log
- `ssend` - Send keys to a tmux session
- `stssend` - Retry sending keys to a tmux session until expected output appears
- `shell` - Execute a shell command
- `stshell` - Retry a shell command until expected output appears
- `ls` - List directory contents or files matching patterns
- `sort` - Sort lines from a file or stdin
- `json` - Read or write JSON/JSON5 files with JMESPath support
- `replace` - Replace text in a file
- `libmgr` - Launch library manager UI
- `configsel` - Launch config selector UI

## Development

This package is part of the ubinos ecosystem and is designed to work with tmux sessions and log monitoring.

## Requirements

- Python 3.8+
- typer
- ipdb
