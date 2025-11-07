"""Settings path derivation utilities."""

from pathlib import Path


class SettingsHelper:
    """Helper class for settings file operations."""

    def __init__(
        self,
        name: str,
        file: str | None,
        path: Path | str | None = None,
        ext: str | None = None,
        *,
        default_exemptions: tuple[str, ...] | frozenset[str] | None = None,
        default_ext: str = "json",
    ) -> None:
        """Initialize SettingsHelper.

        Args:
            name: App name (used as default file name and for default directory)
            file: Optional specific file name (overrides name for filename)
            path: Optional path - can be:
                - Full path to .json file (returns as-is)
                - Directory path (file will be created inside)
                - None (uses default settings directory)
            ext: File extension (default: "json")
            default_exemptions: Optional set of extensions that should use default_ext instead
            default_ext: Default extension to use if ext is in default_exemptions
            mkdir: Whether to create missing directories
        """
        self.name: str = name
        self._file_name: str | None = file
        self._path: Path | str | None = path
        self._ext: str = ext or default_ext
        self.default_exemptions: tuple[str, ...] | frozenset[str] = default_exemptions or frozenset()
        self.default_ext: str = default_ext

    @property
    def file_name(self) -> str:
        """Get the effective file name."""
        if self._file_name is not None:
            return Path(self._file_name).stem
        return self.name

    @property
    def path(self) -> Path:
        """Get the full path to the settings file."""
        from .dir_manager import get_settings_path  # noqa: PLC0415

        if self._path is not None:
            path_value: Path = Path(self._path)
            if path_value.is_file():
                return path_value.parent
            return path_value
        return get_settings_path(self.name)

    @property
    def ext(self) -> str:
        """Get the effective file extension."""
        if self._ext in self.default_exemptions:
            return self.default_ext
        return self._ext

    @property
    def full_path(self) -> Path:
        """Get the full path to the settings file."""
        return self.path / f"{self.file_name}.{self.ext}"


def derive_settings_path(
    name: str,
    file: str | None = None,
    path: Path | str | None = None,
    ext: str | None = None,
    *,
    default_exemptions: tuple[str, ...] | frozenset[str] | None = None,
    default_ext: str = "json",
) -> Path:
    """Get the path to the settings file based on app name, optional file name, and optional path.

    Args:
        name: App name (used as default file name and for default directory)
        file: Optional specific file name (overrides name for filename)
        path: Optional path - can be:
            - Full path to file (returns as-is)
            - Directory path (file will be created inside)
            - None (uses default settings directory)
        ext: File extension (default: "json")
        default_exemptions: Optional set of extensions that should use default_ext instead
        default_ext: Default extension to use if ext is in default_exemptions

    Returns:
        Path: Full path to the settings file
    """
    return SettingsHelper(
        name,
        file,
        path,
        ext,
        default_exemptions=default_exemptions,
        default_ext=default_ext,
    ).full_path
