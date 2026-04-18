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

    if entry.is_dir() and recursive:
      child_prefix = prefix + ("  " if is_last else "│  ")
      lines.extend(get_tree_lines(entry, recursive=True, exclude=exclude, prefix=child_prefix))

  return lines

def count_entries(path: Path, recursive: bool, exclude: set):
  file_count = 0
  dir_count = 0

  try:
    entries = [e for e in path.iterdir() if e.name not in exclude]
  except PermissionError:
    return 0, 0

  for entry in entries:
    if entry.is_file():
      file_count += 1
    elif entry.is_dir():
      dir_count += 1
      if recursive:
        sub_files, sub_dirs = count_entries(entry, recursive=True, exclude=exclude)
        file_count += sub_files
        dir_count += sub_dirs

  return file_count, dir_count

@click.command()
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option("-r", "--recursive", is_flag=True, default=False, help="Recursively show all files in all subdirectories.")
@click.option("-e", "--exclude", multiple=True, metavar="FOLDER",  help="Folder or file names to exclude")
def cli(directory, recursive, exclude):
  root = Path(directory).resolve() if directory else Path.cwd()

  if not root.exists() or not root.is_dir():
    raise click.BadParameter(f"'{root}' is not a valid directory.")

  click.echo()
  click.secho(f"  {root}", fg="cyan", bold=True)
  click.echo()

  exclude_set = set(exclude)
  if exclude_set:
    excluded_display = ", ".join(sorted(exclude_set))
    click.secho(f"  Excluding: {excluded_display}", fg="yellow", dim=True)
    click.echo()

  lines = get_tree_lines(root, recursive=recursive, exclude=exclude_set)

  if not lines:
      click.secho("  (empty directory)", dim=True)
  else:
    for line in lines:
      if line.rstrip().endswith("/"):
        click.secho(f"  {line}", fg="blue", bold=True)
      else:
        click.echo(f"  {line}")

  click.echo()

  file_count, dir_count = count_entries(root, recursive=recursive, exclude=exclude_set)
  mode = "recursive" if recursive else "flat"
  click.secho(f"  {dir_count} folder(s), {file_count} file(s) [{mode}]", dim=True)
  click.echo()

if __name__ == "__main__":
  cli()