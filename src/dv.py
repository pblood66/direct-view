import click
import fnmatch
from pathlib import Path


def parse_ignore_file(filepath: Path) -> list[str]:
  patterns = []
  try:
    with open(filepath, "r", encoding="utf-8") as f:
      for line in f:
        line = line.rstrip("\n")
        if not line.strip() or line.strip().startswith("#"):
          continue
        patterns.append(line.rstrip("/").strip())
  except (OSError, UnicodeDecodeError) as e:
    raise click.ClickException(f"Could not read ignore file: {e}")
  return patterns


def is_ignored(entry: Path, root: Path, patterns: list[str]) -> bool:
  try:
    rel = entry.relative_to(root)
  except ValueError:
    return False

  rel_str = rel.as_posix()
  name = entry.name

  for pattern in patterns:
    if fnmatch.fnmatch(name, pattern):
      return True
    if fnmatch.fnmatch(rel_str, pattern):
      return True
    if any(fnmatch.fnmatch(part, pattern) for part in rel.parts):
      return True

  return False


def get_tree_lines(path: Path, root: Path, recursive: bool, exclude: set, patterns: list[str], prefix: str = "") -> list[str]:
  lines = []

  try:
    entries = sorted(path.iterdir(), key=lambda e: (e.is_file(), e.name.lower()))
  except PermissionError:
    lines.append(f"{prefix}[Permission Denied]")
    return lines

  entries = [e for e in entries if e.name not in exclude and not is_ignored(e, root, patterns)]

  for i, entry in enumerate(entries):
    is_last = i == len(entries) - 1
    connector = "└── " if is_last else "├── "
    extension = "/" if entry.is_dir() else ""
    lines.append(f"{prefix}{connector}{entry.name}{extension}")

    if entry.is_dir() and recursive:
      child_prefix = prefix + ("  " if is_last else "│  ")
      lines.extend(get_tree_lines(entry, root, recursive=True, exclude=exclude, patterns=patterns, prefix=child_prefix))

  return lines


def count_entries(path: Path, root: Path, recursive: bool, exclude: set, patterns: list[str]):
  file_count = 0
  dir_count = 0

  try:
    entries = [e for e in path.iterdir() if e.name not in exclude and not is_ignored(e, root, patterns)]
  except PermissionError:
    return 0, 0

  for entry in entries:
    if entry.is_file():
      file_count += 1
    elif entry.is_dir():
      dir_count += 1
      if recursive:
        sub_files, sub_dirs = count_entries(entry, root, recursive=True, exclude=exclude, patterns=patterns)
        file_count += sub_files
        dir_count += sub_dirs

  return file_count, dir_count


@click.command()
@click.argument("directory", default=None, required=False)
@click.option("-r", "--recursive", is_flag=True, default=False, help="Recursively show all files in all subdirectories.")
@click.option("-e", "--exclude", multiple=True, metavar="NAME", help="File or folder names to exclude")
@click.option("-i", "--ignore-file", type=click.Path(exists=True, dir_okay=False), default=None, metavar="FILE", help="Path to a .gitignore-style file with patterns to exclude.")
def cli(directory, recursive, exclude, ignore_file):
  root = Path(directory).resolve() if directory else Path.cwd()

  if not root.exists() or not root.is_dir():
    raise click.BadParameter(f"'{root}' is not a valid directory.")

  click.echo()
  click.secho(f"  {root}", fg="cyan", bold=True)
  click.echo()

  exclude_set = set(exclude)
  patterns = []

  if ignore_file:
    patterns = parse_ignore_file(Path(ignore_file))
    click.secho(f"  Ignore file: {ignore_file} ({len(patterns)} pattern(s))", fg="red", dim=True)

  if exclude_set:
    excluded_display = ", ".join(sorted(exclude_set))
    click.secho(f"  Excluding: {excluded_display}", fg="red", dim=True)

  if ignore_file or exclude_set:
    click.echo()

  lines = get_tree_lines(root, root, recursive=recursive, exclude=exclude_set, patterns=patterns)

  if not lines:
    click.secho("  (empty directory)", dim=True)
  else:
    for line in lines:
      if line.rstrip().endswith("/"):
        click.secho(f"  {line}", fg="blue", bold=True)
      else:
        click.echo(f"  {line}")

  click.echo()

  file_count, dir_count = count_entries(root, root, recursive=recursive, exclude=exclude_set, patterns=patterns)
  mode = "recursive" if recursive else "flat"
  click.secho(f"  {dir_count} folder(s), {file_count} file(s) [{mode}]", fg="green", dim=True)
  click.echo()


if __name__ == "__main__":
  cli()