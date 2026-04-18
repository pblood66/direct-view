# dv

A CLI tool for visualizing the file layout of a directory.

## Installation

```bash
pip install -e .
```

## Usage

```bash
dv                        # show flat layout of current directory
dv /path/to/project       # show flat layout of a specific directory
dv . -r                   # show full recursive tree
dv . -r -e .venv -e .git  # exclude specific folders
dv . -r -i .gitignore     # use a .gitignore file to exclude patterns
```

## Options

| Option | Description |
|---|---|
| `-r, --recursive` | Recursively show all files in all subdirectories |
| `-e, --exclude NAME` | Exclude a file or folder by name (repeatable) |
| `-i, --ignore-file FILE` | Path to a .gitignore-style file with patterns to exclude |

## Example Output

```
  C:\Users\user\Documents\projects\my-project

  Excluding: .venv

  ├── .git/
  ├── src/
  │  └── main.py
  └── README.md

  1 folder(s), 2 file(s) [recursive]
```