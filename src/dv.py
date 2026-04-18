import click
from pathlib import Path

import click
import os
from pathlib import Path


def get_tree_lines(path: Path, recursive: bool, exclude: tuple, prefix: str = "") -> list[str]:
    lines = []

    try:
        entries = sorted(path.iterdir(), key=lambda e: (e.is_file(), e.name.lower()))
    except PermissionError:
        lines.append(f"{prefix}[Permission Denied]")
        return lines

    entries = [e for e in entries if e.name not in exclude]

    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        extension = "/" if entry.is_dir() else ""
        lines.append(f"{prefix}{connector}{entry.name}{extension}")

        if entry.is_dir():
            child_prefix = prefix + ("    " if is_last else "│   ")
            if recursive:
                lines.extend(get_tree_lines(entry, recursive=True, exclude=exclude, prefix=child_prefix))
            else:
                try:
                    sub_entries = sorted(entry.iterdir(), key=lambda e: (e.is_file(), e.name.lower()))
                    sub_entries = [e for e in sub_entries if e.name not in exclude]
                    for j, sub_entry in enumerate(sub_entries):
                        sub_is_last = j == len(sub_entries) - 1
                        sub_connector = "└── " if sub_is_last else "├── "
                        sub_ext = "/" if sub_entry.is_dir() else ""
                        lines.append(f"{child_prefix}{sub_connector}{sub_entry.name}{sub_ext}")
                except PermissionError:
                    lines.append(f"{child_prefix}[Permission Denied]")

    return lines

@click.command()
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option("-r", "--recursive", is_flag=True, default=False, help="Recursively show all files in all subdirectories.")
@click.option("-e", "--exclude", multiple=True, metavar="FOLDER",  help="Folder or file names to exclude")
def cli(directory, recursive, exclude):
  root = Path(directory)
  click.echo()
  click.secho(f"  {root.resolve()}", fg="cyan", bold=True)
  click.echo()

  exclude_set = set(exclude)
  if exclude_set: 
    excluded_display = ", ".join(sorted(exclude_set))
    click.secho(f"  Excluding: {excluded_display}", fg="red", dim=True)
    click.echo()
    
    lines = get_tree_lines(root, recursive=recursive, exclude=exclude_set)


if __name__ == "__main__":
  cli()