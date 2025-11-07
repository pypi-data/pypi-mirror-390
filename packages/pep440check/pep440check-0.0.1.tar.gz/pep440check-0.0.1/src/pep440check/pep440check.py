import tomllib
from pathlib import Path
from packaging.version import InvalidVersion, Version


def check_version(version_str: str) -> tuple[bool, str]:
    """Check if a version string is PEP 440 compliant and return normalized form.

    Args:
        version_str: Version string to check and normalize

    Returns:
        Tuple of (is_valid, normalized_version):
        - is_valid: True if the version is PEP 440 compliant, False otherwise
        - normalized_version: Normalized version string if valid, original string if invalid
    """
    try:
        version = Version(version_str)
        return True, str(version)
    except InvalidVersion:
        return False, version_str


def load_pyproject_toml(path: Path) -> dict:
    """Load and parse a pyproject.toml file.

    Args:
        path: Path to the pyproject.toml file

    Returns:
        Dictionary containing the parsed TOML data

    Raises:
        TOMLDecodeError: If the file contains invalid TOML
        FileNotFoundError: If the file does not exist
    """
    with open(path, "rb") as f:
        return tomllib.load(f)


def save_pyproject_toml(path: Path, data: dict, normalized_version: str) -> None:
    """Write normalized version back to pyproject.toml file.

    This function preserves the original file format and only updates the version line.

    Args:
        path: Path to the pyproject.toml file
        data: Parsed TOML data (unused but kept for consistency)
        normalized_version: The normalized version string to write

    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If the file cannot be written
    """
    lines = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("version = "):
                lines.append(f'version = "{normalized_version}"\n')
            else:
                lines.append(line)

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)
