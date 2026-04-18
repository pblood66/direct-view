import click
from pathlib import Path


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


if __name__ == "__main__":
  cli()