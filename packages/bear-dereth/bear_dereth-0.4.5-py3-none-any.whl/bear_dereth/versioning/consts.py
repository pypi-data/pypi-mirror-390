"""Constants and types for versioning."""

from typing import Literal

from .classes import VersionParts

type BumpType = Literal["major", "minor", "patch"]


VALID_BUMP_TYPES: list[str] = VersionParts.choices()
ALL_PARTS: int = VersionParts.parts()
