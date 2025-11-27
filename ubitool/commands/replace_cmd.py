"""Replace command implementation for ubitool."""

from pathlib import Path
import sys
import typer


def replace_command(
    file: str = typer.Argument(..., help="Path to the target file."),
    search_text: str = typer.Argument(..., help="Text to search for."),
    replace_text: str = typer.Argument(..., help="Text to replace with."),
    replace_all: bool = typer.Option(False, "-a", "--all", help="Replace all occurrences. If not set, only the first occurrence is replaced.")
):
    """Replace text in a file."""

    target_path = Path(file)

    if not search_text:
        print("Error: SEARCH_TEXT must not be empty.", file=sys.stderr)
        raise typer.Exit(1)

    if not target_path.exists():
        print(f"Error: File '{file}' not found.", file=sys.stderr)
        raise typer.Exit(1)

    if not target_path.is_file():
        print(f"Error: '{file}' is not a file.", file=sys.stderr)
        raise typer.Exit(1)

    try:
        original_content = target_path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        print(f"Error reading file '{file}': {exc}", file=sys.stderr)
        raise typer.Exit(1)

    occurrences = original_content.count(search_text)
    if occurrences == 0:
        print(f"replace: '{search_text}' not found in '{file}'.")
        return

    if replace_all:
        updated_content = original_content.replace(search_text, replace_text)
        replaced_count = occurrences
    else:
        updated_content = original_content.replace(search_text, replace_text, 1)
        replaced_count = 1

    try:
        target_path.write_text(updated_content, encoding="utf-8")
    except Exception as exc:
        print(f"Error writing file '{file}': {exc}", file=sys.stderr)
        raise typer.Exit(1)

    occurrence_label = "occurrence" if replaced_count == 1 else "occurrences"
    print(f"Replaced {replaced_count} {occurrence_label} in '{file}'.")
