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
- `htail` - Print the last part of a file with position tracking
- `bhtail` - Print the last part of a file from tmux session with position tracking
- `bsend` - Send keys to a tmux session
- `stbsend` - Send keys to a tmux session and wait for expected output
- `shell` - Execute shell commands
- `stshell` - Execute shell commands and wait for expected output
- `ls` - List directory contents with filtering
- `sort` - Sort lines in files or stdin

## Development

This package is part of the ubinos ecosystem and is designed to work with tmux sessions and log monitoring.

## Requirements

- Python 3.8+
- typer
- ipdb