# pep440check

[![PyPI - Version](https://img.shields.io/pypi/v/pep440check.svg)](https://pypi.org/project/pep440check)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pep440check.svg)
![Last Commit](https://img.shields.io/github/last-commit/heiwa4126/pep440check)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A utility to check if version strings in pyproject.toml's project.version are [PEP 440](https://peps.python.org/pep-0440/) compliant and suggest normalized forms if they are not.
Optionally, it can rewrite the file with the normalized version.

## Basic usage

```sh
pep440check [path] [-w] [-h]
```

- `path`: Path to pyproject.toml (defaults to current directory's pyproject.toml if omitted)
- `-w, --write`: Write normalized version back to file
- `-h, --help`: Show help message and exit

### Exit codes

- `0`: Version is already PEP 440 compliant (displays "OK")
- `1`: Version needs normalization or error occurred

### Output examples

**When version is already normalized:**

```
$ pep440check
Target: /path/to/pyproject.toml
OK: 0.0.1a1
```

**When version needs normalization:**

```
$ pep440check
Target: /path/to/pyproject.toml
Original version: 1.0.0-rc1
Suggested normalized version: 1.0.0rc1
```

**Writing normalized version:**

```
$ pep440check -w
Target: /path/to/pyproject.toml
Normalized version: 1.0.0-rc1 -> 1.0.0rc1
```

## Installation and Usage

```sh
uv add pep440check --dev
uv run pep440check [args]
```

or

```sh
uvx pep440check [args]
```

or

```sh
uv tool install pep440check
pep440check [args]
```

## Development

```sh
git clone https://github.com/heiwa4126/pep440check.git
cd pep440check
uv sync
```

Run tests:

```sh
uv run poe test
```

Run linter and formatter:

```sh
uv run poe check
```

Type checking:

```sh
uv run poe mypy
```

Build package:

```sh
uv run poe build
```
