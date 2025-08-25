"""JSON command implementation for ubitool."""

import json
import sys
from pathlib import Path
from typing import Optional

import typer

def json_command(subcmd: str, file: str, field: Optional[str] = typer.Option(None, "-f", "--field", help="Print or write only the specified field")):
    """Read or write json file.
    
    Args:
        subcmd: Subcommand (read)
        file: Path to the json target file
        field: Print or write only the specified field
    """
    try:
        file_path = Path(file)
        
        if subcmd == "read":
            if not file_path.exists():
                print(f"Error: File '{file}' not found", file=sys.stderr)
                raise typer.Exit(1)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON in file '{file}': {e}", file=sys.stderr)
                raise typer.Exit(1)
            except UnicodeDecodeError as e:
                print(f"Error: Unable to decode file '{file}': {e}", file=sys.stderr)
                raise typer.Exit(1)
            
            if field:
                try:
                    # First try direct field access (for keys containing dots)
                    if field in data:
                        result = data[field]
                    else:
                        # Navigate through nested fields using dot notation
                        keys = field.split('.')
                        result = data
                        for key in keys:
                            if isinstance(result, dict):
                                result = result[key]
                            else:
                                raise KeyError(f"Cannot access '{key}' on non-dict object")
                    
                    # Pretty print the result
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                except KeyError as e:
                    print(f"Error: Field '{field}' not found in JSON: {e}", file=sys.stderr)
                    raise typer.Exit(1)
            else:
                # Pretty print the entire JSON
                print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"Error: Unknown subcommand '{subcmd}'. Available: read", file=sys.stderr)
            raise typer.Exit(1)
            
    except Exception as e:
        if not isinstance(e, typer.Exit):
            print(f"Error: {e}", file=sys.stderr)
            raise typer.Exit(1)
        raise