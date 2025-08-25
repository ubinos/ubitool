"""JSON command implementation for ubitool."""

import json
import sys
from pathlib import Path
from typing import Optional

import typer

def json_command(
    file: str,
    read: bool = typer.Option(False, "-r", "--read", help="Print the value of a specified field of the json target file (requires --field)"),
    write: bool = typer.Option(False, "-w", "--write", help="Write a specified value to a specified field of the json target file (requires --field and --value)"),
    field: Optional[str] = typer.Option(None, "-f", "--field", help="Specify a field"),
    value: Optional[str] = typer.Option(None, "-v", "--value", help="Specify a value")
):
    """Print or write json file.
    
    Args:
        file: Path to the json target file
        read: Print the value of a specified field
        write: Write a value to a specified field
        field: Field to read or write
        value: Value to write
    """
    try:
        file_path = Path(file)
        
        # Validate options
        if not read and not write:
            print("Error: Either --read or --write must be specified", file=sys.stderr)
            raise typer.Exit(1)
            
        if read and write:
            print("Error: Cannot specify both --read and --write", file=sys.stderr)
            raise typer.Exit(1)
            
        if read and not field:
            print("Error: --read requires --field", file=sys.stderr)
            raise typer.Exit(1)
            
        if write and (not field or value is None):
            print("Error: --write requires both --field and --value", file=sys.stderr)
            raise typer.Exit(1)
        
        # Read operation
        if read:
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
                if isinstance(result, (dict, list)):
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                else:
                    print(json.dumps(result, ensure_ascii=False))
            except KeyError as e:
                print(f"Error: Field '{field}' not found in JSON: {e}", file=sys.stderr)
                raise typer.Exit(1)
        
        # Write operation
        elif write:
            # Read existing data or create new
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except json.JSONDecodeError:
                    data = {}
                except UnicodeDecodeError as e:
                    print(f"Error: Unable to decode file '{file}': {e}", file=sys.stderr)
                    raise typer.Exit(1)
            else:
                data = {}
            
            # Parse value as JSON if possible
            try:
                parsed_value = json.loads(value)
            except json.JSONDecodeError:
                # If not valid JSON, treat as string
                parsed_value = value
            
            # Update the field
            try:
                # First try direct field update (for keys containing dots)
                if '.' not in field or field in data:
                    data[field] = parsed_value
                else:
                    # Navigate through nested fields using dot notation
                    keys = field.split('.')
                    current = data
                    
                    # Navigate to the parent of the target field
                    for key in keys[:-1]:
                        if key not in current:
                            current[key] = {}
                        elif not isinstance(current[key], dict):
                            print(f"Error: Cannot navigate through non-dict field '{key}'", file=sys.stderr)
                            raise typer.Exit(1)
                        current = current[key]
                    
                    # Set the final field
                    current[keys[-1]] = parsed_value
                
                # Write back to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    f.write('\n')
                
                print(f"Successfully updated field '{field}' in '{file}'")
                
            except Exception as e:
                print(f"Error updating field '{field}': {e}", file=sys.stderr)
                raise typer.Exit(1)
            
    except Exception as e:
        if not isinstance(e, typer.Exit):
            print(f"Error: {e}", file=sys.stderr)
            raise typer.Exit(1)
        raise