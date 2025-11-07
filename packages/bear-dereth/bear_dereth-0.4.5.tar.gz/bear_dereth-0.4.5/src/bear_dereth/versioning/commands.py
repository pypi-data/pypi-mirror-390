"""A set of functions related to versioning."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from bear_dereth.cli import ExitCode

from .classes import Version
from .consts import ALL_PARTS, VALID_BUMP_TYPES, BumpType


def get_version(package_name: str) -> str:
    """Get the version of the specified package.

    Args:
        package_name: The name of the package to get the version for.

    Returns:
        A Version instance representing the current version of the package.

    Raises:
        PackageNotFoundError: If the package is not found.
    """
    version: str | None = cli_get_version(package_name)
    if version is not None:
        return version
    raise ValueError("Not able to find package name.")


def cli_get_version(pkg_name: str) -> str | None:
    """Get the version of the current package.

    Returns:
        The version of the package.
    """
    try:
        current_version: str = version(pkg_name)
    except PackageNotFoundError:
        print(f"Package '{pkg_name}' not found.")
        return None
    return current_version


def cli_bump(b: BumpType, v: str | tuple[int, int, int]) -> ExitCode:  # pragma: no cover
    """Bump the version of the current package.

    Args:
        b: The type of bump ("major", "minor", or "patch").
        p: The name of the package.
        v: The current version string or tuple of version parts.

    Returns:
        An ExitCode indicating success or failure.
    """
    if b not in VALID_BUMP_TYPES:
        print(f"Invalid argument '{b}'. Use one of: {', '.join(VALID_BUMP_TYPES)}.")
        return ExitCode.FAILURE
    if not isinstance(v, tuple):
        raise TypeError("Version must be a tuple of integers.")
    try:
        parts: list[int] = list(v)
        version: Version = Version(
            major=parts[0],
            minor=parts[1] if ALL_PARTS > 1 else 0,
            patch=parts[2] if ALL_PARTS > 2 else 0,  # noqa: PLR2004
        )
        new_version: Version = version.new_version(b)
        print(str(new_version))
        return ExitCode.SUCCESS
    except ValueError:
        print(f"Invalid version tuple: {v}")
        return ExitCode.FAILURE
