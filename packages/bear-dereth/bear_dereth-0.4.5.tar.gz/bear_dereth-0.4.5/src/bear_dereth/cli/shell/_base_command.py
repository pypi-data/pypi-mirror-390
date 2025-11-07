from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Self

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from subprocess import CompletedProcess


def get_default_shell() -> str:
    """Get the default shell for the current platform"""
    from bear_dereth.cli.shells import DEFAULT_SHELL  # noqa: PLC0415
    from bear_dereth.system_bools import get_shell  # noqa: PLC0415

    return get_shell() or DEFAULT_SHELL


class ShellConfig(BaseModel):
    """Configuration for shell commands"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    shell: str = Field(default_factory=get_default_shell)
    cwd: Path = Path.cwd()
    env: dict[str, str] = Field(default_factory=dict)
    logger: Any | None = Field(default=None)
    verbose: bool = False
    use_shell: bool = True


class BaseShellCommand[T: str]:
    """Base class for typed shell commands compatible with session systems"""

    command_name: ClassVar[str] = ""

    def __init__(self, *args, **kwargs) -> None:
        self.sub_command: str = kwargs.pop("sub_command", "")
        self.args: tuple[str, ...] = args
        self.kwargs: dict[str, Any] = kwargs
        self.suffix = self.kwargs.get("suffix", "")
        self.result: CompletedProcess[str] | None = None
        self.shell_config: ShellConfig = self.kwargs.pop("shell_config", ShellConfig(**self.kwargs))

    def __str__(self) -> str:
        """String representation of the command"""
        return self.cmd

    def value(self, v: str) -> Self:
        """Add value to the export command"""
        self.suffix: str = v
        return self

    @classmethod
    def adhoc(cls, name: str, *args, **kwargs) -> BaseShellCommand:
        """Create an ad-hoc command class for a specific command

        Args:
            name (str): The name of the command to create

        Returns:
            BaseShellCommand: An instance of the ad-hoc command class.
        """
        return type(
            f"AdHoc{name.title()}Command",
            (cls,),
            {"command_name": name},
        )(*args, **kwargs)

    @classmethod
    def sub(cls, s: str, *args, **kwargs) -> Self:
        """Set a sub-command for the shell command"""
        return cls(s, *args, **kwargs)

    @property
    def cmd(self) -> str:
        """Return the full command as a string"""
        cmd_parts: list[str] = [part for part in [self.command_name, self.sub_command, *self.args] if part]
        joined: str = " ".join(cmd_parts).strip()
        if self.suffix:
            return f"{joined} {self.suffix}"
        return joined

    def do(self, **kwargs) -> Self:
        """Run the command using subprocess"""
        from ._base_shell import shell_session  # noqa: PLC0415

        shell_config: dict[str, Any] = self.shell_config.model_dump(exclude_none=True)
        if kwargs:
            shell_config.update(kwargs)
        with shell_session(**shell_config) as session:
            result: CompletedProcess[str] = session.add(self.cmd).run()
        if result is not None:
            self.result = result
        return self

    def get_result(self) -> CompletedProcess[str]:
        """Get the result of the command execution"""
        if self.result is None:
            self.do()
        if self.result is None:
            raise RuntimeError("Command execution failed for some reason.")
        return self.result

    def get(self) -> str:
        """Get the result of the command execution"""
        if self.result is None:
            self.do()
        if self.result is None:
            raise RuntimeError("Command execution failed for some reason.")
        return str(self.result.stdout).strip()
