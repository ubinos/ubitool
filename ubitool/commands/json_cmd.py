"""JSON command implementation for ubitool."""

import json
import sys
from pathlib import Path
from typing import Optional

import typer
import jmespath
import json5
import re


def _normalize_jmespath_query(query):
    """Normalize JMESPath query by converting escaped quotes to regular quotes."""
    # Replace \" with ' in the query for JMESPath compatibility
    # This handles cases like name=="value" -> name='value'
    normalized = query.replace('\\"', "'")
    # Also handle cases where the input has literal \" characters
    normalized = normalized.replace('=="', "=='").replace('"', "'")
    return normalized


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
                        # Handle both configurations and tasks arrays
                        array_match = re.search(r"(\w+)\[\?(.+?)\]\.(.+)", base_query)
                        if array_match:
                            array_name = array_match.group(1)  # e.g., "configurations" or "tasks"
                            condition = array_match.group(2)   # e.g., "name=='target app debug'"
                            field_path = array_match.group(3)  # e.g., "cwd" or "options.cwd"
                            
                            # Parse condition like "name=='target app debug'" or "label==\"target app reset\""
                            if "==" in condition:
                                cond_parts = condition.split("==")
                                if len(cond_parts) == 2:
                                    key_name = cond_parts[0].strip()
                                    target_value = cond_parts[1].strip()
                                    
                                    # Handle escaped quotes
                                    if target_value.startswith('\\"') and target_value.endswith('\\"'):
                                        target_value = target_value[2:-2]  # Remove \" and \"
                                    elif target_value.startswith("'") and target_value.endswith("'"):
                                        target_value = target_value[1:-1]  # Remove ' and '
                                    elif target_value.startswith('"') and target_value.endswith('"'):
                                        target_value = target_value[1:-1]  # Remove " and "
                                    
                                    # Find and update the matching item in the array
                                    if array_name in data and isinstance(data[array_name], list):
                                        for item in data[array_name]:
                                            if isinstance(item, dict) and item.get(key_name) == target_value:
                                                # Handle nested field paths like "options.cwd"
                                                if "." in field_path:
                                                    field_parts = field_path.split(".")
                                                    current = item
                                                    # Navigate to the nested object
                                                    for part in field_parts[:-1]:
                                                        if part in current and isinstance(current[part], dict):
                                                            current = current[part]
                                                        else:
                                                            return False
                                                    # Set the final field
                                                    current[field_parts[-1]] = new_value
                                                    return True
                                                else:
                                                    # Simple field access
                                                    item[field_path] = new_value
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
    """Print or write JSON5 file (supports comments and relaxed syntax).
    
    Args:
        file: Path to the JSON5 target file
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
                    data = json5.load(f)
            except json5.JSON5DecodeError as e:
                print(f"Error: Invalid JSON5 in file '{file}': {e}", file=sys.stderr)
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
                    
                    # Try different key access approaches
                    result = None
                    
                    # Check for bracket notation for literal keys like ["key.with.dots"]
                    if clean_key.startswith('["') and clean_key.endswith('"]'):
                        # Extract the literal key from ["key"] format
                        literal_key = clean_key[2:-2]  # Remove [" and "]
                        if literal_key in data:
                            result = data[literal_key]
                    else:
                        # First try: direct JMESPath query (for complex queries and simple nested paths)
                        try:
                            # Normalize the query to handle escaped quotes
                            normalized_key = _normalize_jmespath_query(clean_key)
                            result = jmespath.search(normalized_key, data)
                        except:
                            result = None
                        
                        # Second try: if result is None and key contains dots, try as quoted literal key
                        if result is None and "." in clean_key and not ("[" in clean_key or "]" in clean_key or "|" in clean_key):
                            # This might be a literal key with dots, try as quoted key
                            quoted_key = f'"{clean_key}"'
                            try:
                                result = jmespath.search(quoted_key, data)
                            except:
                                result = None
                        
                        # Third try: direct dictionary access for literal keys
                        if result is None and clean_key in data:
                            result = data[clean_key]
                    
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
                        data = json5.load(f)
                except (json5.JSON5DecodeError, json.JSONDecodeError):
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
                    
                    # Check for bracket notation for literal keys like ["key.with.dots"]
                    if clean_key.startswith('["') and clean_key.endswith('"]'):
                        # Extract the literal key from ["key"] format
                        literal_key = clean_key[2:-2]  # Remove [" and "]
                        data[literal_key] = parsed_value
                    # Check if this is a complex JMESPath query that needs special handling
                    elif ("[?" in clean_key and "]" in clean_key) or ("|" in clean_key):
                        # This is a complex JMESPath query - we need to find the target and update it
                        normalized_key = _normalize_jmespath_query(clean_key)
                        success = _update_with_jmespath(data, normalized_key, parsed_value)
                        if not success:
                            print(f"Error: Could not update using JMESPath query '{key}'", file=sys.stderr)
                            raise typer.Exit(1)
                    elif clean_key.startswith('"') and clean_key.endswith('"'):
                        # This is a quoted key with literal dots - use as single key
                        unquoted_key = clean_key[1:-1]  # Remove quotes
                        data[unquoted_key] = parsed_value
                    elif "." in clean_key and not ("[" in clean_key or "]" in clean_key):
                        # Check if this is a literal key first
                        if clean_key in data:
                            # This is a literal key with dots in the name
                            data[clean_key] = parsed_value
                        else:
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