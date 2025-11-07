import sys
from pathlib import Path

from pep440check.pep440check import (
    check_version,
    load_pyproject_toml,
    save_pyproject_toml,
)


def main() -> None:
    """CLI main"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Check and normalize PEP 440 version strings"
    )
    parser.add_argument(
        "path", nargs="?", default="pyproject.toml", help="Path to pyproject.toml"
    )
    parser.add_argument(
        "-w",
        "--write",
        action="store_true",
        help="Write normalized version back to file",
    )

    args = parser.parse_args()

    toml_path = Path(args.path).resolve()
    print(f"Target: {toml_path}")

    if not toml_path.exists():
        print(f"Error: {toml_path} not found", file=sys.stderr)
        sys.exit(1)

    try:
        data = load_pyproject_toml(toml_path)
        version_str = data["project"]["version"]
    except (KeyError, Exception) as e:
        print(f"Error: Failed to read pyproject.toml: {e}", file=sys.stderr)
        sys.exit(1)

    is_valid, normalized = check_version(version_str)

    if not is_valid:
        print(
            f"Error: Version '{version_str}' is not PEP 440 compliant",
            file=sys.stderr,
        )
        sys.exit(1)

    if version_str == normalized:
        print(f"OK: {version_str}")
        sys.exit(0)

    if args.write:
        save_pyproject_toml(toml_path, data, normalized)
        print(f"Normalized version: {version_str} -> {normalized}")
    else:
        print(f"Original version: {version_str}")
        print(f"Suggested normalized version: {normalized}")

    sys.exit(1)


if __name__ == "__main__":
    main()
