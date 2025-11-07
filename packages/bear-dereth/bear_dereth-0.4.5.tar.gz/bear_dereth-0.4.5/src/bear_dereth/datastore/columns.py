"""A module defining the Columns model for representing table columns."""

from __future__ import annotations

from contextlib import suppress
import re
from typing import Any

from pydantic import Field, field_validator, model_validator

from bear_dereth.models.frozen_models import FrozenDict, freeze
from bear_dereth.models.general import ExtraIgnoreModel

INVALID_NAME_PREFIXES: list[str] = ["xml"]


class Columns[T](ExtraIgnoreModel):
    """A model to represent columns in a table."""

    name: str = ""
    type: str = Field(default=type[T].__name__ or "str")
    default: Any = None
    nullable: bool = False
    primary_key: bool | None = None
    autoincrement: bool | None = None

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: Any) -> str:
        """Validate column name format."""
        if not isinstance(v, str):
            raise TypeError(f"Column name must be a string, got {type(v).__name__}.")

        if not v or not v.strip():
            raise ValueError("Column name cannot be empty or whitespace.")

        if not v[0].isalpha() and v[0] != "_":
            raise ValueError(f"Column name must start with a letter or underscore, not '{v[0]}'.")

        if " " in v:
            raise ValueError("Column name cannot contain spaces. Use underscores instead.")

        for prefix in INVALID_NAME_PREFIXES:
            if v.lower().startswith(prefix):
                raise ValueError(
                    f"Column name cannot start with '{prefix}' (case insensitive) due to format restrictions."
                )

        return v

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, v: Any) -> str:
        """Ensure the type is stored as a string."""
        if isinstance(v, type):
            return v.__name__
        if isinstance(v, str):
            with suppress(Exception):
                v = re.sub(r"^Columns\[(.+)\]$", r"\1", v)
            return v
        raise TypeError("Type must be a string or a type.")

    @model_validator(mode="after")
    def validate_column_constraints(self) -> Columns:
        """Validate column constraints."""
        if self.primary_key is True and self.nullable is True:
            raise ValueError(f"Primary key column '{self.name}' cannot be nullable.")

        if self.autoincrement is True:
            if self.primary_key is not True:
                raise ValueError(
                    f"Autoincrement can only be set on primary key columns, but column '{self.name}' is not a primary key."
                )
            if not self.is_int:
                raise ValueError(
                    f"Autoincrement can only be set on integer columns, but column '{self.name}' has type '{self.type}'."
                )

        return self

    @property
    def is_int(self) -> bool:
        """Check if the column type is integer."""
        return self.type.lower() in {"int", "integer"}

    def __hash__(self) -> int:
        """Hash the column based on its attributes."""
        return hash((self.name, self.type, self.nullable, self.primary_key))

    def frozen_dump(self) -> FrozenDict:
        """Return a frozen representation of the column."""
        return freeze(self.model_dump(exclude_none=True))

    def render(self) -> dict[str, Any]:
        """Render the column as a dictionary."""
        return self.model_dump(exclude_none=True)

    def items(self) -> list[tuple[str, Any]]:
        """Return items for the column."""
        return list(self.render().items())


NullColumn: Columns[None] = Columns(name="NULL", type="null", nullable=True, default=None)
