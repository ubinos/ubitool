"""JSON command implementation for ubitool."""

import json
import sys
from pathlib import Path
from typing import Optional

import typer
import jmespath
import re


def _update_with_jmespath(data, jmespath_query, new_value):
    """Update JSON data using JMESPath query to locate the target."""
    try:
        # Handle pipe operations like "configurations[?name=='target app debug'].cwd | [0]"
        if "|" in jmespath_query:
            # Split on the pipe and process
            parts = jmespath_query.split("|")
            if len(parts) == 2:
                base_query = parts[0].strip()
                pipe_operation = parts[1].strip()
                
                # Execute the base query to find matching items
                matches = jmespath.search(base_query, data)
                if matches and len(matches) > 0:
                    # Handle [0] pipe operation to get first item
                    if pipe_operation == "[0]":
                        # We need to find the actual location in the original data structure
                        # For configurations[?name=='target app debug'].cwd | [0]
                        # We need to find the configuration with name 'target app debug' and update its cwd
                        if base_query.startswith("configurations[?") and ".cwd" in base_query:
                            # Extract the filter condition
                            match = re.search(r"configurations\[\?(.+?)\]\.(.+)", base_query)
                            if match:
                                condition = match.group(1)
                                field = match.group(2)
                                
                                # Parse condition like "name=='target app debug'"
                                if "==" in condition:
                                    cond_parts = condition.split("==")
                                    if len(cond_parts) == 2:
                                        key_name = cond_parts[0].strip()
                                        target_value = cond_parts[1].strip().strip("'\"")
                                        
                                        # Find and update the matching configuration
                                        if "configurations" in data and isinstance(data["configurations"], list):
                                            for config in data["configurations"]:
                                                if isinstance(config, dict) and config.get(key_name) == target_value:
                                                    config[field] = new_value
                                                    return True
                return False
        else:
            # Simple JMESPath query without pipe
            return False
    except Exception:
        return False


def _update_simple_array_access(data, key_path, new_value):
    """Update JSON data using simple array access like 'configurations[1].cwd'."""
    try:
        # Parse patterns like "configurations[1].cwd"
        parts = key_path.split(".")
        current = data
        
        for i, part in enumerate(parts):
            if "[" in part and "]" in part:
                # Handle array access
                array_name = part[:part.index("[")]
                index_str = part[part.index("[")+1:part.index("]")]
                
                try:
                    index = int(index_str)
                except ValueError:
                    return False
                
                if array_name not in current or not isinstance(current[array_name], list):
                    return False
                
                if index < 0 or index >= len(current[array_name]):
                    return False
                
                if i == len(parts) - 1:
                    # This is the last part, we're accessing an array element directly
                    current[array_name][index] = new_value
                    return True
                else:
                    # Navigate to the array element
                    current = current[array_name][index]
            else:
                # Handle regular object key
                if i == len(parts) - 1:
                    # Final key, set the value
                    current[part] = new_value
                    return True
                else:
                    # Navigate to the next level
                    if part not in current or not isinstance(current[part], dict):
                        return False
                    current = current[part]
        
        return False
    except Exception:
        return False


def json_command(
    file: str,
    read: bool = typer.Option(False, "-r", "--read", help="Print the value of a specified key of the json target file (requires --key)"),
    write: bool = typer.Option(False, "-w", "--write", help="Write a specified value to a specified key of the json target file (requires --key and --value)"),
    key: Optional[str] = typer.Option(None, "-k", "--key", help="Specify a key"),
    value: Optional[str] = typer.Option(None, "-v", "--value", help="Specify a value")
):
    """Print or write json file.
    
    Args:
        file: Path to the json target file
        read: Print the value of a specified key
        write: Write a value to a specified key
        key: Key to read or write (using JMESPath syntax)
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
            
        if read and not key:
            print("Error: --read requires --key", file=sys.stderr)
            raise typer.Exit(1)
            
        if write and (not key or value is None):
            print("Error: --write requires both --key and --value", file=sys.stderr)
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
                # Handle root access specially
                if key == ".":
                    result = data
                else:
                    # Use JMESPath to query the data
                    # Remove leading "." if present for JMESPath compatibility
                    clean_key = key.lstrip(".")
                    
                    # Use JMESPath directly - it can handle complex queries
                    result = jmespath.search(clean_key, data)
                    
                    if result is None:
                        # Check if the path exists in the data
                        print(f"Error: Key '{key}' not found in JSON", file=sys.stderr)
                        raise typer.Exit(1)
                
                # Pretty print the result
                if isinstance(result, (dict, list)):
                    print(json.dumps(result, indent=4, ensure_ascii=False))
                else:
                    print(json.dumps(result, ensure_ascii=False))
            except jmespath.exceptions.JMESPathError as e:
                print(f"Error: Invalid JMESPath expression '{key}': {e}", file=sys.stderr)
                raise typer.Exit(1)
        
        # Write operation
        elif write:
            # For write operations, we need to handle nested key creation differently
            # JMESPath is primarily for reading, so we'll use a custom approach for writing
            
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
            
            # Update the key using custom logic for writing
            try:
                # Handle simple root-level access with "."
                if key == ".":
                    if isinstance(parsed_value, dict):
                        data = parsed_value
                    else:
                        print(f"Error: Cannot set root to non-object value", file=sys.stderr)
                        raise typer.Exit(1)
                else:
                    # Remove leading "." if present for JMESPath compatibility
                    clean_key = key.lstrip(".")
                    
                    # Check if this is a complex JMESPath query that needs special handling
                    if ("[?" in clean_key and "]" in clean_key) or ("|" in clean_key):
                        # This is a complex JMESPath query - we need to find the target and update it
                        success = _update_with_jmespath(data, clean_key, parsed_value)
                        if not success:
                            print(f"Error: Could not update using JMESPath query '{key}'", file=sys.stderr)
                            raise typer.Exit(1)
                    elif clean_key.startswith('"') and clean_key.endswith('"'):
                        # This is a quoted key with literal dots - use as single key
                        unquoted_key = clean_key[1:-1]  # Remove quotes
                        data[unquoted_key] = parsed_value
                    elif "." in clean_key and not ("[" in clean_key or "]" in clean_key):
                        # Split the key path and navigate/create nested structure (simple dot notation)
                        keys = clean_key.split(".")
                        current = data
                        
                        # Navigate to the parent of the target key
                        for k in keys[:-1]:
                            if k not in current:
                                current[k] = {}
                            elif not isinstance(current[k], dict):
                                print(f"Error: Cannot navigate through non-dict key '{k}'", file=sys.stderr)
                                raise typer.Exit(1)
                            current = current[k]
                        
                        # Set the final key
                        current[keys[-1]] = parsed_value
                    else:
                        # Simple key assignment or array access
                        if "[" in clean_key and "]" in clean_key:
                            # Handle simple array access like "configurations[1].cwd"
                            success = _update_simple_array_access(data, clean_key, parsed_value)
                            if not success:
                                print(f"Error: Could not update array access '{key}'", file=sys.stderr)
                                raise typer.Exit(1)
                        else:
                            data[clean_key] = parsed_value
                
                # Write back to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                    f.write('\n')
                
                print(f"Successfully updated key '{key}' in '{file}'")
                
            except Exception as e:
                print(f"Error updating key '{key}': {e}", file=sys.stderr)
                raise typer.Exit(1)
            
    except Exception as e:
        if not isinstance(e, typer.Exit):
            print(f"Error: {e}", file=sys.stderr)
            raise typer.Exit(1)
        raise